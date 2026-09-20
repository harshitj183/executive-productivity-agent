"""
Validator Agent — fact-checks the main agent's output against source data.

Token budget: keeps total input under 3500 tokens.
- System prompt: ~150 tokens
- Source summary: capped at ~600 tokens  
- Agent output: capped at ~300 tokens
"""

import logging
import os
from typing import Generator

from groq import Groq

from app.data.source_data import get_all_sources_as_text

logger = logging.getLogger(__name__)

GROQ_MODEL = "openai/gpt-oss-120b"  # hardcoded
MODEL_FALLBACK_CHAIN = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

# Source context trimmed to ~2400 chars (~600 tokens) for validator
SOURCE_CHAR_LIMIT = 2400
AGENT_OUTPUT_CHAR_LIMIT = 1200

VALIDATOR_SYSTEM_PROMPT = """You are a fact-checker for an AI executive assistant output.
Check the response against the source data. Return a concise report:

VERDICT: PASS | PARTIAL | FAIL
GROUNDED: (list claims that are correctly sourced)
ISSUES: (invented facts, wrong dates, wrong ownership, hallucinations)
MISSING: (important commitments from source data that were omitted)
SUMMARY: (1-2 sentences)

Today is Monday, 21 September 2026."""


class ValidatorAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        # Trim source context to stay under token limit
        full = get_all_sources_as_text()
        self.source_context = full[:SOURCE_CHAR_LIMIT] + ("…" if len(full) > SOURCE_CHAR_LIMIT else "")
        self.call_count = 0

    def validate(self, agent_output: str) -> Generator[dict, None, None]:
        yield {"type": "log", "step": "validator_start", "message": "Validator checking output..."}

        # Cap agent output too
        output = agent_output[:AGENT_OUTPUT_CHAR_LIMIT]
        if len(agent_output) > AGENT_OUTPUT_CHAR_LIMIT:
            output += "…[truncated]"

        self.call_count += 1
        prompt = (
            f"SOURCE DATA:\n{self.source_context}\n\n"
            f"AGENT RESPONSE:\n{output}\n\n"
            "Validate the agent response against the source data."
        )

        try:
            models_to_try = [GROQ_MODEL] + [m for m in MODEL_FALLBACK_CHAIN if m != GROQ_MODEL]
            result = ""
            for model in models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": VALIDATOR_SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.0,
                        max_tokens=700,
                    )
                    result = response.choices[0].message.content or ""
                    break
                except Exception as e:
                    if "429" in str(e):
                        continue
                    raise
            if not result:
                yield {"type": "error", "message": "All models rate-limited. Please wait a minute."}
                return
        except Exception as e:
            err = str(e)
            logger.error(f"Validator error: {err}")
            if "429" in err or "rate_limit" in err.lower():
                yield {"type": "error", "message": "Rate limit hit. Please wait a minute and retry."}
            else:
                yield {"type": "error", "message": f"Validator failed: {err}"}
            return

        yield {
            "type": "log",
            "step": "validator_complete",
            "message": f"Validator done. Call #{self.call_count}"
        }
        yield {"type": "validation_result", "content": result}
