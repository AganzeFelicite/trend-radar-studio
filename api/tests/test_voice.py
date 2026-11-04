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
