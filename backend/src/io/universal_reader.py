"""
Universal file reader: normalizes .iq or .wav (or real audio .wav) input into
a numpy.ndarray[complex64], and reports where the sample rate came from.

This is the single entry point the pipeline/API should call so the rest of
the system never has to know about file formats.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import numpy as np

from src.io.iq_reader import read_iq
from src.io.wav_reader import read_iq_from_wav


@dataclass
class LoadedSignal:
    iq: np.ndarray                 # complex64
    sample_rate_hz: Optional[float]
    sample_rate_source: str        # "file_metadata" | "wav_header" | "sidecar_json" | "unknown"
    format: str                    # "iq" | "wav"
    path: str


def _find_sidecar_metadata(path: Path) -> Optional[dict]:
    """Look for sample_id.json or a matching row in metadata.jsonl next to the file."""
    candidate = path.with_suffix(".json")
    if candidate.exists():
        return json.loads(candidate.read_text())

    meta_dir = path.parent.parent.parent / "metadata"
    jsonl = meta_dir / "metadata.jsonl"
    if jsonl.exists():
        target_stem = path.stem
        with open(jsonl) as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("sample_id") == target_stem:
                    return rec
    return None


def load_signal(path: str | Path, assumed_sample_rate_hz: Optional[float] = None) -> LoadedSignal:
    path = Path(path)
    suffix = path.suffix.lower()

    sidecar = _find_sidecar_metadata(path)

    if suffix == ".iq":
        iq = read_iq(path)
        if sidecar and sidecar.get("sample_rate_hz"):
            return LoadedSignal(iq, float(sidecar["sample_rate_hz"]), "sidecar_json", "iq", str(path))
        if assumed_sample_rate_hz:
            return LoadedSignal(iq, float(assumed_sample_rate_hz), "user_supplied", "iq", str(path))
        # IMPORTANT: raw IQ with no sidecar metadata genuinely does NOT carry a
        # sample rate. We do not guess. Downstream code must handle None.
        return LoadedSignal(iq, None, "unknown", "iq", str(path))

    elif suffix == ".wav":
        try:
            iq, sr = read_iq_from_wav(path)
            return LoadedSignal(iq, float(sr), "wav_header", "wav", str(path))
        except ValueError:
            # mono real-audio wav -- treat as real-valued "IQ" with Q=0 so the
            # rest of the pipeline still works (useful for AM/FM audio inspection)
            from scipy.io import wavfile
            sr, data = wavfile.read(str(path))
            if data.ndim > 1:
                data = data[:, 0]
            if np.issubdtype(data.dtype, np.integer):
                data = data.astype(np.float32) / np.iinfo(data.dtype).max
            iq = data.astype(np.complex64)
            return LoadedSignal(iq, float(sr), "wav_header", "wav", str(path))
    else:
        raise ValueError(f"Unsupported file extension: {suffix}. Expected .iq or .wav")
