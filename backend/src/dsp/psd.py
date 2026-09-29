"""
Power Spectral Density estimation using Welch's method (scipy.signal.welch).

Welch's method averages the periodogram over overlapping windowed segments,
which trades some frequency resolution for a much lower-variance PSD estimate
than a single FFT -- important because our estimators (bandwidth, SNR, peak
frequency) rely on the PSD shape being stable, not noisy bin-to-bin.
"""
from __future__ import annotations
import numpy as np
from scipy import signal


def compute_psd(iq: np.ndarray, sample_rate_hz: float, nperseg: int = 1024):
    """Returns (freqs_hz, psd_db) both centered (fftshift'd, complex baseband)."""
    nperseg = min(nperseg, len(iq))
    freqs, pxx = signal.welch(
        iq, fs=sample_rate_hz, window="hann", nperseg=nperseg,
        return_onesided=False, scaling="density",
    )
    freqs = np.fft.fftshift(freqs)
    pxx = np.fft.fftshift(pxx)
    pxx_db = 10 * np.log10(pxx + 1e-15)
    return freqs, pxx_db
