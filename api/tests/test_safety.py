"""V3.4: sensitive topics are blocked with a clear reason; sensational framing needs a cited source or is never allowed."""

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from studio import llm, safety, script
from studio.db import Job, engine
from studio.inputs import create_job

PKG = (Path(__file__).parent / "fixtures" / "package.json").read_text()


def job_row(job_id):
    with Session(engine) as s:
        j = s.get(Job, job_id)
        return j.status, j.error


def no_llm(*a, **kw):
    raise AssertionError("the classifier must not run when the blocklist already blocked")


def test_finance_topic_is_blocked_with_a_clear_reason(monkeypatch):
    monkeypatch.setattr(llm, "ask", no_llm)
    job = create_job("How to invest your GTA 6 money in crypto")
    with pytest.raises(safety.Blocked, match=r"Blocked: finance topic \(blocklist: 'invest'\)\. The Studio never covers finance"):
        safety.gate(job.id)
    assert job_row(job.id) == ("blocked", "Blocked: finance topic (blocklist: 'invest'). " + safety.RULE)


def test_classifier_catches_what_the_blocklist_misses(monkeypatch):
    monkeypatch.setattr(llm, "ask", lambda p, schema, **kw: {"category": "finance", "reason": "It is about a company's share price."})
    job = create_job("Take-Two share price after the GTA 6 trailer")
    with pytest.raises(safety.Blocked, match=r"finance topic \(AI classifier: It is about a company's share price\.\)"):
        safety.gate(job.id)
    assert job_row(job.id)[0] == "blocked"


def test_game_news_passes(monkeypatch):
    seen = []
    monkeypatch.setattr(llm, "ask", lambda p, schema, **kw: seen.append(p) or {"category": "none", "reason": "Game news."})
    for raw in ("GTA 6 health bar and armor changes", PKG):
        job = create_job(raw)
        safety.gate(job.id)
        assert job_row(job.id) == ("queued", None)
    assert "Pre-load" in seen[1]  # the package's topics are what gets classified


NOTES = {"N1": ("Rockstar confirmed the pre-load date on its Newswire.", "https://www.rockstargames.com/newswire/x"),
         "N2": ("Destructoid says the file size is not confirmed.", "https://www.destructoid.com/x")}


def errors(line="Pre-load is #1.", note_ids=(), title="Pre-load holds the top spot", text=""):
    s = {"titles": [title, "b", "c"], "thumbnail_text": "Pre-load stays on top",
         "scenes": [{"part": "hook", "shot": "desk", "line": line, "text": text, "note_ids": list(note_ids)}]}
    return " | ".join(safety.sensational(s, NOTES))


@pytest.mark.parametrize("kw, expected", [
    (dict(line="LEAKED footage shows the new map."), "says leaked: never allowed"),
    (dict(line="LEAKED footage shows the new map."), "all-caps words: LEAKED"),
    (dict(line="GTA 6 is CANCELLED."), "says cancelled without a cited note"),
    (dict(line="Rockstar CONFIRMED the date."), "says confirmed without a cited note"),
    (dict(line="Rockstar confirmed the date.", note_ids=["N2"]), "says confirmed without a cited note"),  # N2 says *not* confirmed
    (dict(line="An insider says the map grew."), "says insider: never allowed"),
    (dict(line="Last chance to pre-load!"), "says last chance: never allowed"),
    (dict(text="Breaking news"), "says breaking: never allowed"),
    (dict(title="GTA 6 map size CONFIRMED"), "uses CONFIRMED, confirmed: never in titles"),
    (dict(title="The leak everyone missed"), "uses leak: never in titles"),
])
def test_sensational_rejected(kw, expected):
    assert expected in errors(**kw), errors(**kw)


@pytest.mark.parametrize("kw", [
    dict(line="Rockstar confirmed the pre-load date.", note_ids=["N1"]),  # a cited note says so, in that scene
    dict(line="The file size is not confirmed yet."),
    dict(line="Rockstar hasn't officially confirmed the size."),
    dict(line="The size is unconfirmed, so treat it as a guess."),
    dict(line="GTA and DLC talk is up."),
])
def test_honest_lines_pass(kw):
    assert errors(**kw) == ""


def test_script_validator_runs_the_check():
    job = create_job(PKG)
    ctx = script.context(job.id)
    draft = {"titles": ["a"], "thumbnail_text": "x", "scenes": [{"part": "hook", "shot": "desk", "line": "This leak is huge."}]}
    assert any("says leak: never allowed" in e for e in script.validate(draft, ctx))
