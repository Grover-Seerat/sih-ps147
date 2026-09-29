"""
Carrier/frequency offset estimation.

Two algorithms, selected by modulation family:

1. PSK/QAM (linear digital modulations): raise the signal to the M-th power
   to collapse the M-PSK phase states to a single tone at M*offset, then find
   the FFT peak and divide by M. This is the classic M-th power frequency
   offset estimator used in digital carrier recovery loops.

2. FSK/GFSK/AM/FM (constant/varying envelope, not phase-symmetric): use the
   spectral centroid / PSD peak of the raw signal as an approximate center
   frequency estimate. This is coarser but appropriate given no known phase
   symmetry to exploit.
"""
from __future__ import annotations
import numpy as np
from src.dsp.psd import compute_psd


def estimate_offset_mth_power(iq: np.ndarray, sample_rate_hz: float, m: int) -> float:
    raised = iq ** m
    spectrum = np.fft.fftshift(np.fft.fft(raised))
    freqs = np.fft.fftshift(np.fft.fftfreq(len(raised), d=1.0 / sample_rate_hz))
    peak_idx = np.argmax(np.abs(spectrum))
    return float(freqs[peak_idx] / m)


def estimate_offset_psd_peak(iq: np.ndarray, sample_rate_hz: float) -> float:
    freqs, psd_db = compute_psd(iq, sample_rate_hz, nperseg=min(2048, len(iq)))
    return float(freqs[np.argmax(psd_db)])


def estimate_carrier_offset(iq: np.ndarray, sample_rate_hz: float, modulation_hint: str | None = None) -> dict:
    m_map = {"BPSK": 2, "QPSK": 4, "8PSK": 8, "16QAM": 4}
    if modulation_hint in m_map:
        offset = estimate_offset_mth_power(iq, sample_rate_hz, m_map[modulation_hint])
        method = f"{m_map[modulation_hint]}th_power_estimator"
    else:
        offset = estimate_offset_psd_peak(iq, sample_rate_hz)
        method = "psd_peak"
    return {"carrier_offset_hz": round(offset, 1), "method": method}
