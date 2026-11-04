"""V3.3: the script. Your headless Claude Code drafts timed scenes, and `validate` enforces the hard rules: the
narrative arc, numbers only from verified facts, the character on screen at the start and end, our data on screen,
and titles unlike the last 7 videos. A failed draft goes back with its problems, at most 3 tries in all.
Run on the host: `uv run python -m studio.script <job_id>`."""

import json
import re
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from studio import llm
from studio.config import CHARACTER_NAME, OPENER, SIGNOFF
from studio.db import Fact, Job, Script, engine

WORDS_PER_SECOND = 2.9  # the hype voice, ~175 wpm (docs/CHARACTER.md §10)
PAUSE = 0.3  # seconds between scenes
PARTS = ("hook", "what", "why", "next")
SHOTS = ("desk", "card", "headline")
POSES = ("talk", "shocked", "laughing", "thinking", "celebrating")
TRIES = 3
SIMILAR = 0.75  # difflib ratio at which a title counts as a repeat
NUMBER = re.compile(r"(?<![A-Za-z0-9.])\d+(?:[.,]\d+)*")
NUMBER_WORDS = re.compile(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
                          r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
                          r"hundred|thousand|million|billion|twice|thrice|triple)\b", re.I)

FORMATS = {
    "radar_report": "Radar Report: today's top trends (up to 3) from the Trend Radar data, each with a data card. "
                    "Catchphrase you may use: \"Fetching the data…\"",
    "make_this_now": "Make This Now: one opportunity for creators and why it's hot right now. "
                     "Catchphrase you may use: \"This one's a loot drop for creators.\"",
    "myth_or_real": "Myth or Real?: one viral claim checked against our data and the cited notes. Say \"Let me "
                    "fact-check that.\" and end the check with \"Real. Receipts below.\", \"Myth. Nerfed by the data.\" "
                    "or, if the sources don't settle it, \"Not confirmed yet.\"",
    "weekly_recap": "Weekly Recap: the biggest moves of the week. Catchphrase you may use: \"Patch notes for the internet.\"",
}

SCENE = {"type": "object", "required": ["part", "shot", "line"], "properties": {
    "part": {"enum": list(PARTS)}, "shot": {"enum": list(SHOTS)}, "pose": {"enum": list(POSES)},
    "line": {"type": "string"}, "text": {"type": "string"},
    "fact_ids": {"type": "array", "items": {"type": "string"}}, "note_ids": {"type": "array", "items": {"type": "string"}}}}
SCHEMA = {"type": "object", "required": ["titles", "thumbnail_text", "scenes"], "properties": {
    "titles": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 3},
    "thumbnail_text": {"type": "string"}, "scenes": {"type": "array", "items": SCENE}}}


def _num(s: str) -> str:
    try:
        return format(Decimal(s.replace(",", "")).normalize(), "f")  # "70", never "7E+1"
    except InvalidOperation:
        return s


def numbers(text: str) -> set[str]:
    return {_num(n) for n in NUMBER.findall(text)}


def words(text: str) -> int:
    return len(text.split())


def context(job_id: int) -> dict:
    """Everything the prompt and the validator need about a job."""
    with Session(engine) as s:
        job = s.get(Job, job_id)
        facts = s.scalars(select(Fact).where(Fact.job_id == job_id).order_by(Fact.id)).all()
        latest = select(Script.job_id, func.max(Script.version).label("v")).where(Script.job_id != job_id) \
            .group_by(Script.job_id).order_by(Script.job_id.desc()).limit(7).subquery()
        bodies = s.scalars(select(Script.body).join(latest, (Script.job_id == latest.c.job_id) &
                                                    (Script.version == latest.c.v))).all()
    pkg = job.input if job.input_kind == "package" else {}
    verified = {f["id"]: f"{f['label']}: {f['value']}" for f in pkg.get("facts", []) if f["type"] == "verified"}
    notes = {f"N{i}": (f.text, f.source_url) for i, f in enumerate((f for f in facts if f.kind == "unverified-context"), 1)}
    day = date.fromisoformat(pkg["brief_date"]) if pkg.get("brief_date") else date.today()
    allowed = set().union(*map(numbers, verified.values()), numbers(job.input.get("topic", "")),
                          {str(day.day), str(day.year), str(len(pkg.get("segments", [])) or 1)})
    return {"job": job, "verified": verified, "notes": notes, "allowed": allowed, "day": day,
            "previous": [t for b in bodies for t in b["titles"]] + pkg.get("previous_titles", []),
            "previous_thumbs": [b["thumbnail_text"] for b in bodies]}


def prompt(ctx: dict) -> str:
    job, pkg = ctx["job"], ctx["job"].input
    budget = round(job.target_seconds * WORDS_PER_SECOND) - words(OPENER) - words(SIGNOFF)
    facts = "\n".join(f"- {i}: {t}" for i, t in ctx["verified"].items()) or "- none (a topic, not a Trend Radar package)"
    notes = "\n".join(f"- {i}: {t} ({u})" for i, (t, u) in ctx["notes"].items()) or "- none"
    moves = "\n".join(f"- {x['topic']['name']}: {x['movement']}" for s in pkg.get("segments", []) for x in s["topics"])
    draft = (pkg.get("script") or "").replace(pkg.get("host") or "\0", CHARACTER_NAME)
    return f"""You write the script for one vertical gaming-news short ({job.target_seconds} seconds, about {budget} \
spoken words in total) hosted by {CHARACTER_NAME}, a cartoon AI news reporter in a headset at a news desk. \
Date: {ctx['day']:%B} {ctx['day'].day}, {ctx['day'].year}.

{"Topic: " + pkg["topic"] if job.input_kind == "topic" else "Source: today's Trend Radar Content Package."}
Format: {FORMATS[job.format]}

{CHARACTER_NAME}'s voice: hyped but honest, quick self-aware jokes (at most one pun), light gamer slang (GG, W/L, \
patch notes, buff/nerf, meta), never mean or toxic, news-anchor energy. Says "not confirmed yet" when that's the truth.

Verified facts (Trend Radar data; use them word for word):
{facts}
{"Rank movement (say it exactly like this):" + chr(10) + moves if moves else ""}

Research notes (cited context: attribute them, e.g. "Destructoid reports…"; never use their numbers):
{notes}

{"Trend Radar's draft (keep its facts and framing; rewrite it in " + CHARACTER_NAME + "'s voice):" + chr(10) + draft if draft else ""}

Structure: scenes in arc order. "part" is hook, then what (what's happening), then why (why it matters), then next \
(what to watch next). The first scene is the hook: one punchy line of at most 10 words, shot "desk". The last scene \
is shot "desk". Don't write a greeting or a sign-off: they are added for you.
Shots:
- "desk": {CHARACTER_NAME} on camera, with a "pose" ({", ".join(POSES)}). Use 2 to 4 desk scenes.
- "card": voice-over on a data card showing "fact_ids" (verified) and/or "note_ids" (notes). At least one card. Optional "text": the card's title.
- "headline": voice-over on a big animated headline in "text".
On-screen "text" is at most 6 words (it must be readable on a phone).

Hard rules (a program checks them):
- Every number is written in digits and comes from the verified facts. No other numbers, no spelled-out numbers \
(two, twice, hundred…), no rounding.
- No "breaking", "leaked", "confirmed", "cancelled", "insider" or fake urgency. No rumours.
- Nothing about finance, investing, money-making, health, medical or legal matters.
- 3 titles (under 70 characters, no all-caps words) and a thumbnail_text of at most 5 words, each different from \
these previous ones: {"; ".join(ctx["previous"] + ctx["previous_thumbs"]) or "none yet"}."""


def similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= SIMILAR


def validate(script: dict, ctx: dict) -> list[str]:
    errors = []
    scenes = script.get("scenes", [])
    if not scenes:
        return ["no scenes"]
    parts = [s["part"] for s in scenes]
    if missing := [p for p in PARTS if p not in parts]:
        errors.append(f"narrative arc is missing: {', '.join(missing)}")
    if [PARTS.index(p) for p in parts] != sorted(PARTS.index(p) for p in parts):
        errors.append(f"parts are out of arc order (hook → what → why → next): {' → '.join(parts)}")
    if parts[0] != "hook" or scenes[0]["shot"] != "desk":
        errors.append("the first scene must be the hook, on the desk shot")
    if words(scenes[0]["line"]) > 10:
        errors.append(f"the hook has {words(scenes[0]['line'])} words; at most 10")
    if scenes[-1]["shot"] != "desk":
        errors.append(f"the last scene must be on the desk shot ({CHARACTER_NAME} on screen at the end)")
    if not any(s["shot"] == "card" for s in scenes):
        errors.append("no data card: our data must be on screen at least once")
    for i, s in enumerate(scenes, 1):
        if bad := [f for f in s.get("fact_ids", []) if f not in ctx["verified"]]:
            errors.append(f"scene {i} cites unknown facts {bad}")
        if bad := [n for n in s.get("note_ids", []) if n not in ctx["notes"]]:
            errors.append(f"scene {i} cites unknown notes {bad}")
        if s["shot"] == "card" and not (s.get("fact_ids") or s.get("note_ids")):
            errors.append(f"scene {i} is a card with nothing on it")
        if s["shot"] == "headline" and not s.get("text", "").strip():
            errors.append(f"scene {i} is a headline with no text")
        if words(s.get("text", "")) > 6:
            errors.append(f"scene {i} on-screen text has {words(s['text'])} words; at most 6 (readable on a phone)")
    titles, thumb = script.get("titles", []), script.get("thumbnail_text", "")
    texts = [s["line"] for s in scenes] + [s.get("text", "") for s in scenes] + titles + [thumb]
    if invented := sorted(set().union(*map(numbers, texts)) - ctx["allowed"]):
        errors.append(f"numbers not in the verified facts: {', '.join(invented)}")
    if spelled := sorted({m.lower() for t in texts for m in NUMBER_WORDS.findall(t)}):
        errors.append(f"spelled-out numbers: {', '.join(spelled)} (use digits from the verified facts, or drop them)")
    if len(titles) != 3 or any(len(t) > 70 for t in titles):
        errors.append("need exactly 3 titles under 70 characters")
    for t in titles:
        if p := next((p for p in ctx["previous"] if similar(t, p)), None):
            errors.append(f"title {t!r} is too close to a recent one: {p!r}")
    if not 0 < words(thumb) <= 5:
        errors.append("thumbnail_text must be 1 to 5 words")
    elif p := next((p for p in ctx["previous_thumbs"] if similar(thumb, p)), None):
        errors.append(f"thumbnail text {thumb!r} is too close to a recent one: {p!r}")
    target = ctx["job"].target_seconds
    secs = estimate(scenes)
    if not 0.75 * target <= secs <= 1.15 * target:
        errors.append(f"about {secs:.0f} s of speech; the target is {target} s ({round(target * WORDS_PER_SECOND)} words)")
    return errors


def estimate(scenes: list[dict]) -> float:
    return sum(words(s["line"]) / WORDS_PER_SECOND + PAUSE for s in scenes) + \
        (words(OPENER) + words(SIGNOFF)) / WORDS_PER_SECOND + 2 * PAUSE


def finish(script: dict) -> dict:
    """Add the opener after the hook and the sign-off at the end, and time every scene."""
    scenes = script["scenes"]
    scenes = [scenes[0], {"part": "hook", "shot": "desk", "pose": "talk", "line": OPENER}, *scenes[1:],
              {"part": "next", "shot": "desk", "pose": "talk", "line": SIGNOFF}]
    for s in scenes:
        s["est_seconds"] = round(words(s["line"]) / WORDS_PER_SECOND + PAUSE, 1)
    return {**script, "scenes": scenes, "est_seconds": round(sum(s["est_seconds"] for s in scenes), 1)}


class ScriptInvalid(ValueError):
    pass


def write(job_id: int) -> dict:
    """Draft, validate (at most TRIES drafts) and store a new script version. Raises ScriptInvalid with the reasons."""
    ctx = context(job_id)
    p = base = prompt(ctx)
    for attempt in range(1, TRIES + 1):
        script = llm.ask(p, SCHEMA, job_id=job_id, step=f"script try {attempt}")
        if not (errors := validate(script, ctx)):
            break
        p = (f"{base}\n\nYour previous draft broke these rules:\n" + "\n".join(f"- {e}" for e in errors) +
             f"\n\nPrevious draft:\n{json.dumps(script)}\n\nReturn a corrected script.")
    else:
        raise ScriptInvalid(f"script failed validation after {TRIES} tries: " + "; ".join(errors))
    body = finish(script)
    with Session(engine) as s, s.begin():
        version = (s.scalar(select(func.max(Script.version)).where(Script.job_id == job_id)) or 0) + 1
        s.add(Script(job_id=job_id, version=version, body=body))
    return body


if __name__ == "__main__":
    body = write(int(sys.argv[1]))
    print(" | ".join(body["titles"]), f"· thumbnail: {body['thumbnail_text']} · ~{body['est_seconds']} s")
    for s in body["scenes"]:
        cue = s.get("pose") or s.get("text") or ", ".join(s.get("fact_ids", []) + s.get("note_ids", []))
        print(f"[{s['part']:4} {s['shot']:8} {cue}] {s['line']}")
