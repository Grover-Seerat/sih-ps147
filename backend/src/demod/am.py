"""AM demodulator: envelope detection (|IQ|), DC removal, low-pass smoothing.
Standard non-coherent AM demod."""
from __future__ import annotations
import numpy as np
from scipy import signal


def demodulate_am(iq: np.ndarray, sample_rate_hz: float, carrier_offset_hz: float = 0.0) -> dict:
    t = np.arange(len(iq)) / sample_rate_hz
    corrected = iq * np.exp(-1j * 2 * np.pi * carrier_offset_hz * t)

    envelope = np.abs(corrected)
    envelope = envelope - np.mean(envelope)

    # light low-pass to remove residual RF/noise ripple, keep audio-band content
    b, a = signal.butter(4, 0.4)
    audio = signal.filtfilt(b, a, envelope)

    peak = np.max(np.abs(audio)) or 1.0
    audio_norm = (audio / peak).astype(np.float64)

    return {"audio": audio_norm[:20000].tolist(), "num_samples": len(audio_norm),
            "audio_sample_rate_hz": sample_rate_hz}
