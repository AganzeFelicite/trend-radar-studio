"""V3.4: the safety gate. `gate` stops a job on a sensitive topic (finance, investing, money-making, health, medical,
legal): the blocklist first, then an AI classifier, and the job is `blocked` with the reason. `sensational` is part
of the script validator: no rumours, leaks or fake urgency, and "confirmed"/"cancelled" only with a cited note.
Run on the host: `uv run python -m studio.safety <job_id>`."""

import re
import sys

from sqlalchemy.orm import Session

from studio import llm
from studio.config import SENSATIONAL_CITED_ONLY, SENSATIONAL_NEVER, SENSITIVE_TOPICS
from studio.db import Job, engine

BLOCKLIST = {c: re.compile(r"\b(" + "|".join(map(re.escape, kws)) + r")s?\b", re.I) for c, kws in SENSITIVE_TOPICS.items()}
NEVER = re.compile(r"\b(" + "|".join(map(re.escape, SENSATIONAL_NEVER)) + r")\b", re.I)
CITED_ONLY = re.compile(r"\b(" + "|".join(SENSATIONAL_CITED_ONLY) + r")\b", re.I)
NEGATED = re.compile(r"(\bnot|n't|\bnever|\bno)\s+(\w+\s+){0,2}?(" + "|".join(SENSATIONAL_CITED_ONLY) + r")\b", re.I)
ALL_CAPS = re.compile(r"\b[A-Z]{5,}\b")  # LEAKED, BREAKING, INSANE; short acronyms (GTA, DLC, NPC) are fine
RULE = "The Studio never covers finance, investing, money-making, health, medical or legal topics."
CLASSIFY = {"type": "object", "required": ["category", "reason"], "properties": {
    "category": {"enum": [*SENSITIVE_TOPICS, "none"]}, "reason": {"type": "string"}}}


class Blocked(Exception):
    pass


def subject(job: Job) -> str:
    if job.input_kind == "topic":
        return job.input["topic"]
    segs = job.input.get("segments") or []
    return "\n".join([f"{s['label']}: {', '.join(s['keywords'])}" for s in segs] +
                     [f["label"] for f in job.input["facts"]])


def blocklist(text: str) -> str | None:
    for category, pattern in BLOCKLIST.items():
        if m := pattern.search(text):
            return f"{category} topic (blocklist: {m[0]!r})"
    return None


def classify(text: str, job_id: int | None = None) -> str | None:
    out = llm.ask(f"""Classify the subject of a short gaming-news video.

Subject:
{text}

Answer "none" unless the video itself would be about {", ".join(SENSITIVE_TOPICS)} matters: for example share prices, \
investing, crypto, making money or side incomes, diets, mental or physical health, medicine, lawsuits or legal \
advice. Ordinary game news (release dates, file sizes, maps, consoles, trailers, game mechanics like health bars) \
is "none". News about a game company is game news too: a publisher's earnings call, a CEO's statement about a \
release date or a game's price, sales figures or a studio announcement are "none" unless the video would advise \
on money or centre on share prices. When a gaming subject is a judgment call, answer "none". Give a one-sentence reason.""", CLASSIFY, job_id=job_id, step="safety classifier")
    return None if out["category"] == "none" else f"{out['category']} topic (AI classifier: {out['reason']})"


def gate(job_id: int) -> None:
    """Raise Blocked (and mark the job `blocked` with the reason) if the job's subject is a sensitive topic."""
    with Session(engine) as s:
        text = subject(s.get(Job, job_id))
    reason = blocklist(text) or classify(text, job_id)  # the classifier runs only if the blocklist passes
    if reason:
        with Session(engine) as s, s.begin():
            job = s.get(Job, job_id)
            job.status, job.error = "blocked", f"Blocked: {reason}. {RULE}"
        raise Blocked(f"Blocked: {reason}. {RULE}")


def _positive(text: str) -> set[str]:
    """Cited-only words used positively ("Rockstar confirmed…"); "not confirmed yet" doesn't count."""
    return {m.lower() for m in CITED_ONLY.findall(NEGATED.sub("", text))}


def sensational(script: dict, notes: dict[str, tuple[str, str]]) -> list[str]:
    errors = []
    for i, s in enumerate(script.get("scenes", []), 1):
        said = f"{s.get('line', '')} {s.get('text', '')}"
        if never := sorted({m.lower() for m in NEVER.findall(said)}):
            errors.append(f"scene {i} says {', '.join(never)}: never allowed (no rumours, leaks or fake urgency)")
        cited = set().union(*(_positive(notes[n][0]) for n in s.get("note_ids", []) if n in notes))
        if unsupported := sorted(_positive(said) - cited):
            errors.append(f"scene {i} says {', '.join(unsupported)} without a cited note saying so in that scene")
        if caps := ALL_CAPS.findall(said):
            errors.append(f"scene {i} has all-caps words: {', '.join(caps)}")
    for t in script.get("titles", []) + [script.get("thumbnail_text", "")]:
        if bad := sorted({m.lower() for m in NEVER.findall(t) + CITED_ONLY.findall(t)} | set(ALL_CAPS.findall(t))):
            errors.append(f"title/thumbnail {t!r} uses {', '.join(bad)}: never in titles or thumbnails")
    return errors


if __name__ == "__main__":
    try:
        gate(int(sys.argv[1]))
        print("passed")
    except Blocked as e:
        print(e)
