# Demo Script — Executive Productivity Agent

This is a walkthrough guide for the demo recording. Follow these steps in order — each step has a talking point and what to show on screen.

---

## Setup (before recording)

```bash
cd projects/executive-agent
./start.sh
# Wait for: "✓ Agent is running at: http://localhost:5173"
```

Open Chrome at `http://localhost:5173`. Make sure the browser window is large enough to show the full UI.

---

## Step 1 — Welcome Screen (30 seconds)

**What to show:** The landing screen with four source cards.

**Talking point:**
> "This agent is built for Arjun Malhotra, VP Sales. Before generating anything, it shows you exactly what data it has access to — a meeting transcript, five email threads, four people's calendars, and two voice notes he recorded to himself. No external data fetching, no black box — every claim the agent makes will trace back to one of these sources."

---

## Step 2 — Generate Daily Brief (90 seconds)

**Click:** "Generate Daily Brief"

**What to show while it runs:**
- The reasoning trace auto-expands — show the live tool calls: `search_emails`, `get_thread_history`, `calculate_deadline_urgency`
- The three bouncing dots in the header show the agent is reasoning

**Talking point while it runs:**
> "You can see the agent using its tools in real time — it's not just reading a summary, it's actively searching email threads to track how deadlines shifted. For example, Arjun promised Raghav the vendor list on Monday, then again on Tuesday, then Wednesday — the agent will surface only the final deadline and note the history."

**Once the brief appears:**
> "The brief is structured into three sections: My Actions — things Arjun personally committed to. Waiting On Others — what he's expecting from his team. And Flagged — anything with unclear ownership or a risk. Every item cites its source."

**Point out specifically:**
- Vendor list: shows Wednesday morning deadline, notes the three-day slip
- Mumbai lease renewal: explicitly FLAGGED as ownership unresolved — "this is the honest answer, not a guess"
- Campaign deck: Thursday 9:30 AM, not Wednesday — because the email thread updated it

---

## Step 3 — Follow-up Q&A / Conversation Memory (60 seconds)

**Click the quick prompt:** "What did I promise Raghav?"

**Talking point:**
> "Now I'm asking a follow-up without re-explaining any context. The agent remembers the full conversation — it knows who Raghav is, what the vendor list is, and what deadline was agreed to. This is proper session memory, not just repeating the brief."

**Click:** "Who owns the Mumbai lease?"

**Talking point:**
> "Notice it doesn't guess. It tells you exactly what the source data says — Facilities was mentioned, nobody confirmed, it's unresolved. That's the anti-hallucination rule in action."

---

## Step 4 — Validator Agent (45 seconds)

**Click:** "Validate" button on the brief message

**What to show:** The validator reasoning trace (it will appear under the message), then the PASS/PARTIAL/FAIL verdict.

**Talking point:**
> "This is the second agent — a fact-checker. It takes the main agent's output and goes through it line by line against the raw source data. It checks for invented facts, wrong dates, misclassified ownership, and anything that was in the source data but got omitted. The PASS/PARTIAL/FAIL verdict tells you how much to trust the output."

---

## Step 5 — Reasoning Trace Inspection (30 seconds)

**Click the reasoning trace** on any message to expand it.

**Talking point:**
> "Every LLM call, every tool invocation, every result is logged. This isn't just a pretty UI — during the demo you can literally show a reviewer which email thread the agent queried and what it found. Full explainability."

**Point to the header:**
> "And here — the LLM call counter. This is cost tracking in real time. The architecture is designed to minimize calls: source context is sent only once, follow-ups use only conversation history."

---

## Step 6 — Reset (15 seconds)

**Click:** "Reset" in the header.

**Talking point:**
> "Reset clears the session entirely — all conversation history, all state. Fresh start. The source data stays loaded because it's embedded in the backend — no re-fetching needed."

---

## Key numbers to mention

| Metric | Value |
|--------|-------|
| Source items processed | 25 emails, 1 meeting transcript, 4 calendars, 2 voice notes |
| Agent tools | 7 callable functions |
| Max LLM iterations per request | 8 (capped for cost) |
| Test coverage | 30 tests, 100% pass |
| One-command startup | `./start.sh` |
| Model | Groq · Qwen 3.8B-27B |

---

## If anything goes wrong during the demo

- **Agent takes too long:** Click Stop (the red square button). The stream cancels cleanly. Then retry.
- **Brief looks wrong:** Click Validate to run the fact-checker immediately.
- **Need a fresh run:** Click Reset, then Generate Daily Brief again.
- **Backend not responding:** Check that `uvicorn` is running on port 8000 (`curl http://localhost:8000/` should return JSON).
