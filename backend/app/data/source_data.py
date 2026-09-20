"""
Source data for Arjun Malhotra's week of 21-25 September 2026.
All data is embedded here as structured Python objects — parsed once, never re-fetched.
"""

WEEK_START = "2026-09-21"
WEEK_END = "2026-09-25"
CURRENT_DATE = "2026-09-21"  # Monday — will be overridden at runtime

PEOPLE = {
    "arjun": {"name": "Arjun Malhotra", "role": "VP Sales", "email": "arjun.malhotra@veridian-corp.example"},
    "neha": {"name": "Neha Kapoor", "role": "Marketing Lead", "email": "neha.kapoor@veridian-corp.example"},
    "raghav": {"name": "Raghav Sethi", "role": "Ops Manager", "email": "raghav.sethi@veridian-corp.example"},
    "divya": {"name": "Divya Rao", "role": "Finance", "email": "divya.rao@veridian-corp.example"},
    "priya": {"name": "Priya Nair", "role": "Meridian Logistics (external client)", "email": "priya.nair@meridianlogistics.example"},
    "facilities": {"name": "Facilities", "role": "Internal distribution list", "email": "facilities@veridian-corp.example"},
}

MEETING_TRANSCRIPT = """
Meeting: Leadership Sync
Date: Monday 21 September 2026, 9:00–9:35 AM
Attendees: Arjun Malhotra, Neha Kapoor, Raghav Sethi, Divya Rao

Arjun: Let's keep this quick. Neha, where are we on the Q3 campaign deck?
Neha: Draft is 80% done. I'll send it to Arjun for review by Wednesday.
Arjun: Good. Also, remind me — I told Raghav I'd send him the updated vendor list. I'll get that to him by end of day tomorrow.
Raghav: Appreciated. Separately, the Mumbai office renewal paperwork needs someone to sign off this week. Not sure whose desk that's on right now.
Divya: I think that's supposed to be Facilities, but I haven't seen anyone pick it up.
Arjun: Okay, flag it, don't assume. Divya, can you also pull the July expense variance report before Thursday's board prep?
Divya: Yes, I'll have it ready Wednesday evening.
Arjun: One more thing — client call with Meridian Logistics got pushed. I need to reconfirm the new time with their team myself.
Neha: Also, just a reminder, the campaign deck review — I said Wednesday, but realistically Thursday morning is safer.
Arjun: Noted. Let's close here.
"""

CALENDARS = {
    "arjun": [
        {"date": "2026-09-21", "start": "09:00", "end": "09:35", "title": "Leadership Sync"},
        {"date": "2026-09-21", "start": "14:00", "end": "14:30", "title": "1:1 with Neha"},
        {"date": "2026-09-21", "start": "16:00", "end": "17:00", "title": "Blocked"},
        {"date": "2026-09-22", "start": "11:00", "end": "12:00", "title": "Internal Budget Review"},
        {"date": "2026-09-22", "start": "15:00", "end": "15:30", "title": "Blocked"},
        {"date": "2026-09-23", "start": "15:00", "end": "15:30", "title": "Call — Meridian Logistics"},
        {"date": "2026-09-23", "start": "18:00", "end": "18:15", "title": "Blocked"},
        {"date": "2026-09-24", "start": "09:00", "end": "10:00", "title": "Board Prep Session"},
        {"date": "2026-09-24", "start": "16:00", "end": "17:00", "title": "Hiring Panel — Sales Associate"},
        {"date": "2026-09-25", "start": "10:00", "end": "10:30", "title": "Facilities Check-in"},
        {"date": "2026-09-25", "start": "13:00", "end": "14:00", "title": "Blocked"},
    ],
    "neha": [
        {"date": "2026-09-21", "start": "10:00", "end": "11:00", "title": "Blocked"},
        {"date": "2026-09-21", "start": "14:00", "end": "14:30", "title": "1:1 with Arjun"},
        {"date": "2026-09-22", "start": "13:00", "end": "14:00", "title": "Campaign Vendor Call"},
        {"date": "2026-09-23", "start": "10:00", "end": "10:30", "title": "Deck Prep"},
        {"date": "2026-09-23", "start": "13:00", "end": "15:00", "title": "Blocked"},
        {"date": "2026-09-24", "start": "09:30", "end": "10:00", "title": "Deck Review with Arjun"},
        {"date": "2026-09-25", "start": "11:00", "end": "12:00", "title": "Blocked"},
    ],
    "raghav": [
        {"date": "2026-09-21", "start": "09:00", "end": "09:35", "title": "Leadership Sync"},
        {"date": "2026-09-21", "start": "13:00", "end": "14:00", "title": "Blocked"},
        {"date": "2026-09-22", "start": "11:00", "end": "12:00", "title": "Internal Budget Review"},
        {"date": "2026-09-22", "start": "15:30", "end": "16:00", "title": "Ops Standup"},
        {"date": "2026-09-23", "start": "09:00", "end": "11:00", "title": "Blocked"},
        {"date": "2026-09-24", "start": "14:00", "end": "15:00", "title": "Blocked"},
        {"date": "2026-09-25", "start": "10:00", "end": "10:30", "title": "Facilities Check-in"},
        {"date": "2026-09-25", "start": "15:00", "end": "16:00", "title": "Blocked"},
    ],
    "divya": [
        {"date": "2026-09-21", "start": "14:30", "end": "15:00", "title": "Budget Prep"},
        {"date": "2026-09-21", "start": "16:00", "end": "17:00", "title": "Blocked"},
        {"date": "2026-09-22", "start": "09:00", "end": "09:15", "title": "Quick Call with Arjun"},
        {"date": "2026-09-22", "start": "11:00", "end": "12:00", "title": "Internal Budget Review"},
        {"date": "2026-09-23", "start": "13:00", "end": "14:00", "title": "Blocked"},
        {"date": "2026-09-24", "start": "09:00", "end": "10:00", "title": "Board Prep Session"},
        {"date": "2026-09-24", "start": "14:00", "end": "15:00", "title": "Blocked"},
        {"date": "2026-09-25", "start": "10:00", "end": "11:00", "title": "Blocked"},
    ],
}

EMAIL_THREADS = [
    {
        "subject": "Vendor List",
        "emails": [
            {"date": "2026-09-21", "time": "09:50", "from": "raghav.sethi@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Following up from the sync — can you send the updated vendor list today?"},
            {"date": "2026-09-21", "time": "17:40", "from": "arjun.malhotra@veridian-corp.example", "to": "raghav.sethi@veridian-corp.example", "body": "Running behind, will send first thing tomorrow morning instead."},
            {"date": "2026-09-22", "time": "09:15", "from": "raghav.sethi@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "No worries, whenever you get a chance today works."},
            {"date": "2026-09-22", "time": "18:30", "from": "arjun.malhotra@veridian-corp.example", "to": "raghav.sethi@veridian-corp.example", "body": "Sorry, got pulled into board prep — will send by tomorrow (Wednesday) morning for sure."},
            {"date": "2026-09-23", "time": "08:45", "from": "raghav.sethi@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Just checking — still good for this morning?"},
        ]
    },
    {
        "subject": "Q3 Campaign Deck",
        "emails": [
            {"date": "2026-09-21", "time": "11:00", "from": "neha.kapoor@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Deck's coming together, still targeting Wednesday for your review."},
            {"date": "2026-09-22", "time": "16:15", "from": "neha.kapoor@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Heads up — shifting the review to Thursday morning instead of Wednesday, need one more day on the data slides."},
            {"date": "2026-09-23", "time": "10:00", "from": "arjun.malhotra@veridian-corp.example", "to": "neha.kapoor@veridian-corp.example", "body": "Understood, Thursday morning works. What time exactly?"},
            {"date": "2026-09-23", "time": "10:20", "from": "neha.kapoor@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Let's say 9:30 AM Thursday, before your board prep block."},
            {"date": "2026-09-24", "time": "08:00", "from": "neha.kapoor@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Deck is ready, attaching the draft ahead of our 9:30 review."},
        ]
    },
    {
        "subject": "Call Reschedule — Meridian Logistics",
        "emails": [
            {"date": "2026-09-21", "time": "13:00", "from": "priya.nair@meridianlogistics.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Our scheduled call this week got bumped from our side — can you propose a new time? We're flexible Tuesday–Thursday afternoons."},
            {"date": "2026-09-22", "time": "15:00", "from": "arjun.malhotra@veridian-corp.example", "to": "priya.nair@meridianlogistics.example", "body": "Apologies for the delay — how about Wednesday 3:00 PM?"},
            {"date": "2026-09-22", "time": "17:45", "from": "priya.nair@meridianlogistics.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Wednesday 3 PM works on our end, confirmed."},
            {"date": "2026-09-23", "time": "13:30", "from": "priya.nair@meridianlogistics.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Quick check — still on for 3 PM today?"},
            {"date": "2026-09-23", "time": "14:00", "from": "arjun.malhotra@veridian-corp.example", "to": "priya.nair@meridianlogistics.example", "body": "Yes, confirmed, see you at 3."},
        ]
    },
    {
        "subject": "Expense Variance Report",
        "emails": [
            {"date": "2026-09-21", "time": "14:30", "from": "divya.rao@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Starting on the July variance numbers, targeting Thursday morning for board prep as discussed."},
            {"date": "2026-09-22", "time": "09:00", "from": "arjun.malhotra@veridian-corp.example", "to": "divya.rao@veridian-corp.example", "body": "Actually, can I get it by Wednesday evening instead? Want time to review before Thursday."},
            {"date": "2026-09-22", "time": "09:40", "from": "divya.rao@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Wednesday evening is tight but doable, I'll prioritize it."},
            {"date": "2026-09-23", "time": "18:00", "from": "divya.rao@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "Report attached, sent as promised."},
            {"date": "2026-09-23", "time": "18:10", "from": "arjun.malhotra@veridian-corp.example", "to": "divya.rao@veridian-corp.example", "body": "Got it, thank you — exactly what I needed before tomorrow."},
        ]
    },
    {
        "subject": "Mumbai Office Lease Renewal",
        "emails": [
            {"date": "2026-09-21", "time": "10:15", "from": "facilities@veridian-corp.example", "to": "All Staff", "body": "Reminder: the Mumbai office lease renewal requires an authorized signature by Friday, 25 September."},
            {"date": "2026-09-22", "time": "11:00", "from": "raghav.sethi@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example,divya.rao@veridian-corp.example", "body": "Following up from the sync — has anyone confirmed who's signing off on the Mumbai renewal? Don't think it's been assigned."},
            {"date": "2026-09-23", "time": "09:30", "from": "divya.rao@veridian-corp.example", "to": "raghav.sethi@veridian-corp.example,arjun.malhotra@veridian-corp.example", "body": "Not on my end — I believe this typically sits with Facilities directly, not us."},
            {"date": "2026-09-24", "time": "16:00", "from": "facilities@veridian-corp.example", "to": "All Staff", "body": "Second reminder: signature is still pending. Deadline is Friday, 25 September, end of day."},
            {"date": "2026-09-24", "time": "16:45", "from": "raghav.sethi@veridian-corp.example", "to": "arjun.malhotra@veridian-corp.example", "body": "This is now one day out and still unowned — can you confirm who's handling it?"},
        ]
    },
]

VOICE_NOTES = [
    {
        "date": "2026-09-21",
        "time": "18:40",
        "recorded_by": "Arjun Malhotra",
        "context": "Recorded in cab",
        "transcript": "Quick note to self — need to get Raghav that vendor list, I think I said today but it might slip to tomorrow morning, remind me. Also still haven't heard back on the Mumbai lease thing, someone needs to own that, I don't think it's me."
    },
    {
        "date": "2026-09-23",
        "time": "08:15",
        "recorded_by": "Arjun Malhotra",
        "context": "Morning reminder",
        "transcript": "Reminder — expense variance report from Divya needs to be in my hands by Wednesday evening, not Thursday, I want time to go through it before board prep. Also Meridian call — I owe Priya a time, need to lock that in today."
    },
]


def get_all_sources_as_text() -> str:
    """Returns all source data as a single formatted text block for LLM context."""
    lines = []

    lines.append("=== MEETING TRANSCRIPT ===")
    lines.append(MEETING_TRANSCRIPT.strip())
    lines.append("")

    lines.append("=== ARJUN'S CALENDAR (Week of 21–25 Sep 2026) ===")
    for entry in CALENDARS["arjun"]:
        lines.append(f"  {entry['date']} {entry['start']}–{entry['end']}: {entry['title']}")
    lines.append("")

    lines.append("=== EMAIL THREADS ===")
    for thread in EMAIL_THREADS:
        lines.append(f"\n--- Thread: {thread['subject']} ---")
        for email in thread["emails"]:
            lines.append(f"  [{email['date']} {email['time']}] From: {email['from']} → To: {email['to']}")
            lines.append(f"  \"{email['body']}\"")
    lines.append("")

    lines.append("=== VOICE NOTES (by Arjun Malhotra, personal memos) ===")
    for note in VOICE_NOTES:
        lines.append(f"\n[{note['date']} {note['time']} — {note['context']}]")
        lines.append(f"  \"{note['transcript']}\"")
    lines.append("")

    return "\n".join(lines)
