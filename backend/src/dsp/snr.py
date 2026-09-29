"""
SNR estimation from the PSD.

Algorithm: histogram-based noise floor estimation.
  1. Compute PSD in dB.
  2. Assume the MODE of the PSD histogram is the noise floor (most bins are
     noise-only for a narrowband signal in a wideband recording).
  3. Signal power = power in bins that exceed noise_floor + margin.
  4. SNR_dB = 10*log10(signal_power_linear / noise_power_linear).

This is a coarse but standard and explainable spectrum-analysis estimator --
it will not be perfectly accurate, especially at low SNR, and this is stated
explicitly in the result (SOURCE=dsp_estimated, not ground truth).
"""
from __future__ import annotations
import numpy as np
from src.dsp.psd import compute_psd


def estimate_snr(iq: np.ndarray, sample_rate_hz: float, margin_db: float = 3.0) -> dict:
    freqs, psd_db = compute_psd(iq, sample_rate_hz, nperseg=min(1024, len(iq)))

    hist, bin_edges = np.histogram(psd_db, bins=50)
    noise_floor_db = bin_edges[np.argmax(hist)]

    signal_mask = psd_db > (noise_floor_db + margin_db)
    if not np.any(signal_mask):
        signal_mask = psd_db > np.percentile(psd_db, 90)

    psd_linear = 10 ** (psd_db / 10)
    signal_power = float(np.sum(psd_linear[signal_mask]))
    noise_power = float(np.sum(psd_linear[~signal_mask]))
    if noise_power <= 0:
        noise_power = 1e-15

    # scale noise_power estimate to the full band (it was computed only over ~signal_mask bins)
    n_noise_bins = max(np.sum(~signal_mask), 1)
    n_total_bins = len(psd_linear)
    noise_power_scaled = noise_power / n_noise_bins * n_total_bins

    snr_linear = signal_power / max(noise_power_scaled, 1e-15)
    snr_db = 10 * np.log10(max(snr_linear, 1e-12))

    return {
        "snr_db": float(round(snr_db, 2)),
        "noise_floor_db": float(round(noise_floor_db, 2)),
        "method": "psd_histogram_noise_floor",
    }
