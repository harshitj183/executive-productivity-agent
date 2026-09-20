"""
Session manager — holds MainAgent and ValidatorAgent instances per session.
Avoids recreating agents on every request (preserves conversation memory).
"""

import os
import logging
from app.agents.main_agent import MainAgent
from app.agents.validator_agent import ValidatorAgent

logger = logging.getLogger(__name__)


class AgentSession:
    """Holds a pair of main + validator agents for a user session."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.main_agent = MainAgent(api_key=api_key)
        self.validator_agent = ValidatorAgent(api_key=api_key)
        self.brief_generated = False
        self.last_brief: str = ""

    def reset(self):
        self.main_agent.reset_conversation()
        self.brief_generated = False
        self.last_brief = ""
        logger.info("Session reset.")

    @property
    def total_llm_calls(self) -> int:
        return self.main_agent.call_count + self.validator_agent.call_count


# Single global session (one user — the executive)
_session: AgentSession | None = None


def get_session() -> AgentSession:
    global _session
    if _session is None:
        _session = AgentSession()
    return _session


def reset_session():
    global _session
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    if _session:
        _session.reset()
    else:
        _session = AgentSession()
