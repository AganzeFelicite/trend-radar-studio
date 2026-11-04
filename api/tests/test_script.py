"""V3.3: the script validator enforces the arc, verified numbers, on-screen rules and fresh titles."""

import copy
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from studio import llm, script
from studio.config import OPENER, SIGNOFF
from studio.db import Script, engine
from studio.inputs import create_job

PKG = (Path(__file__).parent / "fixtures" / "package.json").read_text()  # F1 #1, F3 68, F4 11.5%, F5 3, F6 62
VALID = {
    "titles": ["Pre-load holds the #1 spot", "GTA 6 pre-load: what the radar shows", "Why everyone is talking about pre-load"],
    "thumbnail_text": "Pre-load stays #1",
    "scenes": [
        {"part": "hook", "shot": "desk", "pose": "shocked", "line": "Pre-load is still the #1 topic on the radar."},
        {"part": "what", "shot": "card", "fact_ids": ["F1", "F3"],
         "line": "Pre-load sits at #1 with a score of 68 out of 100, the same spot it held 6 hours ago."},
        {"part": "what", "shot": "card", "fact_ids": ["F4", "F5", "F6"],
         "line": "It owns 11.5% of the GTA 6 conversation across 3 sources, with 62 posts and videos in 24 hours."},
        {"part": "why", "shot": "headline", "text": "Your download queue matters",
         "line": "Why it matters: everyone is planning their install, so creators who explain storage and timing get the clicks."},
        {"part": "why", "shot": "desk", "pose": "thinking", "note_ids": ["N1"],
         "line": "Rockstar's own page lists a pre-load start date, and that is what people keep searching for."},
        {"part": "next", "shot": "desk", "pose": "talk",
         "line": "Next, watch whether pre-load keeps the top spot as launch gets closer. That's your patch notes for today."},
    ],
}


@pytest.fixture
def ctx():
    return script.context(create_job(PKG).id)


def test_valid_script_passes(ctx):
    assert script.validate(VALID, ctx) == []


def mutate(path, value):
    s = copy.deepcopy(VALID)
    *keys, last = path
    target = s
    for k in keys:
        target = target[k]
    target[last] = value
    return s


@pytest.mark.parametrize("bad, error", [
    (mutate(["scenes", 1, "line"], "Pre-load sits at #1 with a score of 70."), "numbers not in the verified facts: 70"),
    (mutate(["scenes", 2, "line"], "It owns 12% of the conversation."), "numbers not in the verified facts: 12"),
    (mutate(["scenes", 4, "line"], "The map is twice the size of the last one."), "spelled-out numbers: twice"),
    (mutate(["titles", 0], "Pre-load hits 500 searches"), "numbers not in the verified facts: 500"),
    (mutate(["scenes"], [VALID["scenes"][i] for i in (0, 1, 2, 5)]), "arc is missing: why"),
    (mutate(["scenes"], [VALID["scenes"][i] for i in (0, 3, 1, 2, 4, 5)]), "out of arc order"),
    (mutate(["scenes", 0, "shot"], "headline"), "first scene must be the hook"),
    (mutate(["scenes", 0, "line"], "Pre-load is still the #1 topic on the radar and nothing else comes close today."), "hook has"),
    (mutate(["scenes", 5, "shot"], "headline"), "last scene must be on the desk"),
    (mutate(["scenes"], [s | {"shot": "desk"} for s in VALID["scenes"]]), "no data card"),
    (mutate(["scenes", 1, "fact_ids"], ["F99"]), "unknown facts ['F99']"),
    (mutate(["scenes", 4, "note_ids"], ["N9"]), "unknown notes ['N9']"),
    (mutate(["scenes", 3, "text"], "a headline that is far too long to read"), "on-screen text has 9 words"),
    (mutate(["scenes", 1, "text"], "Pre-load sits at #1 with a score of 68"), "on-screen text has 9 words"),
    (mutate(["scenes", 3, "text"], ""), "headline with no text"),
    (mutate(["titles"], VALID["titles"][:2]), "exactly 3 titles"),
    (mutate(["thumbnail_text"], "this thumbnail text is far too long"), "thumbnail_text must be"),
    (mutate(["scenes", 3, "line"], "Why it matters. " * 40), "of speech; the target is 40 s"),
])
def test_rules(ctx, bad, error):
    assert any(error in e for e in script.validate(bad, ctx)), script.validate(bad, ctx)


def test_titles_and_thumbnail_differ_from_recent_videos(ctx):
    ctx["previous"], ctx["previous_thumbs"] = ["Pre-load holds the #1 spot!"], ["Pre-load stays #1!"]
    errors = script.validate(VALID, ctx)
    assert any("too close to a recent one: 'Pre-load holds the #1 spot!'" in e for e in errors)
    assert any("thumbnail text 'Pre-load stays #1' is too close" in e for e in errors)


def test_retry_then_store(monkeypatch):
    prompts, drafts = [], [mutate(["scenes", 1, "line"], "Pre-load sits at #1 with a score of 70."), VALID]
    monkeypatch.setattr(llm, "ask", lambda p, schema, **kw: prompts.append(p) or copy.deepcopy(drafts[len(prompts) - 1]))
    job = create_job(PKG)
    body = script.write(job.id)
    assert "numbers not in the verified facts: 70" in prompts[1] and "Pre-load" in prompts[0]
    assert [s["line"] for s in body["scenes"][:2]] == [VALID["scenes"][0]["line"], OPENER]
    assert body["scenes"][-1]["line"] == SIGNOFF and 30 <= body["est_seconds"] <= 46
    with Session(engine) as s:
        assert s.scalar(select(Script.version).where(Script.job_id == job.id)) == 1
    # the next job must not reuse these titles
    assert VALID["titles"][0] in script.context(create_job(PKG).id)["previous"]


def test_gives_up_after_three_tries(monkeypatch):
    calls = []
    bad = mutate(["scenes", 1, "line"], "A score of 70.")
    monkeypatch.setattr(llm, "ask", lambda p, schema, **kw: calls.append(1) or copy.deepcopy(bad))
    job = create_job(PKG)
    with pytest.raises(script.ScriptInvalid, match="after 3 tries: numbers not in the verified facts: 70"):
        script.write(job.id)
    assert len(calls) == 3
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(Script).where(Script.job_id == job.id)) == 0
