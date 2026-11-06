"""Free local TTS: Kokoro (Apache-2.0) on onnxruntime. The voice is an original blend of preset
voices, never a clone or imitation of a real person (brief §1)."""

import json
import os
import re
import subprocess
import wave
from difflib import SequenceMatcher
from functools import cache
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro
from sqlalchemy import select
from sqlalchemy.orm import Session

from studio.config import CHARACTER_NAME, STORAGE, WHISPER_MODEL, WHISPER_PYTHON
from studio.costs import ensure_budget, record_cost
from studio.db import Asset, Script, engine

MODELS = Path(os.environ.get("KOKORO_DIR", Path(__file__).parents[2] / "models" / "kokoro"))

# {preset: weight}, speed. "hype" is the channel voice (V2.3, 2026-11-04); the others stay for comparison.
VOICE = "coach"  # D22 (2026-11-06); "hype" was GameReporter's
VOICES = {
    "anchor": ({"am_michael": 0.7, "am_fenrir": 0.3}, 1.10),
    "hype": ({"am_puck": 0.6, "am_michael": 0.4}, 1.15),
    "warm": ({"am_fenrir": 0.5, "am_onyx": 0.5}, 1.05),
    # V7.1 candidates (docs/CHARACTER-CANDIDATES.md): original blends, one per character
    "patch": ({"am_adam": 0.7, "af_sky": 0.3}, 1.2),
    "auntie": ({"af_bella": 0.5, "af_sarah": 0.5}, 1.0),
    "coach": ({"am_michael": 0.5, "am_onyx": 0.5}, 1.1),
}

# 10 s test line per candidate and where a reaction pose lands (first word of the stretch, pose).
CAST = {
    "patch": ("Patch notes incoming. Version one point oh point seven: Rockstar dropped new screenshots. "
              "Severity: I can't breathe. Known issues: none. Patch out.",
              [("Severity", "shocked"), ("Known", "thinking"), ("Patch out", "celebrating")]),
    "auntie": ("Come, come, sit. You won't believe this. Rockstar posted new pictures and I have not slept. "
               "Okay, go and play. And drink water. Auntie out.",
               [("Rockstar", "shocked"), ("drink", "laughing")]),
    "coach": ("Huddle up! Thirteen days out. Scouting report: Rockstar posted new screenshots. Official. "
              "Hydrate. Pre-load. Coach out.",
              [("Huddle", "celebrating"), ("Official", "shocked"), ("Hydrate", "thinking")]),
}


@cache
def _tts() -> Kokoro:
    return Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))


# Kokoro phonemes (misaki IPA set; A=eɪ I=aɪ O=oʊ W=aʊ Y=ɔɪ) -> mouth shapes drawn in renderer/src/Reporter.tsx
# (Rhubarb Lip Sync's A-H/X set, so Rhubarb can replace this later without touching the renderer).
_SHAPES = {
    "A": "mbp",
    "B": "kgɡtdnszʃʒʧʤjŋiɾʔhç",
    "C": "ɛæeʌəɪᵻA",
    "D": "ɑaɐI",
    "E": "ɔɜɚɝɹO",
    "F": "uʊwWY",
    "G": "fv",
    "H": "lθð",
}
_MOUTH = {ch: shape for shape, chars in _SHAPES.items() for ch in chars}
_MODIFIERS = "ˈˌːʰ"  # stress/length marks keep the current shape
MIN_CUE = 2 / 30  # anything shorter flickers at 30 fps


def mouth_cues(timings) -> list[dict]:
    """[{start, end, value}] mouth cues from Kokoro phoneme timings; silence and punctuation are X (rest)."""
    raw: list[dict] = []
    for p in timings:
        shape = raw[-1]["value"] if raw and p.phoneme in _MODIFIERS else _MOUTH.get(p.phoneme, "X")
        if raw and p.start - raw[-1]["end"] > 1e-3:  # a pause between batches
            raw.append({"start": raw[-1]["end"], "end": p.start, "value": "X"})
        if raw and raw[-1]["value"] == shape:
            raw[-1]["end"] = p.end
        else:
            raw.append({"start": p.start, "end": p.end, "value": shape})
    cues: list[dict] = []
    for c in raw:
        if cues and (c["end"] - c["start"] < MIN_CUE or cues[-1]["value"] == c["value"]):
            cues[-1]["end"] = c["end"]
        else:
            cues.append(dict(c))
    return [{"start": round(c["start"], 3), "end": round(c["end"], 3), "value": c["value"]} for c in cues]


# How a line is read aloud; captions and the script keep the original text.
SPEECH = [(r"#(?=\d)", "number "), (r"→", " to "), (r"(?<=\d)x\b", " times"), (r"\bvs\.?(?=\s)", "versus")]


def spoken(text: str) -> str:
    for pattern, repl in SPEECH:
        text = re.sub(pattern, repl, text)
    return text


def _speak(text: str, voice: str = VOICE) -> tuple[np.ndarray, int, list[dict]]:
    weights, speed = VOICES[voice]
    style = sum(_tts().get_voice_style(name) * w for name, w in weights.items())
    audio, rate, timings = _tts().create_timed(spoken(text), voice=style, speed=speed, lang="en-us")
    return audio, rate, mouth_cues(timings)


def _write(audio: np.ndarray, rate: int, out: Path) -> None:
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())


def synthesize(text: str, out: Path, voice: str = VOICE) -> tuple[float, list[dict]]:
    """Write a mono 16-bit WAV of `text`; returns (seconds, mouth cues)."""
    audio, rate, cues = _speak(text, voice)
    _write(audio, rate, out)
    return len(audio) / rate, cues


def words(wav: Path) -> list[dict]:
    """Word timestamps from local mlx-whisper (the model your FilmCraft pipeline uses), for captions and checks."""
    code = ("import json, sys, mlx_whisper\n"
            "r = mlx_whisper.transcribe(sys.argv[1], path_or_hf_repo=sys.argv[2], language='en', word_timestamps=True,"
            " condition_on_previous_text=False)\n"
            "json.dump([{'word': w['word'].strip(), 'start': round(w['start'], 3), 'end': round(w['end'], 3)}"
            " for s in r['segments'] for w in s['words']], sys.stdout)")
    run = subprocess.run([os.path.expanduser(WHISPER_PYTHON), "-c", code, str(wav), WHISPER_MODEL],
                         capture_output=True, text=True, timeout=600)
    if run.returncode:
        raise RuntimeError(f"mlx-whisper failed: {run.stderr[-500:]}")
    return json.loads(run.stdout)


_DIGITS = {w: str(i) for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve "
                                          "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def _tokens(text: str) -> list[str]:
    """Comparable words: "pre-load" = "preload", "six" = "6", "1." = "1" (spelling isn't a misreading)."""
    raw = re.findall(r"[a-z0-9.%']+", spoken(text).lower().replace("-", ""))
    return [_DIGITS.get(t, t) for t in (r.strip(".'") for r in raw) if t]


def match(script_text: str, heard: list[dict]) -> tuple[float, list[str]]:
    """How closely whisper's words match the script (1.0 = word for word), plus the differing stretches."""
    a, b = _tokens(script_text), _tokens(" ".join(w["word"] for w in heard))
    sm = SequenceMatcher(None, a, b, autojunk=False)
    diffs = [f"{' '.join(a[i1:i2]) or '∅'} → {' '.join(b[j1:j2]) or '∅'}" for op, i1, i2, j1, j2 in sm.get_opcodes()
             if op != "equal"]
    return round(sm.ratio(), 3), diffs


def caption_words(lines: list[str], heard: list[dict]) -> list[dict]:
    """The script's own words, timed by whisper: captions show "#1" and the host's name exactly as written,
    never whisper's spelling. Aligned on characters, so whisper splitting or merging words doesn't matter."""
    orig = [w for line in lines for w in line.split()]
    a = [(ch, i) for i, w in enumerate(orig) for ch in "".join(_tokens(w))]
    b = [(ch, j) for j, w in enumerate(heard) for ch in "".join(_tokens(w["word"]))]
    span: dict[int, list[float]] = {}
    sm = SequenceMatcher(None, "".join(c for c, _ in a), "".join(c for c, _ in b), autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = heard[b[blk.b + k][1]]
            s = span.setdefault(a[blk.a + k][1], [w["start"], w["end"]])
            s[0], s[1] = min(s[0], w["start"]), max(s[1], w["end"])
    return [{"word": re.sub(r"[()]", "", orig[i]), "start": s, "end": e} for i, (s, e) in sorted(span.items())]


PAUSE = 0.3  # seconds of silence between scenes (studio/script.py estimates with the same value)
LICENSE = "Apache-2.0 (Kokoro-82M model and voices); original blend, no cloned or imitated voice"


def voice_track(job_id: int, voice: str = VOICE) -> dict:
    """The job's latest script -> storage/jobs/<id>/voice.wav (one track, scenes in order) + voice.json with real
    scene times, mouth cues and whisper word timestamps. Logged in provenance and costs ($0, local)."""
    ensure_budget("tts", 0)
    with Session(engine) as s:
        body = s.scalars(select(Script.body).where(Script.job_id == job_id).order_by(Script.version.desc())).first()
    if body is None:
        raise ValueError(f"job {job_id} has no script yet")
    out = STORAGE / "jobs" / str(job_id)
    out.mkdir(parents=True, exist_ok=True)
    pieces, scenes, cues, t, rate = [], [], [], 0.0, 24000
    for scene in body["scenes"]:
        audio, rate, c = _speak(scene["line"], voice)
        seconds = len(audio) / rate
        scenes.append({**scene, "start": round(t, 3), "end": round(t + seconds, 3)})
        cues += [{**x, "start": round(x["start"] + t, 3), "end": round(x["end"] + t, 3)} for x in c]
        pieces += [audio, np.zeros(int(PAUSE * rate), np.float32)]
        t += seconds + PAUSE
    track = np.concatenate(pieces[:-1])
    _write(track, rate, out / "voice.wav")
    duration = round(len(track) / rate, 3)
    heard = words(out / "voice.wav")
    ratio, diffs = match(" ".join(x["line"] for x in body["scenes"]), heard)
    result = {"audio": "voice.wav", "duration": duration, "voice": voice, "scenes": scenes, "cues": cues,
              "words": heard, "whisper_match": ratio, "whisper_diffs": diffs}
    (out / "voice.json").write_text(json.dumps(result, ensure_ascii=False))
    weights, speed = VOICES[voice]
    with Session(engine) as s, s.begin():
        s.add(Asset(job_id=job_id, kind="voice", source="tts", source_ref=f"kokoro-onnx · {voice} {weights} speed {speed}",
                    license=LICENSE, license_url="https://huggingface.co/hexgrad/Kokoro-82M", path=str(out / "voice.wav"),
                    meta={"seconds": duration, "scenes": len(scenes)}))
    record_cost("tts", "kokoro-local", 0, job_id=job_id, quantity=duration, unit="seconds", note=f"{voice}, local, free")
    return result


SAMPLE = (
    f"Ping check — {CHARACTER_NAME}'s online! Three trends are lighting up the radar today, "
    "and number two surprised even me. "
    "Fetching the data… okay, this one is a real loot drop for creators. "
    f"That's the news for today. {CHARACTER_NAME}, logging off. Stay locked in."
)

if __name__ == "__main__":
    import sys

    repo = Path(__file__).parents[2]
    if sys.argv[1:2] and sys.argv[1].isdigit():  # V3.5: a job's voice track
        r = voice_track(int(sys.argv[1]))
        print(f"{r['duration']:.1f}s, {len(r['scenes'])} scenes, {len(r['words'])} words, whisper match {r['whisper_match']}")
        for sc in r["scenes"]:
            print(f"  {sc['start']:6.2f}-{sc['end']:6.2f} {sc['shot']:8} {sc['line']}")
        for d in r["whisper_diffs"]:
            print(f"  heard differently: {d}")
    elif sys.argv[1:] == ["samples"]:  # V2.3: one sample per candidate voice
        out_dir = repo / "assets" / "voice"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in VOICES:
            print(f"{name}: {synthesize(SAMPLE, out_dir / f'{name}.wav', name)[0]:.1f}s")
    elif sys.argv[1:] == ["cast"]:  # V7.1: one ~10 s test per candidate -> renderer/public/test/<who>.wav + props
        pub = repo / "renderer" / "public" / "test"
        pub.mkdir(parents=True, exist_ok=True)
        (repo / "renderer" / "out").mkdir(exist_ok=True)
        for who, (text, marks) in CAST.items():
            seconds, cues = synthesize(text, pub / f"{who}.wav", who)
            poses = []
            for word, pose in marks:  # ponytail: char-proportion guess, fine for a test
                at = round(seconds * text.index(word) / len(text), 2)
                poses.append({"start": at, "end": round(at + 1.6, 2), "pose": pose})
            props = {"audio": f"test/{who}.wav", "duration": seconds, "cues": cues, "poses": poses, "who": who}
            (repo / "renderer" / "out" / f"{who}-props.json").write_text(json.dumps(props))
            print(f"{who}: {seconds:.1f}s, {len(cues)} mouth cues")
    else:  # V2.4: ~10 s talking-clip test -> renderer/public/test/ + props for `remotion render`
        text = (f"Ping check — {CHARACTER_NAME}'s online! Three trends are lighting up the radar today, "
                "and number two surprised even me. Roll the tape!")
        pub = repo / "renderer" / "public" / "test"
        pub.mkdir(parents=True, exist_ok=True)
        seconds, cues = synthesize(text, pub / "line.wav")
        at = seconds * text.index("surprised") / len(text)  # ponytail: char-proportion guess, fine for a test
        props = {"audio": "test/line.wav", "duration": seconds, "cues": cues,
                 "poses": [{"start": round(at, 2), "end": round(at + 1.6, 2), "pose": "shocked"}]}
        (repo / "renderer" / "out").mkdir(exist_ok=True)
        (repo / "renderer" / "out" / "props.json").write_text(json.dumps(props))
        print(f"{seconds:.1f}s, {len(cues)} mouth cues, shocked at {at:.1f}s")
