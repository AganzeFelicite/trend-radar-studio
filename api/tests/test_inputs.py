"""V3.1: topic text and Trend Radar Content Packages (JSON and Markdown) become jobs with their facts."""

import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from studio.db import Fact, engine
from studio.inputs import create_job, parse

FIXTURES = Path(__file__).parent / "fixtures"  # trimmed real package; package.md rendered by Trend Radar's markdown()
PKG_JSON = (FIXTURES / "package.json").read_text()
PKG_MD = (FIXTURES / "package.md").read_text()


def facts(job_id: int) -> list[tuple]:
    with Session(engine) as s:
        return [(f.kind, f.text, f.source_url) for f in s.scalars(select(Fact).where(Fact.job_id == job_id).order_by(Fact.id))]


def test_topic():
    job = create_job("  GTA 6 pre-load starts next week  ", format="make_this_now")
    assert (job.input_kind, job.input, job.format, job.target_seconds, job.status) == (
        "topic", {"topic": "GTA 6 pre-load starts next week"}, "make_this_now", 40, "queued")
    assert facts(job.id) == []


@pytest.mark.parametrize("raw", [PKG_JSON, PKG_MD], ids=["json", "markdown"])
def test_package(raw):
    job = create_job(raw)
    assert (job.input_kind, job.format, job.target_seconds) == ("package", "radar_report", 40)
    assert job.input["package_id"] == "2026-11-04-daily_radar-en-v5"
    assert job.input["script"].startswith("HOOK: ") and "\n\nWHAT THE DATA SHOWS: " in job.input["script"]
    got = facts(job.id)
    assert len(got) == 7
    assert got[0] == ("verified", "Pre-load: rank: #1", None)
    assert got[3] == ("verified", "Pre-load: share of the GTA 6 conversation, 24h: 11.5%", None)  # word for word
    assert got[6] == ("unverified-context", "Pre-load start date: November 10", "https://www.rockstargames.com/newswire/example")


def test_markdown_matches_json():
    j, m = parse(PKG_JSON)[1], parse(PKG_MD)[1]
    assert m["facts"] == j["facts"]
    assert (m["script"], m["status"]) == (j["script"], j["status"])


@pytest.mark.parametrize("raw, reason", [
    ("   ", "Type a topic"),
    ("line one\nline two", "one line"),
    ("x" * 301, "one line"),
    (json.dumps({"facts": []}), "no facts"),
    (json.dumps({"facts": [{"id": "F1", "type": "verified", "label": "rank"}]}), "incomplete"),
])
def test_rejected(raw, reason):
    with pytest.raises(ValueError, match=reason):
        parse(raw)


def test_unknown_format():
    with pytest.raises(ValueError, match="Unknown format"):
        create_job("a topic", format="vlog")
