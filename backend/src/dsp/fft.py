"""FFT helpers -- thin wrappers so the rest of the code doesn't repeat
fftshift/frequency-axis boilerplate."""
from __future__ import annotations
import numpy as np


def compute_fft(iq: np.ndarray, n_fft: int | None = None) -> np.ndarray:
    n_fft = n_fft or len(iq)
    return np.fft.fftshift(np.fft.fft(iq, n=n_fft))


def freq_axis(n_fft: int, sample_rate_hz: float) -> np.ndarray:
    return np.fft.fftshift(np.fft.fftfreq(n_fft, d=1.0 / sample_rate_hz))
