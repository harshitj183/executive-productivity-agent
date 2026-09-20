"""
Tests for core agent tools — deadline calculation, search accuracy, cross-referencing.
Run with: pytest tests/
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.agents.tools import execute_tool


class TestDeadlineUrgency:
    """Tests for the deadline calculation tool."""

    def test_due_today(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "2026-09-21"})
        assert "DUE TODAY" in result

    def test_due_tomorrow(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "Tuesday"})
        assert "DUE TOMORROW" in result

    def test_due_wednesday(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "Wednesday"})
        assert "Due in 2 days" in result

    def test_due_thursday(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "Thursday"})
        assert "Due in 3 days" in result

    def test_due_friday(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "Friday"})
        assert "Due in 4 days" in result

    def test_overdue(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "2026-09-20"})
        assert "OVERDUE" in result

    def test_natural_language_thursday_morning(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "Thursday morning"})
        assert "Thursday" in result

    def test_invalid_date(self):
        result = execute_tool("calculate_deadline_urgency", {"deadline_date": "next quarter"})
        assert "parse" in result.lower()  # "Cannot parse" or "Could not parse"


class TestEmailSearch:
    """Tests for email search accuracy."""

    def test_vendor_list_search(self):
        result = execute_tool("search_emails", {"query": "vendor list"})
        assert "Vendor List" in result
        assert "raghav" in result.lower()

    def test_search_by_person(self):
        result = execute_tool("search_emails", {"query": "divya.rao"})
        assert "Expense Variance" in result or "Mumbai" in result

    def test_mumbai_lease_search(self):
        result = execute_tool("search_emails", {"query": "Mumbai"})
        assert "Mumbai Office Lease Renewal" in result
        assert "Friday" in result or "25 September" in result

    def test_no_results(self):
        result = execute_tool("search_emails", {"query": "xyznomatch999"})
        assert "No email" in result  # "No emails found" or "No emails matching"

    def test_meridian_search(self):
        result = execute_tool("search_emails", {"query": "Meridian"})
        assert "Priya" in result or "Call Reschedule" in result


class TestVoiceNoteSearch:
    """Tests for voice note search."""

    def test_vendor_list_voice(self):
        result = execute_tool("search_voice_notes", {"query": "vendor list"})
        assert "Raghav" in result

    def test_expense_voice(self):
        result = execute_tool("search_voice_notes", {"query": "expense"})
        assert "Wednesday evening" in result

    def test_mumbai_voice(self):
        result = execute_tool("search_voice_notes", {"query": "Mumbai"})
        assert "lease" in result.lower()


class TestMeetingTranscriptSearch:
    """Tests for meeting transcript search."""

    def test_vendor_in_transcript(self):
        result = execute_tool("search_meeting_transcript", {"query": "vendor list"})
        assert "Raghav" in result or "vendor" in result.lower()

    def test_mumbai_in_transcript(self):
        result = execute_tool("search_meeting_transcript", {"query": "Mumbai"})
        assert "renewal" in result.lower() or "Mumbai" in result

    def test_no_match_transcript(self):
        result = execute_tool("search_meeting_transcript", {"query": "zzznomatch"})
        assert "No" in result and "match" in result.lower()  # any "no match" message


class TestCalendarRetrieval:
    """Tests for calendar events."""

    def test_arjun_calendar(self):
        result = execute_tool("get_calendar_events", {"person": "arjun"})
        assert "Board Prep" in result
        assert "Arjun Malhotra" in result

    def test_arjun_thursday(self):
        result = execute_tool("get_calendar_events", {"person": "arjun", "date_filter": "2026-09-24"})
        assert "Board Prep Session" in result

    def test_neha_calendar(self):
        result = execute_tool("get_calendar_events", {"person": "neha"})
        assert "Deck Review" in result

    def test_no_events_on_date(self):
        result = execute_tool("get_calendar_events", {"person": "arjun", "date_filter": "2026-09-26"})
        assert "No event" in result  # "No events found" or "No events for"


class TestThreadHistory:
    """Tests for email thread history retrieval — critical for dedup tracking."""

    def test_vendor_thread_shows_evolution(self):
        result = execute_tool("get_thread_history", {"subject_keyword": "vendor"})
        # Should show the date shifting from Mon → Tue → Wed
        assert "2026-09-21" in result
        assert "2026-09-22" in result
        assert "2026-09-23" in result

    def test_deck_thread_shows_date_shift(self):
        result = execute_tool("get_thread_history", {"subject_keyword": "Campaign Deck"})
        # Wednesday → Thursday shift must be traceable
        assert "Wednesday" in result or "Thursday" in result

    def test_expense_thread(self):
        result = execute_tool("get_thread_history", {"subject_keyword": "Expense"})
        assert "Wednesday evening" in result

    def test_unknown_thread(self):
        result = execute_tool("get_thread_history", {"subject_keyword": "xyznomatch"})
        assert "No thread" in result  # "No thread found" or "No thread matching"


class TestPersonInfo:
    """Tests for person lookup."""

    def test_arjun(self):
        result = execute_tool("get_person_info", {"person_key": "arjun"})
        assert "VP Sales" in result

    def test_priya(self):
        result = execute_tool("get_person_info", {"person_key": "priya"})
        assert "Meridian Logistics" in result

    def test_invalid_person(self):
        result = execute_tool("get_person_info", {"person_key": "batman"})
        assert "Unknown" in result or "No person" in result  # any not-found message
