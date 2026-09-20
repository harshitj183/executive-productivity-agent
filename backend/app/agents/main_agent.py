"""
Main Agent — Executive Productivity Agent for Arjun Malhotra.

Architecture: Source data is embedded directly in the first user message.
Tools are available for targeted follow-up lookups but the core data
is always present — the agent cannot "not have" the data.

Token budget (gpt-oss-20b / qwen fallback):
  ~2000 tokens input per call, 1500 output max.
"""

import json
import logging
from typing import Generator

from groq import Groq

from app.agents.tools import TOOL_DEFINITIONS, execute_tool
from app.data.source_data import get_all_sources_as_text

logger = logging.getLogger(__name__)

# ── Model config ──────────────────────────────────────────────────────────────
PRIMARY_MODEL   = "openai/gpt-oss-120b"   # hardcoded — best reasoning, 131K ctx
FALLBACK_MODELS = ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

MAX_TOOL_ITERATIONS = 3
MAX_OUTPUT_TOKENS   = 8000   # gpt-oss models use internal thinking tokens, need headroom
TOOL_RESULT_CAP     = 600


# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Executive Productivity Agent for Arjun Malhotra (VP Sales, Veridian Corp).
Week: Mon 21 – Fri 25 Sep 2026. Today = Mon 21 Sep 2026.

RULES:
1. Only use facts from the SOURCE DATA provided. Never invent anything.
2. Cite source for every item (meeting / email thread / voice note date).
3. Classify: MY_ACTION | WAITING_ON_OTHERS | AMBIGUOUS.
4. Rescheduled items: show final date only + note history.
5. Mumbai lease = AMBIGUOUS (ownership not confirmed).

BRIEF FORMAT:
## My Actions  (overdue first, then by date)
## Waiting on Others
## Flagged / Needs Attention"""

BRIEF_PROMPT_TEMPLATE = """Here is all source data for Arjun's week:

{source_data}

---
Using ONLY the data above, generate the complete daily brief.
- List every commitment, classify it, cite source, include deadline.
- Track date shifts (vendor list changed Mon→Tue→Wed).
- Flag Mumbai lease as AMBIGUOUS.
- Do not invent anything not in the data."""


def _call_with_fallback(
    client: Groq,
    messages: list[dict],
    tools: list | None = None,
    max_tokens: int = MAX_OUTPUT_TOKENS,
) -> tuple[object | None, str]:
    """
    Try PRIMARY_MODEL then FALLBACK_MODELS.
    Returns (response, model_used) or (None, "") on all failures.
    """
    for model in [PRIMARY_MODEL] + FALLBACK_MODELS:
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        try:
            resp = client.chat.completions.create(**kwargs)
            return resp, model
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                logger.warning(f"{model} rate-limited, trying next")
                continue
            if "400" in err and "tool_use_failed" in err:
                # Model tried invalid tool — retry same model without tools
                try:
                    kwargs.pop("tools", None)
                    kwargs.pop("tool_choice", None)
                    resp = client.chat.completions.create(**kwargs)
                    return resp, model
                except Exception:
                    continue
            logger.error(f"Groq error on {model}: {e}")
            return None, ""
    return None, ""


def _cap(text: str) -> str:
    if len(text) <= TOOL_RESULT_CAP:
        return text
    return text[:TOOL_RESULT_CAP] + f"…[{len(text)-TOOL_RESULT_CAP} more chars]"


class MainAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.conversation_history: list[dict] = []
        self.source_context = get_all_sources_as_text()
        self.call_count = 0
        self._brief_done = False

    def reset_conversation(self):
        self.conversation_history = []
        self._brief_done = False

    def generate_brief(self) -> Generator[dict, None, None]:
        """Generate the daily brief with source data embedded directly."""
        yield {"type": "log", "step": "init", "message": "Reading source data..."}

        # Embed source data directly — agent always has it
        brief_prompt = BRIEF_PROMPT_TEMPLATE.format(source_data=self.source_context)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": brief_prompt},
        ]

        result = yield from self._agentic_loop(messages, "Brief")
        if not result:
            result = "Could not generate brief — please try again."

        self._brief_done = True
        self.conversation_history.append({"role": "user",      "content": "Generate my daily brief."})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def chat(self, user_message: str) -> Generator[dict, None, None]:
        """Follow-up Q&A. Source data embedded on first chat call."""
        yield {"type": "log", "step": "chat", "message": f"Processing: {user_message[:60]}..."}

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if not self._brief_done:
            # First interaction without brief — include source data
            messages.append({
                "role": "user",
                "content": f"{BRIEF_PROMPT_TEMPLATE.format(source_data=self.source_context)}\n\nAlso: {user_message}"
            })
            self._brief_done = True
        else:
            # Has brief context — use history
            messages.extend(self.conversation_history[-10:])
            messages.append({"role": "user", "content": user_message})

        result = yield from self._agentic_loop(messages, "Chat")
        if not result:
            result = "Could not process your question — please try again."

        self.conversation_history.append({"role": "user",      "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def _agentic_loop(
        self, messages: list[dict], prefix: str
    ) -> Generator[dict, None, str]:
        """LLM → tool calls → repeat → final text. Source data already in context."""
        current = list(messages)
        used_model = PRIMARY_MODEL

        for iteration in range(1, MAX_TOOL_ITERATIONS + 1):
            self.call_count += 1

            yield {
                "type": "log",
                "step": f"iter_{iteration}",
                "message": f"[{prefix}] call #{self.call_count} (iter {iteration})"
            }

            resp, used_model = _call_with_fallback(
                self.client, current, tools=TOOL_DEFINITIONS
            )

            if resp is None:
                yield {
                    "type": "error",
                    "message": "All models rate-limited. Please wait 1–2 minutes and try again."
                }
                return ""

            msg = resp.choices[0].message

            # No tool calls → done
            if not msg.tool_calls:
                text = msg.content or ""
                yield {
                    "type": "log",
                    "step": "done",
                    "message": f"[{prefix}] complete — {iteration} iter, model={used_model}"
                }
                return text

            # Execute tool calls
            current.append(msg)
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

                raw = execute_tool(tname, args)
                capped = _cap(raw)

                yield {
                    "type": "tool_result",
                    "tool": tname,
                    "message": f"← {tname}: {len(raw)} chars"
                }

                current.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": capped,
                })

        # Max iterations — generate final answer without tool calls
        yield {"type": "log", "step": "finalize", "message": "Finalizing answer..."}
        current.append({
            "role": "user",
            "content": "Now write the complete daily brief based on all data gathered. No more tool calls needed."
        })
        self.call_count += 1

        resp, _ = _call_with_fallback(
            self.client, current, tools=None  # no tools = can't call them
        )
        if resp:
            return resp.choices[0].message.content or ""
        return ""
