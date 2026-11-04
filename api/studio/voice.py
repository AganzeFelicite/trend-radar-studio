"""Free local TTS: Kokoro (Apache-2.0) on onnxruntime. The voice is an original blend of preset
voices, never a clone or imitation of a real person (brief §1)."""

import os
import wave
from functools import cache
from pathlib import Path

import numpy as np
from kokoro_onnx import Kokoro

from studio.config import CHARACTER_NAME

MODELS = Path(os.environ.get("KOKORO_DIR", Path(__file__).parents[2] / "models" / "kokoro"))

# {preset: weight}, speed. "hype" is the channel voice (V2.3, 2026-11-04); the others stay for comparison.
VOICE = "hype"
VOICES = {
    "anchor": ({"am_michael": 0.7, "am_fenrir": 0.3}, 1.10),
    "hype": ({"am_puck": 0.6, "am_michael": 0.4}, 1.15),
    "warm": ({"am_fenrir": 0.5, "am_onyx": 0.5}, 1.05),
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


def synthesize(text: str, out: Path, voice: str = VOICE) -> tuple[float, list[dict]]:
    """Write a mono 16-bit WAV of `text`; returns (seconds, mouth cues)."""
    weights, speed = VOICES[voice]
    style = sum(_tts().get_voice_style(name) * w for name, w in weights.items())
    audio, rate, timings = _tts().create_timed(text, voice=style, speed=speed, lang="en-us")
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(pcm.tobytes())
    return len(audio) / rate, mouth_cues(timings)


SAMPLE = (
    f"Ping check — {CHARACTER_NAME}'s online! Three trends are lighting up the radar today, "
    "and number two surprised even me. "
    "Fetching the data… okay, this one is a real loot drop for creators. "
    f"That's the news for today. {CHARACTER_NAME}, logging off. Stay locked in."
)

if __name__ == "__main__":
    import json
    import sys

    repo = Path(__file__).parents[2]
    if sys.argv[1:] == ["samples"]:  # V2.3: one sample per candidate voice
        out_dir = repo / "assets" / "voice"
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in VOICES:
            print(f"{name}: {synthesize(SAMPLE, out_dir / f'{name}.wav', name)[0]:.1f}s")
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
