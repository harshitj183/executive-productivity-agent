"""
Agent tools — these are the callable functions the main agent can invoke
to search source data, calculate deadlines, and cross-reference entries.
"""

from datetime import date, datetime, timedelta
from typing import Optional
from app.data.source_data import (
    EMAIL_THREADS, VOICE_NOTES, MEETING_TRANSCRIPT,
    CALENDARS, PEOPLE, WEEK_START, WEEK_END
)

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search all email threads for a keyword, person name, or topic. Returns matching emails with their thread subject, date, sender, and body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword or phrase to search for (case-insensitive)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_voice_notes",
            "description": "Search Arjun's voice note transcripts for a keyword or topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword or phrase to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_meeting_transcript",
            "description": "Search the Leadership Sync meeting transcript for specific statements, commitments, or topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword, person name, or topic to search for"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calendar_events",
            "description": "Get calendar events for a specific person and/or date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person": {
                        "type": "string",
                        "description": "Person key: arjun, neha, raghav, divya",
                        "enum": ["arjun", "neha", "raghav", "divya"]
                    },
                    "date_filter": {
                        "type": "string",
                        "description": "Optional specific date in YYYY-MM-DD format to filter by"
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
            "description": "Given a deadline date string, calculate how many days away it is from today (2026-09-21) and whether it's overdue, today, tomorrow, or this week.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deadline_date": {
                        "type": "string",
                        "description": "Deadline date in YYYY-MM-DD format or natural language like 'Wednesday', 'Friday', 'Thursday morning'"
                    }
                },
                "required": ["deadline_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_person_info",
            "description": "Get name, role, and email of a person involved in Arjun's week.",
            "parameters": {
                "type": "object",
                "properties": {
                    "person_key": {
                        "type": "string",
                        "description": "Person key: arjun, neha, raghav, divya, priya, facilities"
                    }
                },
                "required": ["person_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_thread_history",
            "description": "Get the full email thread history for a specific subject to track how a commitment or date evolved.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject_keyword": {
                        "type": "string",
                        "description": "Keyword from the thread subject (e.g. 'vendor', 'deck', 'expense', 'Mumbai', 'reschedule')"
                    }
                },
                "required": ["subject_keyword"]
            }
        }
    }
]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool by name and return result as a string."""
    handlers = {
        "search_emails": _search_emails,
        "search_voice_notes": _search_voice_notes,
        "search_meeting_transcript": _search_meeting_transcript,
        "get_calendar_events": _get_calendar_events,
        "calculate_deadline_urgency": _calculate_deadline_urgency,
        "get_person_info": _get_person_info,
        "get_thread_history": _get_thread_history,
    }
    handler = handlers.get(tool_name)
    if not handler:
        return f"Unknown tool: {tool_name}"
    return handler(**arguments)


# ── Tool implementations ──────────────────────────────────────────────────────

def _search_emails(query: str) -> str:
    query_lower = query.lower()
    results = []
    for thread in EMAIL_THREADS:
        for email in thread["emails"]:
            if (query_lower in email["body"].lower()
                    or query_lower in email["from"].lower()
                    or query_lower in email["to"].lower()
                    or query_lower in thread["subject"].lower()):
                results.append(
                    f"[Thread: {thread['subject']}] [{email['date']} {email['time']}]\n"
                    f"  From: {email['from']} → To: {email['to']}\n"
                    f"  \"{email['body']}\""
                )
    if not results:
        return f"No emails found matching '{query}'."
    return f"Found {len(results)} email(s) matching '{query}':\n\n" + "\n\n".join(results)


def _search_voice_notes(query: str) -> str:
    query_lower = query.lower()
    results = []
    for note in VOICE_NOTES:
        if query_lower in note["transcript"].lower():
            results.append(
                f"[{note['date']} {note['time']} — {note['context']}]\n"
                f"  \"{note['transcript']}\""
            )
    if not results:
        return f"No voice notes found matching '{query}'."
    return f"Found {len(results)} voice note(s) matching '{query}':\n\n" + "\n\n".join(results)


def _search_meeting_transcript(query: str) -> str:
    query_lower = query.lower()
    lines = MEETING_TRANSCRIPT.strip().split("\n")
    matching_lines = [line for line in lines if query_lower in line.lower()]
    if not matching_lines:
        return f"No lines in the meeting transcript matching '{query}'."
    return f"Matching lines from Leadership Sync transcript:\n\n" + "\n".join(matching_lines)


def _get_calendar_events(person: str, date_filter: Optional[str] = None) -> str:
    events = CALENDARS.get(person)
    if not events:
        return f"No calendar found for '{person}'."
    if date_filter:
        events = [e for e in events if e["date"] == date_filter]
    if not events:
        return f"No events found for {person} on {date_filter}."
    person_info = PEOPLE.get(person, {})
    name = person_info.get("name", person)
    lines = [f"Calendar for {name}:"]
    for e in events:
        lines.append(f"  {e['date']} {e['start']}–{e['end']}: {e['title']}")
    return "\n".join(lines)


def _calculate_deadline_urgency(deadline_date: str) -> str:
    today = date(2026, 9, 21)
    day_map = {
        "monday": date(2026, 9, 21),
        "tuesday": date(2026, 9, 22),
        "wednesday": date(2026, 9, 23),
        "thursday": date(2026, 9, 24),
        "friday": date(2026, 9, 25),
    }

    # Normalize natural language
    deadline_lower = deadline_date.lower().strip()
    for day_name, day_date in day_map.items():
        if day_name in deadline_lower:
            deadline = day_date
            break
    else:
        try:
            deadline = date.fromisoformat(deadline_date.strip())
        except ValueError:
            return f"Could not parse deadline date: '{deadline_date}'. Use YYYY-MM-DD or day name (Monday–Friday)."

    delta = (deadline - today).days

    if delta < 0:
        status = f"OVERDUE by {abs(delta)} day(s)"
    elif delta == 0:
        status = "DUE TODAY"
    elif delta == 1:
        status = "DUE TOMORROW"
    elif delta <= 4:
        status = f"Due in {delta} days (this week)"
    else:
        status = f"Due in {delta} days"

    return (
        f"Deadline: {deadline.strftime('%A, %d %B %Y')}\n"
        f"Today: {today.strftime('%A, %d %B %Y')}\n"
        f"Status: {status}"
    )


def _get_person_info(person_key: str) -> str:
    person = PEOPLE.get(person_key.lower())
    if not person:
        return f"No person found with key '{person_key}'. Valid keys: {', '.join(PEOPLE.keys())}"
    return f"Name: {person['name']}\nRole: {person['role']}\nEmail: {person['email']}"


def _get_thread_history(subject_keyword: str) -> str:
    keyword_lower = subject_keyword.lower()
    for thread in EMAIL_THREADS:
        if keyword_lower in thread["subject"].lower():
            lines = [f"Full thread: '{thread['subject']}'"]
            for i, email in enumerate(thread["emails"], 1):
                lines.append(
                    f"\n  Email {i} — [{email['date']} {email['time']}]"
                    f"\n  From: {email['from']} → To: {email['to']}"
                    f"\n  \"{email['body']}\""
                )
            return "\n".join(lines)
    return f"No thread found with subject containing '{subject_keyword}'."
