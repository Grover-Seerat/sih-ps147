"""FM demodulator: quadrature (phase-difference) discriminator, the standard
non-coherent FM demod technique -- derivative of instantaneous phase is
proportional to the message signal."""
from __future__ import annotations
import numpy as np
from scipy import signal


def demodulate_fm(iq: np.ndarray, sample_rate_hz: float, carrier_offset_hz: float = 0.0) -> dict:
    t = np.arange(len(iq)) / sample_rate_hz
    corrected = iq * np.exp(-1j * 2 * np.pi * carrier_offset_hz * t)

    phase = np.unwrap(np.angle(corrected))
    inst_freq = np.diff(phase) / (2 * np.pi) * sample_rate_hz
    inst_freq = np.concatenate([[inst_freq[0]], inst_freq])

    b, a = signal.butter(4, 0.3)
    audio = signal.filtfilt(b, a, inst_freq)

    peak = np.max(np.abs(audio)) or 1.0
    audio_norm = (audio / peak).astype(np.float64)

    return {"audio": audio_norm[:20000].tolist(), "num_samples": len(audio_norm),
            "audio_sample_rate_hz": sample_rate_hz}
