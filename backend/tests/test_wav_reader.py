import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.io.wav_reader import write_iq_as_wav, read_iq_from_wav, write_audio_wav


def test_iq_wav_roundtrip(tmp_path):
    iq = (np.random.randn(500) + 1j * np.random.randn(500)).astype(np.complex64) * 0.5
    path = tmp_path / "test.wav"
    write_iq_as_wav(iq, 1_000_000, path)
    loaded, sr = read_iq_from_wav(path)
    assert sr == 1_000_000
    assert len(loaded) == 500
    assert np.allclose(loaded, iq, atol=1e-4)


def test_audio_wav_writes(tmp_path):
    audio = np.sin(np.linspace(0, 20, 1000))
    path = tmp_path / "audio.wav"
    write_audio_wav(audio, 8000, path)
    assert path.exists()
