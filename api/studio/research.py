"""V3.2: cited research notes for a job, kept apart from the verified facts. Every note needs a reputable source URL
and is stored as `unverified-context`. Run on the host: `uv run python -m studio.research <job_id>`."""

import re
import sys
from datetime import date
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from studio import llm
from studio.config import RESEARCH_BLOCKED_DOMAINS, RESEARCH_EXCLUDE_WORDS, RESEARCH_MAX_SEARCHES
from studio.db import Fact, Job, engine

MAX_NOTES = 8
EXCLUDED = re.compile(RESEARCH_EXCLUDE_WORDS, re.I)
HOMEPAGE = re.compile(r"/?([a-z]{2}(-[a-z]{2})?/?)?", re.I)  # "", "/", "/en-us/"
SCHEMA = {"type": "object", "required": ["notes"], "properties": {"notes": {"type": "array", "items": {
    "type": "object", "required": ["claim", "source_url"],
    "properties": {"claim": {"type": "string"}, "source_url": {"type": "string"}}}}}}


def prompt(job: Job) -> str:
    if job.input_kind == "topic":
        subject = f"Topic: {job.input['topic']}"
    else:
        segs = job.input.get("segments") or []
        subject = "Trend Radar topics today:\n" + "\n".join(
            f"- {s['label']} (people call it: {', '.join(s['keywords'][:8])})" for s in segs) if segs else ""
        subject += "\n\nOur verified data (don't repeat it as notes, never contradict it):\n" + "\n".join(
            f"- {f['label']}: {f['value']}" for f in job.input["facts"])
    return f"""You research a short gaming-news video. Today is {date.today():%B %d, %Y}.

{subject}

Find out what is actually happening and why it matters to gamers and creators. Use at most \
{RESEARCH_MAX_SEARCHES} web searches. Return up to {MAX_NOTES} notes. Each note is one plain sentence (under 200 \
characters) with the URL of the exact article or page that says it (never a homepage).

Rules:
- Sources: official publisher, platform or store pages first, then established gaming or tech news outlets. Never \
YouTube, TikTok, Twitch, Reddit, X/Twitter, Facebook, Instagram, Discord, forums, wikis or fan sites.
- Only what the source actually says. No rumours, leaks, insider claims, dataminers, piracy, jailbreaks or cheats.
- Nothing about finance, investing, money-making, health, medical or legal matters.
- If you can't find a reputable source for something, leave it out."""


def keep(note: dict) -> str | None:
    """None if the note may be used, else why it was dropped."""
    url = note.get("source_url", "").strip()
    host = (urlparse(url).hostname or "").removeprefix("www.")
    if urlparse(url).scheme not in ("http", "https") or not host:
        return "no source URL"
    if any(host == d or host.endswith("." + d) for d in RESEARCH_BLOCKED_DOMAINS):
        return f"not a reputable source ({host})"
    if HOMEPAGE.fullmatch(urlparse(url).path):
        return "homepage, not the page that says it"
    if EXCLUDED.search(note.get("claim", "")):
        return "rumour/leak/piracy wording"
    if not note.get("claim", "").strip():
        return "empty claim"
    return None


def research(job_id: int) -> tuple[list[dict], list[tuple[dict, str]]]:
    """-> (kept notes, dropped notes with reasons). Kept notes are stored as `unverified-context` facts."""
    with Session(engine) as s:
        p = prompt(s.get(Job, job_id))
    # no DB transaction stays open while Claude Code works (minutes)
    notes = llm.ask(p, SCHEMA, tools="WebSearch,WebFetch", max_turns=RESEARCH_MAX_SEARCHES + 6, job_id=job_id,
                    step="research")["notes"]
    kept, dropped = [], []
    for n in notes[:MAX_NOTES]:
        if why := keep(n):
            dropped.append((n, why))
        else:
            kept.append(n)
    with Session(engine) as s, s.begin():
        s.add_all(Fact(job_id=job_id, kind="unverified-context", text=n["claim"].strip(),
                       source_url=n["source_url"].strip()) for n in kept)
    return kept, dropped


if __name__ == "__main__":
    kept, dropped = research(int(sys.argv[1]))
    for n in kept:
        print(f"+ {n['claim']}\n    {n['source_url']}")
    for n, why in dropped:
        print(f"- DROPPED ({why}): {n.get('claim')}\n    {n.get('source_url')}")
