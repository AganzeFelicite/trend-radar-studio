"""V4.1-V4.2: the final edit in your FilmCraft format (D16), headless: your open FilmCraft app is never touched.
The job's scenes become a filmcraft-commentary-short plan.json. The reporter clip stands in for phone footage,
cards and headlines are full-frame `broll` beats, and the skill's pop captions show the script's own words, timed
by whisper. Every media file in the built project must have a provenance row with a licence, or nothing renders.
Your Studio's render.py draws the picture in FilmCraft and mixes the audio with ffmpeg; loudness ends at -14 LUFS.
Run on the host: `uv run python -m studio.edit <job_id>`."""

import csv
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from studio.config import CHARACTER_NAME, FILMCRAFT_CLI, FILMCRAFT_RENDER, FILMCRAFT_SKILL, SOUND_LIBRARY, STORAGE
from studio.db import Asset, Job, Unlicensed, engine, ensure_licensed
from studio.voice import caption_words

FACE, HEAD_TOP = [540, 503], 152  # renderer/src/Reporter.tsx FACE: where the reporter's face sits in the clip
# The PRESS badge spans y 1224-1386 at 1x and moves down with a face-held zoom (y' = 503 + (y - 503) * z):
# captions at 1530 stay clear of it up to a 1.1x punch-in, above the "+ Follow" pill (1595+).
CAPTION_Y, PUNCH = 1530, 1.1
CREDIT_Y = 1400  # the footage credit line, just above the captions
REACTIONS = {"shocked", "celebrating", "laughing"}
CYAN, WHITE = "#00e5d4", "#ffffff"
# Beds from your skill's cleared list (CC0 / Mixkit Free License, no credit needed), rotated per job.
BEDS = ["Impacts & Cinematic/Cinematic Ambience/lo-fi-beat-atmo-music-piano-drums-dub-experimental-cinematic-freesound-611186.mp3",
        "Music & Background/Tension Beds/minimal-investigative-tension-no-melody-freesound-868504.mp3",
        "Impacts & Cinematic/Cinematic Ambience/dark-beat-synth-electro-atmo-ambience-bell-drama-rap-cinemat-freesound-611374.mp3",
        "Impacts & Cinematic/Cinematic Ambience/future-ambience-background-freesound-456101.mp3",
        "Impacts & Cinematic/Suspense & Tension/synth-suspense-music-mixkit-681.wav",
        "Music & Background/Tension Beds/tension-and-progress-drum-loop-at-120bpm-freesound-843467.mp3"]


def beats(scenes: list[dict], package: bool, credits: dict | None = None) -> list:
    """News format: desk scenes on the host (punch-in for the hook, reactions and sign-off, slow push otherwise),
    card/headline/broll scenes as full-frame B-roll (fetched footage carries its credit line), a name lower-third
    on the opener."""
    out, credits = [], credits or {}
    for i, s in enumerate(scenes):
        t = 0.0 if i == 0 else round(s["start"] - 0.05, 3)  # a beat starts just before its first word
        if s["shot"] != "desk":
            credit = credits.get(str(i)) or credits.get(i)
            out.append([t, "broll", f"scene-{i:02d}", {"title": [[credit, 34, "F", WHITE, CREDIT_Y]]} if credit else {}])
        elif i == 0:
            out.append([t, "punch", None, {"zoom": PUNCH, "boom": True}])
        elif i == len(scenes) - 1:
            out.append([t, "punch", None, {"zoom": PUNCH, "follow": True, "sfx": [["ding", 0.1]]}])
        elif s.get("pose") in REACTIONS:
            out.append([t, "punch", None, {"zoom": PUNCH}])
        else:
            out.append([t, "full", None, {}])
    if len(out) > 1 and out[1][1] != "broll":  # the opener ("Ping check…") introduces the host
        out[1][3]["title"] = [[CHARACTER_NAME, 90, "T", CYAN, 1105],  # above the badge, under the chin
                              ["AI news host" + (" · data by Trend Radar" if package else ""), 46, "F", WHITE, 1180]]
    return out


def highlights(pkg: dict) -> list[str]:
    """Caption words that turn yellow: topic names and our verified values."""
    words = {w for f in pkg.get("facts", []) if f["type"] == "verified"
             for w in f["label"].split(": ", 1)[0].split() + [f["value"]]}
    return sorted(w.lower() for w in words)


def write_plan(job_id: int) -> Path:
    job_dir = STORAGE / "jobs" / str(job_id)
    work, assets = job_dir / "edit", job_dir / "broll"
    work.mkdir(parents=True, exist_ok=True)
    assets.mkdir(exist_ok=True)
    track = json.loads((job_dir / "voice.json").read_text())
    with Session(engine) as s:
        pkg = s.get(Job, job_id).input
    duration = round(track["duration"] + 0.45, 3)  # the clip runs 0.5 s past the last word
    json.dump({"edl": [{"in": 0.0, "out": duration, "at": 0.0}], "duration": duration}, open(work / "edl.json", "w"))
    words = caption_words([sc["line"] for sc in track["scenes"]], track["words"])
    json.dump({"segments": [{"words": words}]}, open(work / "cut.json", "w"))
    shutil.copy(job_dir / "voice.wav", work / "cut.wav")  # build.py sets the voice gain from its loudness
    if not (assets / "meme_bg.png").exists():  # build.py always imports one; ours is a plain navy frame
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x0b1026:s=1080x1920",
                        "-frames:v", "1", str(assets / "meme_bg.png")], check=True)
        with Session(engine) as s, s.begin():
            s.add(Asset(job_id=job_id, kind="broll", source="own", source_ref="ffmpeg color 0x0b1026",
                        license="Own work: plain navy frame", path=str(assets / "meme_bg.png")))
    credits_file = assets / "credits.json"
    credits = json.loads(credits_file.read_text()) if credits_file.exists() else {}
    plan = {"name": f"{CHARACTER_NAME} job {job_id}", "src": str(job_dir / "reporter.mp4"), "face": FACE,
            "head_top": HEAD_TOP, "caption_low": CAPTION_Y, "music": str(SOUND_LIBRARY / BEDS[job_id % len(BEDS)]), "takes": [[0.0, duration]],
            "beats": beats(track["scenes"], "facts" in pkg, credits), "hl": highlights(pkg), "work": str(work),
            "assets": str(assets)}
    (work / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    return work / "plan.json"


def library_provenance(paths: list[str]) -> None:
    """Log Sound Library files as shared assets from its verified catalogue; refuse anything not cleared."""
    catalogue = {r["filename"]: r for r in csv.DictReader(open(SOUND_LIBRARY / "Download Records" / "sound-library.csv"))}
    with Session(engine) as s, s.begin():
        logged = set(s.scalars(select(Asset.path).where(Asset.job_id.is_(None))))
        for p in paths:
            if p in logged or not p.startswith(str(SOUND_LIBRARY)):
                continue
            r = catalogue.get(Path(p).name)
            if not r or r["commercial_use"] != "yes" or r["verification_status"] != "verified" or "Uncertain" in p:
                raise Unlicensed(f"refusing to render: {Path(p).name} is not cleared for commercial use in the library")
            s.add(Asset(job_id=None, kind="music" if p.endswith(tuple(BEDS)) else "sfx", source="royalty_free",
                        source_ref=r["source_url"], license=r["license"], path=p,
                        meta={"creator": r["creator"], "attribution_required": r["attribution_required"] == "yes"}))


def project_media(project: Path) -> list[str]:
    items = json.loads(project.read_text())["project"]["items"].values()
    return sorted({i["kind"]["Media"]["media"]["File"]["path"] for i in items
                   if i.get("kind", {}).get("Media", {}).get("media", {}).get("File")})


def _run(cmd: list[str], what: str, timeout: int = 1800) -> str:
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    failed = [line for line in run.stdout.splitlines() if " cmds, " in line and " 0 failed" not in line]
    if run.returncode or failed:  # build.py prints "[run_x.jsonl] N cmds, K failed" per batch
        raise RuntimeError(f"{what} failed: {(run.stdout + run.stderr)[-1500:]}")
    return run.stdout


def render(project: Path, out: Path) -> None:
    """Your Studio render.py's method: FilmCraft exports the picture only, ffmpeg mixes the timeline's audio
    (FilmCraft's headless export deadlocks on overlapping sounds). Its own functions build the mix."""
    spec = importlib.util.spec_from_file_location("studio_render", FILMCRAFT_RENDER)
    r = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r)
    txt = _run([FILMCRAFT_CLI, "--project", str(project), "inspect", "sequence"], "inspect")
    seq = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    total = seq["duration"] / r.TICKS
    video = out.with_name(out.stem + ".video.mp4")
    _run([FILMCRAFT_CLI, "--project", str(project), "export", str(video), "--format", "h264", "--no-audio"],
         "picture export", timeout=3600)
    cmd = r.build_cmd(video, r.audio_clips(seq, json.loads(project.read_text())), total, out, True)
    i = cmd.index("-filter_complex") + 1
    # render.py pads with an endless `apad` and relies on -t, which this ffmpeg never honours with a copied video
    # stream (the mix runs forever). Bounded padding ends it: same result, finishes in ~1 s.
    cmd[i] = cmd[i].replace(",apad[aout]", f",apad=whole_dur={total:.3f}[aout]")
    _run(cmd, "audio mix", timeout=600)
    video.unlink()


# The ffmpeg mix skips FilmCraft's mixer inserts, so the voice compressor/limiter from build.py runs here instead:
# it leaves loudnorm the headroom to reach -14 LUFS (without it: -14.9 at the -1.5 dBTP ceiling).
DYNAMICS = "acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=4dB,alimiter=limit=-3dB:level=false"


def loudnorm(src: Path, out: Path, lufs: float = -14.0) -> None:
    """Two-pass loudnorm to your -14 LUFS / -1.5 dBTP export target."""
    target = f"{DYNAMICS},loudnorm=I={lufs}:TP=-1.5:LRA=11"
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"{target}:print_format=json",
                          "-f", "null", "-"], capture_output=True, text=True, stdin=subprocess.DEVNULL).stderr
    m = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
    measured = (f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
                f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    _run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:v", "-map", "0:a", "-af",
          f"{target}:{measured}", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
          "-movflags", "+faststart", str(out)], "loudness")


def edit(job_id: int) -> Path:
    t0 = time.time()
    step = lambda msg: print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)  # progress for the log
    plan = write_plan(job_id)
    step("plan written")
    work = plan.parent
    scripts = FILMCRAFT_SKILL / "scripts"
    step(_run(["python3", str(scripts / "check.py"), str(plan)], "check").strip())
    project = work / "project.fcproj"
    if not project.exists():
        # a bin named like the plan: build.py's cleanup deletes and recreates it, so nothing is left over
        name = json.loads(plan.read_text())["name"]
        _run([FILMCRAFT_CLI, "--save-as", str(project), "--compact", "exec", "file.newBin", f"name={name}"], "new project")
    cli = [FILMCRAFT_CLI, "--project", str(project), "--save", "--compact", "--keep-going"]
    build = (f"import sys; sys.path.insert(0, {str(scripts)!r}); import common, build\n"
             f"common.CLI[:] = {cli!r}  # headless on this job's own project, never the live app\n"
             f"build.build({str(plan)!r})")
    log = _run(["python3", "-c", build], "build")
    step("built headless: " + log.strip().splitlines()[-1])
    media = project_media(project)
    library_provenance(media)
    ensure_licensed(job_id, media)
    step(f"all {len(media)} media files licensed")
    raw, final = work / "render.mp4", STORAGE / "jobs" / str(job_id) / "final.mp4"
    render(project, raw)
    step("rendered")
    loudnorm(raw, final)
    (work / "build.log").write_text(log)
    return final


if __name__ == "__main__":
    print(edit(int(sys.argv[1])))
