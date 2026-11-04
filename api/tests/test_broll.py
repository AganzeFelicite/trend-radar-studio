"""V3.7/V3.8: B-roll and data cards from our own graphics; facts shown exactly; render refused without a licence."""

import json
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from studio import broll
from studio.db import Asset, Unlicensed, engine, ensure_licensed
from studio.inputs import create_job

PKG = (Path(__file__).parent / "fixtures" / "package.json").read_text()
FACTS = {"F1": {"id": "F1", "type": "verified", "label": "Pre-load: rank", "value": "#1"},
         "F4": {"id": "F4", "type": "verified", "label": "Pre-load: share of the GTA 6 conversation, 24h", "value": "11.5%"}}
NOTES = {"N1": ("Destructoid gives the size as 212 GB, unconfirmed.", "https://www.destructoid.com/gta-6-size/")}


def test_card_shows_facts_exactly_and_sources_without_numbers():
    p = broll.scene_props({"shot": "card", "fact_ids": ["F1", "F4"], "note_ids": ["N1"], "start": 1.0, "end": 4.5},
                          FACTS, NOTES, "2026-11-04 09:00 UTC")
    assert p["rows"] == [{"topic": "Pre-load", "metric": "rank", "value": "#1"},
                         {"topic": "Pre-load", "metric": "share of the GTA 6 conversation, 24h", "value": "11.5%"}]
    assert p["sources"] == ["destructoid.com"] and "212" not in json.dumps(p)  # the note's number never reaches the card
    assert (p["kind"], p["title"], p["footer"], p["duration"]) == ("card", "Pre-load", "Data: Trend Radar · 2026-11-04 09:00 UTC", 3.8)


def test_headline_and_note_only_card():
    h = broll.scene_props({"shot": "headline", "text": "Your queue matters", "start": 0, "end": 2}, FACTS, NOTES, None)
    assert (h["kind"], h["title"], h["footer"], h["rows"]) == ("headline", "Your queue matters", "", [])
    n = broll.scene_props({"shot": "card", "note_ids": ["N1"], "start": 0, "end": 2}, FACTS, NOTES, None)
    assert (n["title"], n["footer"]) == ("What the sources say", "Sources linked in the description")


def test_render_refused_without_a_licence_entry():
    job = create_job("a topic")
    with Session(engine) as s, s.begin():
        s.add(Asset(job_id=job.id, kind="voice", source="tts", source_ref="kokoro", license="Apache-2.0", path="/x/voice.wav"))
        s.add(Asset(job_id=None, kind="music", source="royalty_free", source_ref="lib", license="Pixabay", path="/lib/bed.mp3"))
    ensure_licensed(job.id, ["/x/voice.wav", "/lib/bed.mp3"])  # shared library assets count for every job
    with pytest.raises(Unlicensed, match="no licence entry for /x/meme.mp4"):
        ensure_licensed(job.id, ["/x/voice.wav", "/x/meme.mp4"])


def test_broll_renders_every_card_and_headline_and_logs_them(monkeypatch, tmp_path):
    job = create_job(PKG)
    job_dir = tmp_path / "jobs" / str(job.id)
    job_dir.mkdir(parents=True)
    scenes = [{"shot": "desk", "line": "Hi.", "start": 0, "end": 2},
              {"shot": "card", "fact_ids": ["F1", "F3"], "line": "x", "start": 2.3, "end": 5},
              {"shot": "headline", "text": "Big week", "line": "y", "start": 5.3, "end": 7}]
    (job_dir / "voice.json").write_text(json.dumps({"scenes": scenes}))
    monkeypatch.setattr(broll, "STORAGE", tmp_path)

    def fake_run(cmd, **kw):
        items = json.loads((job_dir / "broll.json").read_text())
        (job_dir / "broll").mkdir()
        for x in items:
            (job_dir / "broll" / f"{x['id']}.mp4").write_bytes(b"mp4")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    out = broll.broll(job.id)
    assert [(x["scene"], x["start"]) for x in out] == [(1, 2.3), (2, 5.3)]
    items = json.loads((job_dir / "broll.json").read_text())
    assert [r["value"] for r in items[0]["props"]["rows"]] == ["#1", "68"]
    with Session(engine) as s:
        kinds = s.scalars(select(Asset.kind).where(Asset.job_id == job.id).order_by(Asset.id)).all()
    assert kinds == ["data_card", "broll"]
    ensure_licensed(job.id, [x["path"] for x in out])
