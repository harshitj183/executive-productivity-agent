# Executive Productivity Agent

An AI-powered daily briefing agent built for **Arjun Malhotra, VP Sales** at Veridian Corp.

The agent reads his meeting transcript, email threads, calendar, and personal voice notes for the week of **21–25 September 2026**, then extracts every commitment, tracks deadlines, deduplicates items that evolved across multiple sources, and generates a structured daily brief — with source attribution on every item.

---

## Quick Start (One Command)

```bash
# 1. Clone / navigate to the project root
cd projects/executive-agent

# 2. Start everything
./start.sh
```

That script starts the FastAPI backend on `localhost:8000` and the Vite frontend on `localhost:5173`. Open your browser at **http://localhost:5173**.

### Manual start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## What the Agent Does

### Main Agent
Reads all source data (meeting, emails, calendar, voice notes) and:
- Extracts every commitment Arjun made or is waiting on
- Classifies each item: **MY ACTION** / **WAITING ON OTHERS** / **AMBIGUOUS / FLAGGED**
- Detects deadlines and calculates urgency relative to the current date
- Deduplicates the same commitment when it appears across sources with conflicting dates (e.g. the vendor list deadline shifted Mon → Tue → Wed across 5 email exchanges)
- Cites the source(s) for every item
- Maintains conversation memory so follow-up questions like "What did I promise Raghav?" work without re-explaining context

### Validator Agent
After any response, you can click **Validate** to run a second LLM pass that:
- Checks every claim against the raw source data
- Flags hallucinations or invented facts
- Identifies items in the source data that were omitted
- Returns a structured PASS / PARTIAL / FAIL report with specific citations

### Agent Tools (7 callable tools)
| Tool | Purpose |
|------|---------|
| `search_emails` | Full-text search across all 5 email threads |
| `search_voice_notes` | Search Arjun's personal voice memos |
| `search_meeting_transcript` | Search the Leadership Sync transcript |
| `get_calendar_events` | Get calendar for any person, optionally filtered by date |
| `calculate_deadline_urgency` | Given a date or day name → overdue / today / this week |
| `get_person_info` | Look up name, role, email of any stakeholder |
| `get_thread_history` | Get the full chronological history of an email thread (critical for dedup) |

---

## Source Data

All data is embedded in `backend/app/data/source_data.py`. No external data fetching.

| Source | Content |
|--------|---------|
| Meeting transcript | Leadership Sync, Mon 21 Sep 2026, 9:00–9:35 AM |
| Email threads | 5 threads: Vendor List, Q3 Campaign Deck, Call Reschedule, Expense Variance Report, Mumbai Office Lease Renewal |
| Calendars | Arjun, Neha, Raghav, Divya — full week |
| Voice notes | 2 personal memos by Arjun (Mon evening, Wed morning) |

---

## Architecture

```
frontend (React + Vite + Tailwind)
    │
    │  SSE streams (real-time log + result events)
    ▼
backend (FastAPI)
    ├── POST /api/brief      — generate daily brief
    ├── POST /api/chat       — follow-up Q&A
    ├── POST /api/validate   — run validator agent
    ├── POST /api/reset      — reset conversation
    └── GET  /api/status     — health + LLM call count
    │
    ├── Main Agent (main_agent.py)
    │     └── Agentic loop: LLM → tool calls → LLM → ... → final response
    │         Tools: 7 search/lookup/calculation tools
    │
    ├── Validator Agent (validator_agent.py)
    │     └── Single-shot: source data + response → structured validation report
    │
    └── Source Data (source_data.py)
          └── Embedded structured Python objects (parsed once, reused)
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed flow diagram.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq API — Qwen QwQ 32B |
| Backend | Python 3.12, FastAPI, Uvicorn |
| Agentic loop | Native function calling via Groq SDK |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Streaming | Server-Sent Events (SSE) — real-time log + result streaming |
| Tests | pytest — 30 tests covering all core tools |

---

## Tests

```bash
cd backend
python3 -m pytest tests/ -v
# → 30 passed
```

Tests cover: deadline urgency calculation, email search accuracy, voice note search, meeting transcript search, calendar retrieval, email thread history (dedup tracking), and person lookup.

---

## Key Design Decisions

**Cost optimization**: Source context is injected only on the first message. Subsequent follow-ups use only the conversation history, not the full source data again. Tool calls are used for targeted lookups rather than sending the entire corpus every time.

**No hallucination policy**: The system prompt explicitly forbids the agent from inventing ownership, dates, or facts. Items with unclear ownership (Mumbai lease) are flagged — not assigned by assumption.

**Dedup by thread history**: The `get_thread_history` tool returns the full email thread chronologically, so the agent can see that the vendor list deadline shifted Mon → Tue → Wed and surface only the final version.

**Source attribution**: Every item in the brief shows which source(s) it came from — this is enforced in the system prompt and validated by the validator agent.

**Conversation memory**: The main agent stores all prior turns so "What did I promise Raghav?" works on turn 5 without re-sending the full source context.

---

## Project Structure

```
executive-agent/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── main_agent.py      # Main agentic loop + tool use
│   │   │   ├── validator_agent.py # Fact-checking agent
│   │   │   └── tools.py           # 7 callable tools + implementations
│   │   ├── api/
│   │   │   └── routes.py          # FastAPI routes (SSE streaming)
│   │   ├── core/
│   │   │   └── session.py         # Session management
│   │   ├── data/
│   │   │   └── source_data.py     # All source data (embedded)
│   │   └── main.py                # App entrypoint
│   ├── tests/
│   │   └── test_tools.py          # 30 pytest tests
│   ├── .env                       # GROQ_API_KEY
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── WelcomeScreen.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ReasoningTrace.tsx # Live tool call log
│   │   │   ├── ValidationPanel.tsx
│   │   │   └── ChatInput.tsx      # Input + quick prompts
│   │   ├── App.tsx
│   │   ├── api.ts                 # SSE client
│   │   └── types.ts
│   └── package.json
├── docs/
│   ├── architecture.md
│   └── prd.md
├── start.sh
└── README.md
```
