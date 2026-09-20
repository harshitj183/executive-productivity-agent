# Product Requirements Document — Executive Productivity Agent

**Version**: 1.0  
**Date**: September 2026  
**User**: Arjun Malhotra, VP Sales, Veridian Corp  

---

## Problem Statement

Arjun runs a high-velocity week: back-to-back meetings, 5+ active email threads, calendar events across 4 people, and personal voice notes he dictates to himself on the go. By Monday afternoon, he's already made commitments across multiple contexts — some verbal in a meeting, some via email, some as quick voice reminders — and there's no single place that tells him:

1. What he's committed to doing himself
2. What he's waiting on from others
3. What's unclear, overdue, or about to be

The result: things slip. A vendor list that was promised Monday gets pushed twice. A client call gets confirmed via email but nobody knows if the calendar was updated. A lease renewal has a Friday deadline but nobody has confirmed who's signing.

## Solution

An AI agent that reads all of Arjun's sources — meeting transcript, email threads, calendar, voice notes — and produces a clear, honest daily brief. Not a summary. A **commitment tracker**: who owes what to whom, by when, and what's still unresolved.

## User

One user: Arjun Malhotra. The agent serves him exclusively. Neha, Raghav, Divya, Priya, and Facilities are sources of information — their emails and calendars are inputs the agent reads on Arjun's behalf.

## Core Features

### F1: Daily Brief Generation
On demand, the agent reads all sources and produces a structured brief:
- **MY ACTIONS**: items Arjun committed to do, sorted by urgency (overdue → today → this week)
- **WAITING ON OTHERS**: items Arjun is expecting from others
- **FLAGGED**: ambiguous ownership, unresolved items, deadline risks

Each item shows: description, deadline, classification, and source(s).

### F2: Source Attribution
Every item in the brief must cite which source(s) it came from. No unattributed claims.

### F3: Deduplication
The same commitment appearing across multiple sources (meeting + multiple emails) is surfaced once — as the most recent/final version — with the evolution history noted.

### F4: Honest Flagging
Items with unclear ownership (e.g. Mumbai lease renewal) are explicitly flagged with "ownership unclear" rather than assigned to Arjun by assumption.

### F5: Conversation Memory
After the brief is generated, Arjun can ask follow-up questions. The agent remembers all prior turns in the session. "What did I promise Raghav?" works on turn 5.

### F6: Validator Agent
A second agent that fact-checks any response against the raw source data. Returns PASS / PARTIAL / FAIL with specific issues cited.

### F7: Reasoning Trace
Every response shows a collapsible log of the agent's tool calls — which data it searched, what it found — so the reasoning is inspectable.

## Non-Goals

- Email sending, calendar editing, or any write actions
- Serving anyone other than Arjun (no multi-user support)
- Processing data outside the provided source pack
- Persistent storage across sessions (in-memory only for this prototype)

## Acceptance Criteria

| Criterion | Test |
|-----------|------|
| All 5 commitment areas surface correctly | Manual review of brief |
| Vendor list deadline shows Wed (not Mon/Tue) | Thread history shows the shift |
| Campaign deck review shows Thu 9:30 AM (not Wed) | Thread history shows the shift |
| Mumbai lease is flagged AMBIGUOUS (not assigned to Arjun) | Brief includes explicit flag |
| Meridian call shows confirmed Wed 3 PM | Email thread confirms this |
| Expense report shows DELIVERED (from Divya Wed evening) | Thread + meeting cross-referenced |
| Validator correctly identifies grounded vs invented claims | Manual review of validator output |
| Follow-up "What did I promise Raghav?" works without re-explaining | Conversation memory test |
| 30 unit tests pass | `pytest tests/ -v` |

## Out of Scope (for this prototype)

- Persistent memory across browser sessions
- Multi-device sync
- Calendar write access
- Email draft generation
- Mobile app
