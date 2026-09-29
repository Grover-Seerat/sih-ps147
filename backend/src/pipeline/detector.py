"""
Signal detection in a wideband recording.

Algorithm:
  1. Compute PSD (Welch).
  2. Estimate noise floor as the median of the PSD (robust to a few strong
     signals occupying a small fraction of the band).
  3. Threshold: bins > noise_floor + margin_db are "occupied".
  4. Group contiguous occupied bins into regions (connected-component style
     1D scan), merging small gaps to avoid splitting one signal into pieces
     due to spectral scalloping.
  5. Discard regions narrower than min_bandwidth_hz (likely spectral leakage,
     not a real signal).

Returns a list of {start_frequency_hz, stop_frequency_hz, center_frequency_hz}
exactly as specified in the design brief.
"""
from __future__ import annotations
import numpy as np
from src.dsp.psd import compute_psd


def detect_signals(iq: np.ndarray, sample_rate_hz: float, margin_db: float = 6.0,
                    min_bandwidth_hz: float = 5_000, max_gap_bins: int = 3) -> list[dict]:
    freqs, psd_db = compute_psd(iq, sample_rate_hz, nperseg=min(2048, len(iq)))

    noise_floor_db = float(np.median(psd_db))
    occupied = psd_db > (noise_floor_db + margin_db)

    # merge small gaps
    occupied = occupied.copy()
    gap_start = None
    for idx, val in enumerate(occupied):
        if not val:
            if gap_start is None:
                gap_start = idx
        else:
            if gap_start is not None and (idx - gap_start) <= max_gap_bins:
                occupied[gap_start:idx] = True
            gap_start = None

    regions = []
    in_region = False
    start_idx = None
    for idx, val in enumerate(occupied):
        if val and not in_region:
            in_region = True
            start_idx = idx
        elif not val and in_region:
            in_region = False
            regions.append((start_idx, idx - 1))
    if in_region:
        regions.append((start_idx, len(occupied) - 1))

    detections = []
    for start_idx, stop_idx in regions:
        f_start = float(freqs[start_idx])
        f_stop = float(freqs[stop_idx])
        bandwidth = f_stop - f_start
        if bandwidth < min_bandwidth_hz:
            continue
        peak_idx = start_idx + int(np.argmax(psd_db[start_idx:stop_idx + 1]))
        detections.append({
            "start_frequency_hz": round(f_start, 1),
            "stop_frequency_hz": round(f_stop, 1),
            "center_frequency_hz": round((f_start + f_stop) / 2, 1),
            "bandwidth_hz": round(bandwidth, 1),
            "peak_power_db": round(float(psd_db[peak_idx]), 2),
            "peak_frequency_hz": round(float(freqs[peak_idx]), 1),
        })

    detections.sort(key=lambda d: d["center_frequency_hz"])
    return detections


def extract_signal_region(iq: np.ndarray, sample_rate_hz: float, center_frequency_hz: float,
                           bandwidth_hz: float, guard_factor: float = 1.5) -> np.ndarray:
    """Frequency-shift the region of interest to baseband and low-pass/decimate
    so downstream DSP/ML sees an isolated single-signal baseband IQ stream."""
    from scipy import signal as sp_signal

    t = np.arange(len(iq)) / sample_rate_hz
    shifted = iq * np.exp(-1j * 2 * np.pi * center_frequency_hz * t)

    cutoff = min((bandwidth_hz * guard_factor) / 2, sample_rate_hz / 2 * 0.95)
    nyq = sample_rate_hz / 2
    normalized_cutoff = max(cutoff / nyq, 0.01)
    b, a = sp_signal.butter(6, normalized_cutoff)
    filtered = sp_signal.filtfilt(b, a, shifted)

    return filtered.astype(np.complex64)
