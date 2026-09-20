"""
Main Agent — Executive Productivity Agent for Arjun Malhotra.

Token budget (llama-3.1-8b-instant free tier):
  - 6000 TPM (tokens per minute)
  - 500K TPD (tokens per day)
  - 14400 RPD (requests per day)

Strategy: keep total context well under 4000 tokens per call.
  - system prompt  ~150 tokens
  - user message   ~100 tokens
  - tool defs      ~500 tokens
  - tool results   capped at 400 chars each (~100 tokens each)
  - max iterations  4 (fewer tool round-trips = smaller context)
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
MAX_TOOL_ITERATIONS = 4          # fewer iterations = smaller growing context
MAX_TOOL_RESULT_CHARS = 500      # cap each tool result to avoid context blowup
MAX_OUTPUT_TOKENS = 1500         # enough for a full brief

# ── System prompt (~150 tokens) ───────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Executive Productivity Agent for Arjun Malhotra (VP Sales, Veridian Corp).
Week: Mon 21 – Fri 25 Sep 2026. Today = Mon 21 Sep 2026.

RULES (follow strictly):
1. Never invent facts. If ownership is unclear, flag it — do NOT guess.
2. Every commitment must cite its source (meeting / email thread / voice note).
3. Classify each item: MY_ACTION | WAITING_ON_OTHERS | AMBIGUOUS.
4. For rescheduled items: show final/latest date only, note previous dates briefly.
5. Use tools to look up source data before answering.

OUTPUT FORMAT for the daily brief:
## My Actions  ← overdue first, then by deadline
## Waiting on Others
## Flagged / Needs Attention  ← unclear ownership, risks"""

# ── Brief prompt (~80 tokens) ─────────────────────────────────────────────────
BRIEF_GENERATION_PROMPT = """Generate Arjun's daily brief. Use tools to find ALL commitments from emails, meeting transcript, and voice notes. Check deadlines. Track shifted dates (vendor list: Mon→Tue→Wed). Flag Mumbai lease as AMBIGUOUS. Cite source + deadline per item."""


def _cap(text: str, limit: int = MAX_TOOL_RESULT_CHARS) -> str:
    """Truncate tool result to keep context size under control."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"…[+{len(text)-limit} chars truncated]"


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
        """Build messages for follow-up chat. Context injected once."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if not self._initialized:
            messages.append({
                "role": "user",
                "content": f"SOURCE DATA:\n{self.source_context}\n\n---\n{user_message}"
            })
            self._initialized = True
        else:
            # Keep history but prune to last 6 turns max (cost control)
            recent = self.conversation_history[-12:]
            messages.extend(recent)
            messages.append({"role": "user", "content": user_message})
        return messages

    def generate_brief(self) -> Generator[dict, None, None]:
        yield {"type": "log", "step": "init", "message": "Starting brief generation..."}

        # Brief: agent uses tools, no large context blob in the message
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": BRIEF_GENERATION_PROMPT},
        ]
        self._initialized = True

        result = yield from self._run_agentic_loop(messages, "Brief")
        if not result:
            result = ""

        self.conversation_history.append({"role": "user", "content": BRIEF_GENERATION_PROMPT})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def chat(self, user_message: str) -> Generator[dict, None, None]:
        yield {"type": "log", "step": "chat_start", "message": f"Processing: {user_message[:60]}..."}

        messages = self._build_messages(user_message)
        result = yield from self._run_agentic_loop(messages, "Chat")
        if not result:
            result = ""

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def _run_agentic_loop(
        self, messages: list[dict], log_prefix: str = ""
    ) -> Generator[dict, None, str]:
        """
        Core loop: LLM call → tool calls → repeat.
        Tool results are capped so the context never blows up.
        """
        iteration = 0
        current_messages = list(messages)

        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1
            self.call_count += 1

            yield {
                "type": "log",
                "step": f"llm_call_{iteration}",
                "message": f"[{log_prefix}] LLM call #{self.call_count} (iter {iteration}/{MAX_TOOL_ITERATIONS})"
            }

            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=current_messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.1,
                    max_tokens=MAX_OUTPUT_TOKENS,
                )
            except Exception as e:
                err = str(e)
                logger.error(f"Groq error: {err}")
                # Friendly 429 message
                if "429" in err or "rate_limit" in err.lower():
                    yield {
                        "type": "error",
                        "message": "Groq API rate limit hit. Please wait a minute and try again."
                    }
                else:
                    yield {"type": "error", "message": f"LLM call failed: {err}"}
                return ""

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

                    raw_result = execute_tool(tname, args)
                    # Cap result to keep context from growing
                    capped = _cap(raw_result)

                    yield {
                        "type": "tool_result",
                        "tool": tname,
                        "message": f"← {tname}: {len(raw_result)} chars"
                    }

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": capped,
                    })
                continue

            # No tool calls → final answer
            final_text = msg.content or ""
            yield {
                "type": "log",
                "step": "complete",
                "message": f"[{log_prefix}] Done — {iteration} iter, {self.call_count} total calls"
            }
            return final_text

        # Hit iteration cap → force final answer without tools
        yield {
            "type": "log",
            "step": "max_iter",
            "message": f"Max iterations reached. Generating final answer..."
        }
        current_messages.append({
            "role": "user",
            "content": "Based on everything gathered, produce the final answer now. Be concise."
        })
        self.call_count += 1
        try:
            resp = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=current_messages,
                temperature=0.1,
                max_tokens=MAX_OUTPUT_TOKENS,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Final answer error: {e}")
            return ""
