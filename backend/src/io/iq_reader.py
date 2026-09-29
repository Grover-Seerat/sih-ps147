"""
Reader/writer for raw complex64 .iq files.

Format: raw binary, little-endian, interleaved float32 I,Q,I,Q,... i.e.
numpy dtype `complex64`. No header -- sample rate etc. must come from a
sidecar metadata.json/.jsonl entry, exactly like real-world SIGINT capture
tools (e.g. GNU Radio file sinks) which also store raw IQ with no header.

If no metadata is available for a given .iq file, the sample rate is
UNKNOWN and must be treated as such (see universal_reader.py).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np


def read_iq(path: str | Path) -> np.ndarray:
    """Read a raw complex64 .iq file into a numpy complex64 array."""
    data = np.fromfile(str(path), dtype=np.complex64)
    return data


def write_iq(iq: np.ndarray, path: str | Path) -> None:
    iq = iq.astype(np.complex64)
    iq.tofile(str(path))
