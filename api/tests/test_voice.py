import wave

import pytest

from studio import voice

needs_model = pytest.mark.skipif(not (voice.MODELS / "kokoro-v1.0.onnx").exists(), reason="Kokoro model not downloaded")


@needs_model
def test_synthesize_writes_audio(tmp_path):
    out = tmp_path / "line.wav"
    seconds = voice.synthesize("Ping check, the radar is online.", out)
    assert 1 < seconds < 6
    with wave.open(str(out)) as f:
        assert f.getnchannels() == 1 and f.getnframes() / f.getframerate() == pytest.approx(seconds)
