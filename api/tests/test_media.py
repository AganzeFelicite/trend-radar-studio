"""V7.4: fetched B-roll becomes timed 1080x1920 clips; only Rockstar-hosted official media; the D20 share gate."""

import json
import subprocess
from pathlib import Path

import pytest

from studio import media, script
from studio.config import PIXABAY_API_KEY


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,codec_type,r_frame_rate,nb_frames",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["streams"]


@pytest.mark.parametrize("make", ["image", "video"])
def test_to_clip_is_vertical_silent_and_timed(tmp_path, make):
    src = tmp_path / ("src.png" if make == "image" else "src.mp4")
    lavfi = "testsrc=size=1600x900:rate=30" + ("" if make == "video" else ":duration=1")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", lavfi, "-t", "1", *(["-frames:v", "1"] if make == "image" else []),
                    "-pix_fmt", "yuv420p", str(src)], check=True)  # a 1 s landscape source
    out = media.to_clip(src, 2.5, tmp_path / "scene-03.mp4")  # longer than the source: the video loops, the still pushes in
    streams = probe(out)
    assert [s["codec_type"] for s in streams] == ["video"]
    assert (streams[0]["width"], streams[0]["height"], streams[0]["r_frame_rate"]) == (1080, 1920, "30/1")
    assert abs(int(streams[0]["nb_frames"]) - 75) <= 2


@pytest.mark.parametrize("url", ["https://www.ign.com/articles/gta-6", "http://rockstargames.com/newswire/x", "https://rockstargames.com.evil.io/a"])
def test_official_media_must_be_rockstar_hosted_https(tmp_path, url):
    with pytest.raises(ValueError, match="not an official media URL"):
        media.official(url, tmp_path)


def test_third_party_share_counts_only_broll_scenes():
    scenes = [{"shot": "desk", "start": 0, "end": 4}, {"shot": "broll", "start": 4, "end": 10}, {"shot": "card", "start": 10, "end": 16},
              {"shot": "broll", "start": 16, "end": 18}, {"shot": "desk", "start": 18, "end": 20}]
    assert media.third_party_share(scenes) == 0.4
    assert media.third_party_share([]) == 0.0


def test_research_media_leads_keep_only_rockstar_hosted_images():
    from studio.research import media_leads
    leads = media_leads([
        {"url": "https://media-rockstargames-com.akamaized.net/x.jpg", "page": "https://www.rockstargames.com/newswire/a", "shows": "cdn copy"},
        {"url": "https://www.rockstargames.com/img/a.jpg", "page": "https://www.rockstargames.com/newswire/a", "shows": "Jason and Lucia"},
        {"url": "https://www.rockstargames.com/img/b.jpg", "page": "https://www.ign.com/a", "shows": "a news page"},
    ])
    assert [m["id"] for m in leads] == ["M1"] and leads[0]["shows"] == "Jason and Lucia"


@pytest.mark.skipif(not PIXABAY_API_KEY, reason="PIXABAY_API_KEY not set")
def test_pixabay_returns_a_credited_file(tmp_path):
    got = media.pixabay("game controller close up", tmp_path)
    assert got and Path(got["path"]).stat().st_size > 10_000 and got["page"].startswith("https://pixabay.com/")
    assert got["credit"].startswith(("Footage: Pixabay", "Photo: Pixabay"))


def test_script_broll_rules():
    ctx = {"verified": {"F1": "Pre-load: rank: #1"}, "notes": {}, "media": {"M1": {"url": "u", "page": "p", "shows": "s"}},
           "allowed": {"1"}, "previous": [], "previous_thumbs": []}
    ok = {"part": "what", "shot": "broll", "query": "game controller close up", "line": "x"}
    errs = lambda sc: [e for e in script.validate({"titles": ["a", "b", "c"], "thumbnail_text": "t", "scenes": [
        {"part": "hook", "shot": "desk", "line": "Hook."}, sc, {"part": "why", "shot": "card", "fact_ids": ["F1"], "line": "y"},
        {"part": "next", "shot": "desk", "line": "z"}]}, ctx | {"job": type("J", (), {"target_seconds": 15})()}) if "broll" in e]
    assert errs(ok) == []
    assert errs(ok | {"media_id": "M1"}) and errs({**ok, "query": ""})
    assert errs({**ok, "query": "", "media_id": "M9"}) and not errs({**ok, "query": "", "media_id": "M1"})
    assert errs({**ok, "query": "top 5 consoles 2026"}) and errs({**ok, "query": "controller"})
    two = {"titles": ["a", "b", "c"], "thumbnail_text": "t", "scenes": [
        {"part": "hook", "shot": "desk", "line": "Hook."}, {**ok, "query": "", "media_id": "M1"}, {**ok, "query": "", "media_id": "M1"},
        {"part": "why", "shot": "card", "fact_ids": ["F1"], "line": "y"}, {"part": "next", "shot": "desk", "line": "z"}]}
    assert any("repeats media_id" in e for e in script.validate(two, ctx | {"job": type("J", (), {"target_seconds": 15})()}))
