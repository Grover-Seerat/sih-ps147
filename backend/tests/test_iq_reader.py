import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.io.iq_reader import read_iq, write_iq


def test_write_read_roundtrip(tmp_path):
    iq = (np.random.randn(1000) + 1j * np.random.randn(1000)).astype(np.complex64)
    path = tmp_path / "test.iq"
    write_iq(iq, path)
    loaded = read_iq(path)
    assert loaded.dtype == np.complex64
    assert len(loaded) == 1000
    assert np.allclose(loaded, iq)
