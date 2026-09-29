"""Spectrogram (waterfall) computation, with output decimation for the frontend."""
from __future__ import annotations
import numpy as np
from scipy import signal


def compute_spectrogram(iq: np.ndarray, sample_rate_hz: float, nperseg: int = 256,
                         max_time_bins: int = 200, max_freq_bins: int = 256):
    nperseg = min(nperseg, len(iq))
    freqs, times, sxx = signal.spectrogram(
        iq, fs=sample_rate_hz, window="hann", nperseg=nperseg,
        noverlap=nperseg // 2, return_onesided=False, mode="magnitude",
    )
    freqs = np.fft.fftshift(freqs)
    sxx = np.fft.fftshift(sxx, axes=0)
    sxx_db = 20 * np.log10(sxx + 1e-12)

    # decimate for frontend friendliness
    t_step = max(1, sxx_db.shape[1] // max_time_bins)
    f_step = max(1, sxx_db.shape[0] // max_freq_bins)
    sxx_db_small = sxx_db[::f_step, ::t_step]
    freqs_small = freqs[::f_step]
    times_small = times[::t_step]

    return {
        "frequencies_hz": freqs_small.tolist(),
        "times_s": times_small.tolist(),
        "power_db": sxx_db_small.round(2).tolist(),  # shape [freq, time]
    }
