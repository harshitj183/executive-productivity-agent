"""
Agent tools — callable functions for the main agent.
Descriptions kept short to save tokens on the free Groq tier (7000 ITPM).
"""

from datetime import date
from typing import Optional
from app.data.source_data import (
    EMAIL_THREADS, VOICE_NOTES, MEETING_TRANSCRIPT,
    CALENDARS, PEOPLE,
)

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search all email threads by keyword, sender, or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword to search (case-insensitive)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_voice_notes",
            "description": "Search Arjun's personal voice note transcripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword to search"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_meeting_transcript",
            "description": "Search the Leadership Sync meeting transcript.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword or person name"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get calendar events for a person (arjun/neha/raghav/divya), optionally filtered by date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person": {
                        "type": "string",
                        "enum": ["arjun", "neha", "raghav", "divya"]
                    },
                    "date_filter": {
                        "type": "string",
                        "description": "YYYY-MM-DD (optional)"
                    }
                },
                "required": ["person"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_deadline_urgency",
            "description": "Calculate urgency of a deadline relative to today (21 Sep 2026). Accepts YYYY-MM-DD or day name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deadline_date": {"type": "string", "description": "e.g. 'Wednesday', 'Friday', '2026-09-24'"}
                },
                "required": ["deadline_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_person_info",
            "description": "Get name, role, and email of a stakeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person_key": {"type": "string", "description": "arjun | neha | raghav | divya | priya | facilities"}
                },
                "required": ["person_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_thread_history",
            "description": "Get full chronological email thread to track how a deadline or commitment evolved.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject_keyword": {"type": "string", "description": "Part of thread subject, e.g. 'vendor', 'deck', 'Mumbai'"}
                },
                "required": ["subject_keyword"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    handlers = {
        "search_emails": _search_emails,
        "search_voice_notes": _search_voice_notes,
        "search_meeting_transcript": _search_meeting_transcript,
        "get_calendar_events": _get_calendar_events,
        "calculate_deadline_urgency": _calculate_deadline_urgency,
        "get_person_info": _get_person_info,
        "get_thread_history": _get_thread_history,
    }
    fn = handlers.get(tool_name)
    if not fn:
        return f"Unknown tool: {tool_name}"
    try:
        return fn(**arguments)
    except Exception as e:
        return f"Tool error: {e}"


def _search_emails(query: str) -> str:
    q = query.lower()
    results = []
    for t in EMAIL_THREADS:
        for e in t["emails"]:
            if q in e["body"].lower() or q in e["from"].lower() or q in t["subject"].lower():
                results.append(
                    f"[{t['subject']}][{e['date']} {e['time']}] {e['from']}→{e['to']}: \"{e['body']}\""
                )
    return "\n".join(results) if results else f"No emails matching '{query}'."


def _search_voice_notes(query: str) -> str:
    q = query.lower()
    results = []
    for n in VOICE_NOTES:
        if q in n["transcript"].lower():
            results.append(f"[{n['date']} {n['time']} {n['context']}]: \"{n['transcript']}\"")
    return "\n".join(results) if results else f"No voice notes matching '{query}'."


def _search_meeting_transcript(query: str) -> str:
    q = query.lower()
    lines = [l for l in MEETING_TRANSCRIPT.strip().split("\n") if q in l.lower()]
    return "\n".join(lines) if lines else f"No transcript lines matching '{query}'."


def _get_calendar_events(person: str, date_filter: Optional[str] = None) -> str:
    events = CALENDARS.get(person, [])
    if date_filter:
        events = [e for e in events if e["date"] == date_filter]
    if not events:
        return f"No events for {person}" + (f" on {date_filter}" if date_filter else "") + "."
    name = PEOPLE.get(person, {}).get("name", person)
    return f"{name}:\n" + "\n".join(f"  {e['date']} {e['start']}–{e['end']}: {e['title']}" for e in events)


def _calculate_deadline_urgency(deadline_date: str) -> str:
    today = date(2026, 9, 21)
    day_map = {
        "monday": date(2026, 9, 21), "tuesday": date(2026, 9, 22),
        "wednesday": date(2026, 9, 23), "thursday": date(2026, 9, 24),
        "friday": date(2026, 9, 25),
    }
    dl = deadline_date.lower().strip()
    deadline = None
    for name, d in day_map.items():
        if name in dl:
            deadline = d
            break
    if not deadline:
        try:
            deadline = date.fromisoformat(deadline_date.strip())
        except ValueError:
            return f"Cannot parse '{deadline_date}'."
    delta = (deadline - today).days
    if delta < 0:
        status = f"OVERDUE by {abs(delta)} day(s)"
    elif delta == 0:
        status = "DUE TODAY"
    elif delta == 1:
        status = "DUE TOMORROW"
    else:
        status = f"Due in {delta} days (this week)"
    return f"{deadline.strftime('%A %d %b')} — {status}"


def _get_person_info(person_key: str) -> str:
    p = PEOPLE.get(person_key.lower())
    if not p:
        return f"Unknown: '{person_key}'. Valid: {', '.join(PEOPLE)}"
    return f"{p['name']} | {p['role']} | {p['email']}"


def _get_thread_history(subject_keyword: str) -> str:
    kw = subject_keyword.lower()
    for t in EMAIL_THREADS:
        if kw in t["subject"].lower():
            lines = [f"Thread: {t['subject']}"]
            for i, e in enumerate(t["emails"], 1):
                lines.append(f"  {i}. [{e['date']} {e['time']}] {e['from']}→{e['to']}: \"{e['body']}\"")
            return "\n".join(lines)
    return f"No thread matching '{subject_keyword}'."
