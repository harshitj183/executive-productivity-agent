# Architecture — Executive Productivity Agent

## System Overview

The system has two runtime processes: a Python/FastAPI backend that runs the agents and a React/Vite frontend that streams the results in real time.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (React)                          │
│                                                                 │
│  ┌──────────────┐   SSE stream    ┌────────────────────────┐   │
│  │  Welcome     │ ─────────────▶  │   Chat + Brief view    │   │
│  │  Screen      │                 │   + Reasoning Trace    │   │
│  └──────────────┘                 └────────────────────────┘   │
│         │                                    │                  │
│         │ POST /api/brief            POST /api/chat             │
│         │ POST /api/validate         POST /api/reset            │
└─────────┼────────────────────────────────────┼──────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  routes.py — wraps agent generators as SSE StreamingResponse   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    AgentSession                          │  │
│  │  (one global session — preserves conversation memory)    │  │
│  │                                                          │  │
│  │  ┌─────────────────┐    ┌──────────────────────────┐    │  │
│  │  │   Main Agent    │    │    Validator Agent        │    │  │
│  │  │                 │    │                           │    │  │
│  │  │  conversation   │    │  single-shot fact-check   │    │  │
│  │  │  history ✓      │    │  against source data      │    │  │
│  │  │  tool calling ✓ │    │  returns PASS/FAIL report │    │  │
│  │  └────────┬────────┘    └──────────────────────────┘    │  │
│  │           │                                              │  │
│  └───────────┼──────────────────────────────────────────────┘  │
│              │                                                  │
│     ┌────────▼─────────────────────────────────────────┐       │
│     │              Agentic Loop                        │       │
│     │                                                  │       │
│     │  1. Build messages (system + context + history)  │       │
│     │  2. Call Groq API with tool_choice="auto"        │       │
│     │  3. If tool_calls → execute → append results     │       │
│     │  4. Repeat up to 8 iterations                    │       │
│     │  5. When no tool_calls → return final text       │       │
│     │                                                  │       │
│     │  Yields: log / tool_call / tool_result / result  │       │
│     └────────┬─────────────────────────────────────────┘       │
│              │                                                  │
│     ┌────────▼──────────────────────────────────────────┐      │
│     │                  Tools (7)                        │      │
│     │                                                   │      │
│     │  search_emails            → EMAIL_THREADS         │      │
│     │  search_voice_notes       → VOICE_NOTES           │      │
│     │  search_meeting_transcript→ MEETING_TRANSCRIPT    │      │
│     │  get_calendar_events      → CALENDARS             │      │
│     │  calculate_deadline_urgency → date math           │      │
│     │  get_person_info          → PEOPLE                │      │
│     │  get_thread_history       → EMAIL_THREADS (full)  │      │
│     └───────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Groq API (Qwen QwQ 32B)                       │
│                   Tool calling / function calling               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow — Brief Generation

```
User clicks "Generate Brief"
        │
        ▼
POST /api/brief
        │
        ▼
MainAgent.generate_brief()
        │
        ├─ builds prompt: system + full source context + brief generation instructions
        │
        ├─ Iteration 1: LLM call → tool_calls (e.g. search_emails, get_thread_history)
        │       │
        │       ├─ execute search_emails("vendor list")    → email results
        │       ├─ execute get_thread_history("vendor")    → full thread (Mon→Tue→Wed shift)
        │       ├─ execute calculate_deadline_urgency("Wednesday")  → "Due in 2 days"
        │       └─ ... (up to 8 tool calls across iterations)
        │
        ├─ Iteration 2: LLM call (with tool results) → more tool_calls or final response
        │
        └─ Final: LLM produces structured brief text (no tool_calls)
                │
                ▼
        SSE stream → frontend renders markdown brief
        Reasoning trace shows every tool call in collapsible panel
```

## Data Flow — Follow-up Q&A

```
User types "What did I promise Raghav?"
        │
        ▼
POST /api/chat { message }
        │
        ▼
MainAgent.chat()
        │
        ├─ builds messages: system + conversation_history + new user message
        │   (source context NOT re-sent — cost optimization)
        │
        ├─ Agentic loop → tool calls as needed
        │
        └─ Returns answer with source attribution
```

## Data Flow — Validation

```
User clicks "Validate" on a response
        │
        ▼
POST /api/validate { content: "<response text>" }
        │
        ▼
ValidatorAgent.validate()
        │
        ├─ Single LLM call: system_prompt + full source data + response to validate
        │
        └─ Returns structured report:
               VERDICT: PASS | FAIL | PARTIAL
               GROUNDED_ITEMS: list
               ISSUES: list (hallucinations, wrong dates, wrong owners)
               MISSING_ITEMS: list
               SUMMARY: paragraph
```

## Deduplication Logic

The agent uses the `get_thread_history` tool to fetch the full email thread for any item that might have evolved (e.g. the vendor list deadline). The thread is returned in chronological order, so the model can see:

```
Email 1 (Mon 21 Sep, 09:50): "can you send today?"
Email 2 (Mon 21 Sep, 17:40): "will send first thing tomorrow"
Email 3 (Tue 22 Sep, 09:15): "whenever today works"
Email 4 (Tue 22 Sep, 18:30): "will send by tomorrow (Wednesday) morning for sure"
Email 5 (Wed 23 Sep, 08:45): "still good for this morning?"
```

The model surfaces the **most recent agreed deadline** (Wednesday morning) and notes the history as context.

## Cost Optimization

1. Source context is injected only once (first message in a session)
2. Follow-up questions use conversation history only — no re-sending 3,000-token source blob
3. Max 8 agentic iterations per request to cap runaway loops
4. `calculate_deadline_urgency` is a pure Python function — no LLM call needed for date math
5. `search_*` tools filter before sending to LLM — only relevant snippets go back

## Security & Reliability

- Bad/missing input: all tools return descriptive error strings (no crashes, no exceptions bubbling to the user)
- Invalid dates: `calculate_deadline_urgency` returns a clear "Could not parse" message
- Empty queries: FastAPI validates request bodies via Pydantic before reaching agent logic
- API failures: the agentic loop catches Groq exceptions and yields an `error` event that the frontend displays gracefully
