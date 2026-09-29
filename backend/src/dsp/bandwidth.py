"""
Occupied bandwidth estimation.

Algorithm: 99%-power method (a standard occupied-bandwidth definition used in
spectrum regulation, e.g. ITU-R SM.328). We compute the PSD, find the total
power, then find the narrowest frequency window (around the peak) that
contains `power_fraction` of the total power.
"""
from __future__ import annotations
import numpy as np
from src.dsp.psd import compute_psd


def estimate_occupied_bandwidth(iq: np.ndarray, sample_rate_hz: float, power_fraction: float = 0.99):
    freqs, psd_db = compute_psd(iq, sample_rate_hz, nperseg=min(2048, len(iq)))
    psd_linear = 10 ** (psd_db / 10)
    total_power = np.sum(psd_linear)
    cumulative = np.cumsum(psd_linear) / total_power

    lower_idx = np.searchsorted(cumulative, (1 - power_fraction) / 2)
    upper_idx = np.searchsorted(cumulative, 1 - (1 - power_fraction) / 2)
    lower_idx = np.clip(lower_idx, 0, len(freqs) - 1)
    upper_idx = np.clip(upper_idx, 0, len(freqs) - 1)

    bandwidth_hz = float(freqs[upper_idx] - freqs[lower_idx])
    peak_idx = int(np.argmax(psd_db))
    peak_freq_hz = float(freqs[peak_idx])

    return {
        "bandwidth_hz": abs(bandwidth_hz),
        "lower_freq_hz": float(freqs[lower_idx]),
        "upper_freq_hz": float(freqs[upper_idx]),
        "peak_frequency_hz": peak_freq_hz,
        "method": "99pct_power_psd",
    }
