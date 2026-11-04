"""V3.1: the owner's input becomes a job. Input is a topic line, or a Trend Radar Content Package: the JSON from
`GET /api/admin/content-package`, or the Markdown Trend Radar renders from it."""

import json
import re

from sqlalchemy.orm import Session

from studio.db import FORMATS, Fact, Job, engine

DEFAULT_SECONDS = {"radar_report": 50, "make_this_now": 40, "myth_or_real": 40, "weekly_recap": 75}
PACKAGE_FORMATS = {"daily_radar": "radar_report"}  # Trend Radar's format name -> ours
MAX_TOPIC = 300
_ROW = re.compile(r"^\|(.+)\|\s*$", re.M)


def _cells(md: str) -> list[list[str]]:
    return [[c.strip() for c in m.split("|")] for m in _ROW.findall(md)]


def _from_markdown(md: str) -> dict:
    """Pull what the Studio needs out of Trend Radar's package Markdown: ids, format, length, facts, script draft."""
    rows = _cells(md)
    meta = {r[0]: r[1].strip("`") for r in rows if len(r) == 2}
    facts = [dict(zip(("id", "type", "label", "value", "source"), r)) for r in rows
             if len(r) == 5 and re.fullmatch(r"F\d+", r[0])]
    script = re.search(r"^\*\*Script\*\*.*\n((?:>.*\n?)+)", md, re.M)
    seconds = re.match(r"\d+", meta.get("target length", ""))
    return {"package_id": meta.get("package_id"), "format": meta.get("format"),
            "target_length_seconds": int(seconds[0]) if seconds else None,
            "status": meta.get("status", "").strip("*"), "facts": facts,
            "script": "\n".join(l[2:] for l in script[1].splitlines()) if script else None}


def parse(raw: str) -> tuple[str, dict]:
    """-> (input_kind, input). Raises ValueError with a reason the admin page can show."""
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except ValueError:
        data = _from_markdown(raw) if "| package_id |" in raw else None
    if isinstance(data, dict) and "facts" in data:
        if not data["facts"]:
            raise ValueError("Content Package has no facts")
        for f in data["facts"]:
            if not all(f.get(k) for k in ("id", "type", "label", "value", "source")):
                raise ValueError(f"Content Package fact is incomplete: {f}")
        return "package", data
    if not raw:
        raise ValueError("Type a topic or paste a Content Package")
    if len(raw) > MAX_TOPIC or "\n" in raw:
        raise ValueError(f"A topic is one line of at most {MAX_TOPIC} characters (or paste a whole Content Package)")
    return "topic", {"topic": raw}


def facts_of(kind: str, data: dict) -> list[dict]:
    """Package facts: `verified` stays verified, word for word. Trend Radar's `official` facts (primary-source URL)
    are stored as cited `unverified-context`."""
    # ponytail: official facts lose number-on-screen rights here; add an 'official' fact kind if a script needs them.
    if kind != "package":
        return []
    return [{"kind": "verified", "text": f"{f['label']}: {f['value']}"} if f["type"] == "verified" else
            {"kind": "unverified-context", "text": f"{f['label']}: {f['value']}", "source_url": f["source"]}
            for f in data["facts"]]


def create_job(raw: str, format: str | None = None, target_seconds: int | None = None) -> Job:
    kind, data = parse(raw)
    fmt = format or PACKAGE_FORMATS.get(data.get("format"), "radar_report")
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format {fmt!r}; pick one of {', '.join(FORMATS)}")
    seconds = target_seconds or data.get("target_length_seconds") or DEFAULT_SECONDS[fmt]
    with Session(engine, expire_on_commit=False) as s, s.begin():
        job = Job(input_kind=kind, input=data, format=fmt, target_seconds=seconds)
        s.add(job)
        s.flush()
        s.add_all(Fact(job_id=job.id, **f) for f in facts_of(kind, data))
        s.refresh(job)  # load server defaults (status)
    return job
