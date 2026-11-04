"""V4.1-V4.2: the job becomes your FilmCraft format; captions clear the badge; library sounds need a cleared licence."""

import csv
from pathlib import Path

import pytest

from studio import edit
from studio.config import CHARACTER_NAME
from studio.db import Unlicensed, ensure_licensed
from studio.inputs import create_job

SCENES = [{"shot": "desk", "pose": "talk", "start": 0.0}, {"shot": "desk", "pose": "talk", "start": 3.9},
          {"shot": "card", "start": 6.1}, {"shot": "headline", "start": 20.7}, {"shot": "desk", "pose": "shocked", "start": 25.7},
          {"shot": "desk", "pose": "thinking", "start": 35.1}, {"shot": "desk", "pose": "talk", "start": 39.6}]


def test_news_format_beats():
    b = edit.beats(SCENES, package=True)
    assert [(t, lay, asset) for t, lay, asset, _ in b] == [
        (0.0, "punch", None), (3.85, "full", None), (6.05, "broll", "scene-02"), (20.65, "broll", "scene-03"),
        (25.65, "punch", None), (35.05, "full", None), (39.55, "punch", None)]
    assert b[1][3]["title"][0][0] == CHARACTER_NAME and b[1][3]["title"][1][0] == "AI news host · data by Trend Radar"
    assert b[-1][3]["follow"] and ["ding", 0.1] in b[-1][3]["sfx"]
    assert all(ex.get("zoom", 1) <= edit.PUNCH for *_, ex in b)
    assert edit.beats(SCENES, package=False)[1][3]["title"][1][0] == "AI news host"  # no Trend Radar claim on topics


def test_captions_and_lower_third_clear_the_press_badge():
    badge_top, badge_bottom, face_y, half_caption = 1224, 1386, edit.FACE[1], 42
    for zoom in (1.0, 1.05, edit.PUNCH):  # full push-in ends at 1.05; punch-ins at PUNCH
        assert face_y + (badge_bottom - face_y) * zoom < edit.CAPTION_Y - half_caption
    lower_third = edit.beats(SCENES, package=True)[1][3]["title"]
    assert max(y for *_, y in lower_third) + 23 < badge_top  # 46 px subtitle above the badge at 1x


def test_highlights_are_topics_and_values():
    hl = edit.highlights({"facts": [{"type": "verified", "label": "Pre-load: rank", "value": "#1"},
                                    {"type": "verified", "label": "File size: score (0-100)", "value": "36"}]})
    assert hl == ["#1", "36", "file", "pre-load", "size"]


def test_library_sounds_need_a_cleared_licence(monkeypatch, tmp_path):
    lib = tmp_path / "lib"
    (lib / "Download Records").mkdir(parents=True)
    cols = ["filename", "source_url", "creator", "license", "commercial_use", "attribution_required", "verification_status"]
    with open(lib / "Download Records" / "sound-library.csv", "w", newline="") as f:
        w = csv.DictWriter(f, cols)
        w.writeheader()
        w.writerow(dict(zip(cols, ["pop-mixkit-1.wav", "https://mixkit.co/x", "Mixkit", "Mixkit Sound Effects Free License", "yes", "no", "verified"])))
        w.writerow(dict(zip(cols, ["meme-2.mp4", "https://memes.example/x", "unknown", "unverified", "uncertain", "no", "unverified"])))
    monkeypatch.setattr(edit, "SOUND_LIBRARY", lib)
    job = create_job("a topic")
    ok, bad = str(lib / "UI" / "pop-mixkit-1.wav"), str(lib / "Memes" / "meme-2.mp4")
    edit.library_provenance([ok])
    ensure_licensed(job.id, [ok])  # logged once as a shared asset, so it counts for every job
    with pytest.raises(Unlicensed, match="meme-2.mp4 is not cleared"):
        edit.library_provenance([bad])
    with pytest.raises(Unlicensed, match="no licence entry"):
        ensure_licensed(job.id, [ok, str(Path("/elsewhere/unlogged.wav"))])
