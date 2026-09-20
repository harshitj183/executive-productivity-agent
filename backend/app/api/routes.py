"""
FastAPI routes — all endpoints for the Executive Productivity Agent.

Endpoints:
  POST /api/brief         — Generate (or regenerate) the daily brief
  POST /api/chat          — Send a follow-up question
  POST /api/validate      — Run the validator against the last brief
  POST /api/reset         — Reset conversation history
  GET  /api/status        — Health check + LLM call count
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.session import get_session, reset_session

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Request models ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class ValidateRequest(BaseModel):
    content: str


# ── SSE helpers ───────────────────────────────────────────────────────────────

def _event(data: dict) -> str:
    """Format a dict as an SSE data frame."""
    return f"data: {json.dumps(data)}\n\n"


async def _stream_sync_generator(gen) -> AsyncGenerator[str, None]:
    """
    Run a synchronous Python generator (the agentic loop) in a thread pool
    so it doesn't block FastAPI's async event loop.

    Uses asyncio.to_thread (Python 3.9+) which is cleaner than get_event_loop().
    """
    sentinel = object()

    def _next_item():
        try:
            return next(gen)
        except StopIteration:
            return sentinel

    while True:
        item = await asyncio.to_thread(_next_item)
        if item is sentinel:
            yield _event({"type": "done", "message": "Stream complete"})
            break
        yield _event(item)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/brief")
async def generate_brief():
    """Generate the daily brief — SSE stream of reasoning + final result."""
    try:
        session = get_session()
        gen = session.main_agent.generate_brief()

        async def stream():
            async for chunk in _stream_sync_generator(gen):
                try:
                    data = json.loads(chunk.removeprefix("data: ").strip())
                    if data.get("type") == "result":
                        session.last_brief = data.get("content", "")
                        session.brief_generated = True
                except Exception:
                    pass
                yield chunk

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.post("/chat")
async def chat(request: ChatRequest):
    """Follow-up Q&A — SSE stream."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        session = get_session()
        gen = session.main_agent.chat(request.message)
        return StreamingResponse(
            _stream_sync_generator(gen),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.post("/validate")
async def validate(request: ValidateRequest):
    """Run the validator agent — SSE stream."""
    content = request.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Content cannot be empty.")
    try:
        session = get_session()
        gen = session.validator_agent.validate(content)
        return StreamingResponse(
            _stream_sync_generator(gen),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.post("/reset")
async def reset():
    """Reset conversation history and session state."""
    try:
        reset_session()
        return {"status": "ok", "message": "Session reset. Conversation history cleared."}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@router.get("/status")
async def status():
    """Health check + usage stats."""
    try:
        session = get_session()
        return {
            "status": "ok",
            "brief_generated": session.brief_generated,
            "total_llm_calls": session.total_llm_calls,
            "conversation_turns": len(session.main_agent.conversation_history) // 2,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/sources")
async def get_sources():
    """Return structured source data (for demo / transparency panel)."""
    from app.data.source_data import (
        EMAIL_THREADS, VOICE_NOTES, CALENDARS, MEETING_TRANSCRIPT, PEOPLE
    )
    return {
        "people": PEOPLE,
        "meeting_transcript": MEETING_TRANSCRIPT.strip(),
        "email_threads": EMAIL_THREADS,
        "voice_notes": VOICE_NOTES,
        "calendars": CALENDARS,
        "week": "21–25 September 2026",
    }
