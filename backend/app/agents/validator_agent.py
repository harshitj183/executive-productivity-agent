"""
Validator Agent — checks the Main Agent's output for:
1. Factual grounding (every claim must trace back to source data)
2. Hallucinations (invented facts, dates, names, or ownership)
3. Missing items (commitments present in the source data but absent from the brief)
4. Classification errors (wrong MY_ACTION / WAITING_ON_OTHERS / AMBIGUOUS label)

This runs AFTER the main agent produces output. It gets the same source data
and the main agent's output, then returns a structured validation report.
"""

import json
import logging
import os
from typing import Generator

from groq import Groq

from app.data.source_data import get_all_sources_as_text

logger = logging.getLogger(__name__)

GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

VALIDATOR_SYSTEM_PROMPT = """You are a strict fact-checker for an AI executive assistant.
Your sole job is to validate whether a given response about commitments and deadlines is actually grounded in the source data.

You will receive:
1. The original source data (meeting transcript, emails, calendar, voice notes)
2. The AI assistant's response to validate

Your job:
- Check every commitment, date, deadline, and ownership claim against the source data
- Flag anything that appears to be invented (not traceable to any source)
- Identify anything important that was in the source data but missing from the response
- Flag any misclassifications (wrong owner, wrong date, wrong status)

Output a structured validation report with:
- VERDICT: PASS | FAIL | PARTIAL
- GROUNDED_ITEMS: List of claims that are correctly sourced
- ISSUES: List of specific problems found (hallucinations, wrong dates, wrong owners, missing items)
- MISSING_ITEMS: List of commitments in the source data that were omitted
- SUMMARY: One paragraph summary of overall quality

Be precise and cite specific source lines when flagging issues.
Today is Monday, 21 September 2026."""


class ValidatorAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.source_context = get_all_sources_as_text()
        self.call_count = 0

    def validate(self, agent_output: str) -> Generator[dict, None, None]:
        """
        Validate the main agent's output against source data.
        Yields log events and the final validation report.
        """
        yield {"type": "log", "step": "validator_start", "message": "Validator agent starting..."}

        self.call_count += 1
        prompt = (
            f"=== SOURCE DATA ===\n{self.source_context}\n\n"
            f"=== AI ASSISTANT RESPONSE TO VALIDATE ===\n{agent_output}\n\n"
            "Please validate the response against the source data and produce a structured validation report."
        )

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": VALIDATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=3000,
            )
            validation_text = response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Validator API error: {e}")
            yield {"type": "error", "message": f"Validator failed: {str(e)}"}
            return

        yield {
            "type": "log",
            "step": "validator_complete",
            "message": f"Validator completed. Total LLM calls: {self.call_count}"
        }
        yield {"type": "validation_result", "content": validation_text}
