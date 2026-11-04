"""V3.6: the talking clip gets the whole voice track, reaction poses on desk scenes, provenance and a $0 cost."""

import json
import subprocess

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from studio import clip
from studio.db import Asset, Cost, engine
from studio.inputs import create_job

TRACK = {"duration": 9.0, "cues": [{"start": 0.1, "end": 0.4, "value": "C"}], "scenes": [
    {"shot": "desk", "pose": "shocked", "start": 0.0, "end": 3.0},
    {"shot": "card", "start": 3.3, "end": 6.0},
    {"shot": "desk", "pose": "thinking", "start": 6.3, "end": 7.5},
    {"shot": "desk", "pose": "talk", "start": 7.8, "end": 9.0}]}


def test_props_hold_reactions_briefly_on_desk_scenes():
    assert clip.props(TRACK) == {"audio": "job/voice.wav", "duration": 9.0, "cues": TRACK["cues"], "poses": [
        {"start": 0.0, "end": 2.0, "pose": "shocked"}, {"start": 6.3, "end": 7.5, "pose": "thinking"}]}


def test_render_logs_provenance_and_zero_cost(monkeypatch, tmp_path):
    job = create_job("a topic")
    job_dir = tmp_path / "jobs" / str(job.id)
    job_dir.mkdir(parents=True)
    (job_dir / "voice.json").write_text(json.dumps(TRACK))
    monkeypatch.setattr(clip, "STORAGE", tmp_path)
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        (job_dir / "reporter.mp4").write_bytes(b"mp4")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with engine.begin() as c:
        c.execute(text("delete from costs where service = 'avatar'"))
    assert clip.talking_clip(job.id) == job_dir / "reporter.mp4"
    assert "TalkingClip" in calls[0] and f"{job_dir / 'voice.wav'}:/app/public/job/voice.wav:ro" in calls[0]
    assert json.loads((job_dir / "talk-props.json").read_text())["poses"][0]["pose"] == "shocked"
    with Session(engine) as s:
        a = s.scalars(select(Asset).where(Asset.job_id == job.id)).one()
        c = s.scalars(select(Cost).where(Cost.job_id == job.id)).one()
    assert (a.kind, a.source, a.license.startswith("Own work")) == ("avatar_clip", "own", True)
    assert (c.service, c.usd) == ("avatar", 0)
