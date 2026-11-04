import wave

import pytest

from studio import voice

needs_model = pytest.mark.skipif(not (voice.MODELS / "kokoro-v1.0.onnx").exists(), reason="Kokoro model not downloaded")


@needs_model
def test_synthesize_writes_audio(tmp_path):
    out = tmp_path / "line.wav"
    seconds, cues = voice.synthesize("Ping check, the radar is online.", out)
    assert 1 < seconds < 6
    assert {c["value"] for c in cues} >= {"A", "B"}  # the p in "ping", the t/k sounds
    with wave.open(str(out)) as f:
        assert f.getnchannels() == 1 and f.getnframes() / f.getframerate() == pytest.approx(seconds)


def test_mouth_cues_map_merge_and_rest():
    from kokoro_onnx import Timing

    t = [Timing("m", 0.0, 0.1), Timing("ˈ", 0.1, 0.12), Timing("ɑ", 0.12, 0.3), Timing("ɑ", 0.3, 0.4),
         Timing(" ", 0.4, 0.41), Timing("f", 0.6, 0.7)]
    cues = voice.mouth_cues(t)
    assert [c["value"] for c in cues] == ["A", "D", "X", "G"]  # stress mark kept "m", the 10 ms space folded in
    assert cues[1] == {"start": 0.12, "end": 0.41, "value": "D"}
    assert cues[2] == {"start": 0.41, "end": 0.6, "value": "X"}  # the pause before "f" is rest


def test_spoken_text_reads_symbols_aloud():
    assert voice.spoken("Map is up 1 place (#5 → #4), growth 1.2x vs Xbox.") == \
        "Map is up 1 place (number 5  to  number 4), growth 1.2 times versus Xbox."


def test_match_reports_what_whisper_heard_differently():
    heard = [{"word": w} for w in "Preload is number six, not hash one.".split()]
    ratio, diffs = voice.match("Pre-load is #6, not #1.", heard)
    assert ratio < 1 and diffs == ["number → hash"]  # spelling (preload, six) is not a difference
    assert voice.match("Pre-load is #1.", [{"word": "Pre-load"}, {"word": "is"}, {"word": "number"}, {"word": "1."}])[0] == 1.0


def test_voice_track_joins_scenes_and_logs_provenance(monkeypatch, tmp_path):
    import json

    import numpy as np
    from sqlalchemy import select, text
    from sqlalchemy.orm import Session

    from studio.db import Asset, Cost, Script, engine
    from studio.inputs import create_job

    rate = 24000
    monkeypatch.setattr(voice, "STORAGE", tmp_path)
    monkeypatch.setattr(voice, "_speak", lambda text, v: (np.zeros(rate, np.float32), rate,
                                                          [{"start": 0.1, "end": 0.5, "value": "C"}]))
    monkeypatch.setattr(voice, "words", lambda wav: [{"word": "hi", "start": 0.1, "end": 0.3}])
    with engine.begin() as c:  # other tests leave tts spend behind; the $0 cap would rightly refuse
        c.execute(text("delete from costs where service = 'tts'"))
    job = create_job("a topic")
    lines = [{"part": "hook", "shot": "desk", "pose": "talk", "line": "One."}, {"part": "next", "shot": "card", "line": "Two."}]
    with Session(engine) as s, s.begin():
        s.add(Script(job_id=job.id, version=1, body={"scenes": lines}))
    r = voice.voice_track(job.id)
    assert [(x["start"], x["end"]) for x in r["scenes"]] == [(0.0, 1.0), (1.3, 2.3)]  # 0.3 s pause between scenes
    assert r["cues"][1] == {"start": 1.4, "end": 1.8, "value": "C"} and r["duration"] == 2.3
    with wave.open(str(tmp_path / "jobs" / str(job.id) / "voice.wav")) as f:
        assert f.getnframes() / f.getframerate() == pytest.approx(2.3)
    assert json.loads((tmp_path / "jobs" / str(job.id) / "voice.json").read_text())["words"] == r["words"]
    with Session(engine) as s:
        a = s.scalars(select(Asset).where(Asset.job_id == job.id)).one()
        c = s.scalars(select(Cost).where(Cost.job_id == job.id)).one()
    assert (a.kind, a.source, a.license.startswith("Apache-2.0")) == ("voice", "tts", True)
    assert (c.service, c.usd, float(c.quantity), c.unit) == ("tts", 0, 2.3, "seconds")


def test_caption_words_keep_the_script_text_with_whisper_timing():
    heard = [{"word": "Preload", "start": 0.0, "end": 0.4}, {"word": "is", "start": 0.4, "end": 0.5},
             {"word": "number", "start": 0.5, "end": 0.8}, {"word": "one.", "start": 0.8, "end": 1.0},
             {"word": "Game", "start": 1.2, "end": 1.4}, {"word": "Reporter's", "start": 1.4, "end": 1.9},
             {"word": "online!", "start": 1.9, "end": 2.3}]
    got = voice.caption_words(["Pre-load is (#1).", "Ping — GameReporter's online!"], heard)
    assert [(w["word"], w["start"], w["end"]) for w in got] == [
        ("Pre-load", 0.0, 0.4), ("is", 0.4, 0.5), ("#1.", 0.5, 1.0), ("GameReporter's", 1.2, 1.9), ("online!", 1.9, 2.3)]  # "Ping" unheard: no caption
