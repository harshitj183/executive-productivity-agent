"""
Main Agent — Executive Productivity Agent for Arjun Malhotra.
Uses Groq function-calling with a tight token budget (7000 ITPM on free tier).
"""

import json
import logging
import os
from typing import Generator

from groq import Groq

from app.agents.tools import TOOL_DEFINITIONS, execute_tool
from app.data.source_data import get_all_sources_as_text

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_TOOL_ITERATIONS = 6

# ── Kept under 400 tokens ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Executive Productivity Agent for Arjun Malhotra (VP Sales, Veridian Corp).
Week: Mon 21 Sep – Fri 25 Sep 2026. Today = Monday 21 Sep 2026.

RULES:
- Never invent facts. If ownership is unclear, flag it — never assume.
- Cite source for every item (meeting / email thread name / voice note date).
- Classify: MY_ACTION (Arjun does it) | WAITING_ON_OTHERS | AMBIGUOUS (flag these).
- When same commitment appears in multiple sources with conflicting dates: surface the most recent version only, note the shift.
- Use tools to look up data. Be concise — Arjun is busy.

BRIEF FORMAT:
## My Actions  (overdue → today → this week)
## Waiting on Others
## Flagged / Needs Attention"""

# ── Under 120 tokens ─────────────────────────────────────────────────────────
BRIEF_GENERATION_PROMPT = """Generate Arjun's daily brief for week of 21–25 Sep 2026.
Use tools to: find all commitments across emails/transcript/voice notes, check deadlines, track date shifts (e.g. vendor list moved Mon→Tue→Wed), flag Mumbai lease as AMBIGUOUS.
Cite source + deadline for every item."""


class MainAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.conversation_history: list[dict] = []
        self.source_context = get_all_sources_as_text()
        self.call_count = 0
        self._initialized = False

    def reset_conversation(self):
        self.conversation_history = []
        self._initialized = False

    def _build_messages(self, user_message: str) -> list[dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if not self._initialized:
            # First chat call: inject source data once
            messages.append({
                "role": "user",
                "content": (
                    f"SOURCE DATA:\n{self.source_context}\n---\n{user_message}"
                )
            })
            self._initialized = True
        else:
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": user_message})
        return messages

    def generate_brief(self) -> Generator[dict, None, None]:
        yield {"type": "log", "step": "init", "message": "Starting brief generation..."}

        # Brief generation: NO source context in the message — agent uses tools
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": BRIEF_GENERATION_PROMPT},
        ]
        self._initialized = True

        result = yield from self._run_agentic_loop(messages, log_prefix="Brief")
        if not result:
            result = ""

        self.conversation_history.append({"role": "user", "content": BRIEF_GENERATION_PROMPT})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def chat(self, user_message: str) -> Generator[dict, None, None]:
        yield {"type": "log", "step": "chat_start", "message": f"Processing: {user_message[:60]}..."}

        messages = self._build_messages(user_message)
        result = yield from self._run_agentic_loop(messages, log_prefix="Chat")
        if not result:
            result = ""

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def _run_agentic_loop(self, messages: list[dict], log_prefix: str = "") -> Generator[dict, None, str]:
        iteration = 0
        current_messages = list(messages)

        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1
            self.call_count += 1

            yield {
                "type": "log",
                "step": f"llm_call_{iteration}",
                "message": f"[{log_prefix}] LLM call #{self.call_count} (iter {iteration})"
            }

            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=current_messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.1,
                    max_tokens=1200,
                )
            except Exception as e:
                logger.error(f"Groq error: {e}")
                yield {"type": "error", "message": f"LLM call failed: {str(e)}"}
                return f"Error: {str(e)}"

            msg = response.choices[0].message

            if msg.tool_calls:
                current_messages.append(msg)
                for tc in msg.tool_calls:
                    tname = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}

                    yield {
                        "type": "tool_call",
                        "tool": tname,
                        "args": args,
                        "message": f"→ {tname}({json.dumps(args)})"
                    }

                    tres = execute_tool(tname, args)

                    yield {
                        "type": "tool_result",
                        "tool": tname,
                        "message": f"← {tname}: {len(tres)} chars"
                    }

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tres,
                    })
                continue

            final_text = msg.content or ""
            yield {
                "type": "log",
                "step": "complete",
                "message": f"[{log_prefix}] Done — {iteration} iter, {self.call_count} calls total"
            }
            return final_text

        # Max iterations hit — force a final answer
        yield {"type": "log", "step": "max_iter", "message": "Max iterations reached, finalizing..."}
        current_messages.append({"role": "user", "content": "Summarize your findings now."})
        self.call_count += 1
        resp = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=current_messages,
            temperature=0.1,
            max_tokens=1200,
        )
        return resp.choices[0].message.content or ""
