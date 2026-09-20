"""
Main Agent — Executive Productivity Agent for Arjun Malhotra.

Responsibilities:
- Extract commitments from all sources (meeting, email, calendar, voice notes)
- Classify each commitment: MY_ACTION | WAITING_ON_OTHERS | AMBIGUOUS
- Detect deadlines and urgency
- Deduplicate the same commitment appearing across multiple sources
- Generate the daily brief
- Answer follow-up questions with memory
- Show source attribution for every item

Uses Groq API with function-calling (tool use).
"""

import json
import logging
import os
from typing import Any, Generator, Optional

from groq import Groq

from app.agents.tools import TOOL_DEFINITIONS, execute_tool
from app.data.source_data import get_all_sources_as_text

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
MAX_TOOL_ITERATIONS = 8  # cap agentic loops to control cost

SYSTEM_PROMPT = """You are an Executive Productivity Agent built exclusively for Arjun Malhotra, VP Sales at Veridian Corp.
Your job is to read his meeting transcript, emails, calendar, and voice notes — then extract every commitment, track deadlines, and give him a clear, honest daily brief.

CRITICAL RULES:
1. Never invent facts. If something is unclear or unassigned, say so explicitly — don't guess ownership.
2. Every commitment you surface must cite which source(s) it came from (meeting, email thread title, voice note date).
3. Classify every item as:
   - MY_ACTION: Arjun committed to do this himself
   - WAITING_ON_OTHERS: Someone else committed to deliver something to Arjun
   - AMBIGUOUS: Ownership is unclear or explicitly unresolved (flag these with a note)
4. When the same commitment appears in multiple sources with conflicting dates, surface the MOST RECENT/FINAL version and note the history.
5. Use your tools to search source data — don't rely only on your memory of the context.
6. Be concise but complete. Arjun is busy.
7. Today is Monday, 21 September 2026. The week runs Mon 21 Sep – Fri 25 Sep.

When generating the daily brief, structure it as:
- Section 1: MY ACTIONS (items Arjun must do, sorted by urgency)
- Section 2: WAITING ON OTHERS (items Arjun is expecting from others)
- Section 3: FLAGGED / NEEDS ATTENTION (ambiguous ownership, conflicting info, overdue items)

For follow-up questions, use conversation history — Arjun should not have to re-explain context."""

BRIEF_GENERATION_PROMPT = """Generate the daily brief for Arjun Malhotra for the week of 21–25 September 2026.

Use your tools to:
1. Search emails, meeting transcript, and voice notes for all commitments
2. Check deadlines and urgency for each item
3. Identify which thread shows the final/latest version of any rescheduled item
4. Flag the Mumbai lease situation explicitly (ownership unclear)

Then produce a structured brief with:
- MY ACTIONS (Arjun's own commitments, sorted overdue → today → this week)
- WAITING ON OTHERS (what Arjun is expecting from others)
- FLAGGED (ambiguous ownership, conflicts, risks)

For each item, cite the source(s) and the current deadline."""


class MainAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.conversation_history: list[dict] = []
        self.source_context = get_all_sources_as_text()
        self.call_count = 0
        self._initialized = False

    def reset_conversation(self):
        """Clear conversation history but keep source context."""
        self.conversation_history = []
        self._initialized = False
        logger.info("Conversation history cleared.")

    def _build_messages(self, user_message: str) -> list[dict]:
        """Build the full message list for the API call."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Include source context in the first message only (cost optimization)
        if not self._initialized:
            context_intro = (
                "Here is all source data for this week. Use this along with your tools "
                "to answer questions accurately.\n\n"
                f"{self.source_context}\n\n"
                "--- End of source data ---\n\n"
                f"User request: {user_message}"
            )
            messages.append({"role": "user", "content": context_intro})
            self._initialized = True
        else:
            # Subsequent messages: only include the new user message
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": user_message})

        return messages

    def generate_brief(self) -> Generator[dict, None, None]:
        """Generate the initial daily brief. Yields log events and the final result."""
        yield {"type": "log", "step": "init", "message": "Starting brief generation..."}

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Here is all source data for this week:\n\n{self.source_context}\n\n"
                    f"--- End of source data ---\n\n{BRIEF_GENERATION_PROMPT}"
                )
            }
        ]
        self._initialized = True

        result = yield from self._run_agentic_loop(messages, log_prefix="Brief")
        if result is None:
            result = ""

        # Store in conversation history for follow-ups
        self.conversation_history.append({"role": "user", "content": BRIEF_GENERATION_PROMPT})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def chat(self, user_message: str) -> Generator[dict, None, None]:
        """Handle a follow-up question with full conversation memory."""
        yield {"type": "log", "step": "chat_start", "message": f"Processing: {user_message[:80]}..."}

        messages = self._build_messages(user_message)
        result = yield from self._run_agentic_loop(messages, log_prefix="Chat")
        if result is None:
            result = ""

        # Append to history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": result})

        yield {"type": "result", "content": result}

    def _run_agentic_loop(self, messages: list[dict], log_prefix: str = "") -> Generator[dict, None, str]:
        """
        Core agentic loop: call LLM → handle tool calls → repeat → return final text.
        Yields log events throughout, returns the final text response.
        """
        iteration = 0
        current_messages = list(messages)

        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1
            self.call_count += 1

            yield {
                "type": "log",
                "step": f"llm_call_{iteration}",
                "message": f"[{log_prefix}] LLM call #{self.call_count} (iteration {iteration})"
            }

            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=current_messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.1,
                    max_tokens=800,
                )
            except Exception as e:
                logger.error(f"Groq API error: {e}")
                yield {"type": "error", "message": f"LLM call failed: {str(e)}"}
                return f"Error: {str(e)}"

            choice = response.choices[0]
            message = choice.message

            # If there are tool calls, execute them
            if message.tool_calls:
                current_messages.append(message)  # assistant message with tool_calls

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}

                    yield {
                        "type": "tool_call",
                        "tool": tool_name,
                        "args": args,
                        "message": f"Calling tool: {tool_name}({json.dumps(args)})"
                    }

                    result = execute_tool(tool_name, args)

                    yield {
                        "type": "tool_result",
                        "tool": tool_name,
                        "message": f"Tool result ({len(result)} chars)"
                    }

                    current_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                # Continue the loop to let the model process tool results
                continue

            # No tool calls — we have the final response
            final_text = message.content or ""
            yield {
                "type": "log",
                "step": "complete",
                "message": f"[{log_prefix}] Done after {iteration} iteration(s), {self.call_count} total LLM calls."
            }
            return final_text

        # Exceeded max iterations
        logger.warning(f"Hit max iterations ({MAX_TOOL_ITERATIONS})")
        yield {
            "type": "log",
            "step": "max_iterations",
            "message": f"Warning: reached max tool iterations ({MAX_TOOL_ITERATIONS})."
        }
        # Try to get a final response
        current_messages.append({
            "role": "user",
            "content": "Please provide your final answer based on what you've gathered so far."
        })
        self.call_count += 1
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=current_messages,
            temperature=0.1,
            max_tokens=4096,
        )
        final_text = response.choices[0].message.content or ""
        return final_text
