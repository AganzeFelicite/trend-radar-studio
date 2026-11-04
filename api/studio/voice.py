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

# V2.3 candidates: {preset: weight}, speed. The one you pick becomes the channel voice.
VOICES = {
    "anchor": ({"am_michael": 0.7, "am_fenrir": 0.3}, 1.10),
    "hype": ({"am_puck": 0.6, "am_michael": 0.4}, 1.15),
    "warm": ({"am_fenrir": 0.5, "am_onyx": 0.5}, 1.05),
}


@cache
def _tts() -> Kokoro:
    return Kokoro(str(MODELS / "kokoro-v1.0.onnx"), str(MODELS / "voices-v1.0.bin"))


def synthesize(text: str, out: Path, voice: str = "anchor") -> float:
    """Write a mono 16-bit WAV of `text`; returns its length in seconds."""
    weights, speed = VOICES[voice]
    style = sum(_tts().get_voice_style(name) * w for name, w in weights.items())
    audio, rate = _tts().create(text, voice=style, speed=speed, lang="en-us")
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(pcm.tobytes())
    return len(audio) / rate


SAMPLE = (
    f"Ping check — {CHARACTER_NAME}'s online! Three trends are lighting up the radar today, "
    "and number two surprised even me. "
    "Fetching the data… okay, this one is a real loot drop for creators. "
    f"That's the news for today. {CHARACTER_NAME}, logging off. Stay locked in."
)

if __name__ == "__main__":  # V2.3: one sample per candidate voice
    out_dir = Path(__file__).parents[2] / "assets" / "voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in VOICES:
        seconds = synthesize(SAMPLE, out_dir / f"{name}.wav", name)
        print(f"{name}: {seconds:.1f}s")
