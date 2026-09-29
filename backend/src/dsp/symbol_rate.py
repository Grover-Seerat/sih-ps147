"""
Approximate symbol-rate estimation.

Algorithm: spectral-line / cyclostationary method.
  1. Compute the instantaneous power |iq[n]|^2 (or magnitude for FSK-like
     constant-envelope signals, the phase-derivative squared works better --
     we use amplitude^2 here as a modulation-agnostic default).
  2. FFT the power waveform. Digital modulations produce a spectral line at
     the symbol rate due to the periodicity introduced by pulse shaping /
     symbol transitions (this is the standard "delay-and-multiply" /
     squaring symbol-timing-recovery principle, simplified to a single FFT).
  3. Report the strongest peak in a plausible symbol-rate search range as the
     estimate.

This is an ESTIMATE (dsp_estimated), not exact -- pulse shaping roll-off and
noise change the exact peak location, especially at low SNR.
"""
from __future__ import annotations
import numpy as np


def estimate_symbol_rate(iq: np.ndarray, sample_rate_hz: float,
                          min_symbol_rate_hz: float = 5_000, max_symbol_rate_hz: float = 500_000) -> dict:
    power = np.abs(iq) ** 2
    power = power - np.mean(power)
    spectrum = np.abs(np.fft.rfft(power))
    freqs = np.fft.rfftfreq(len(power), d=1.0 / sample_rate_hz)

    mask = (freqs >= min_symbol_rate_hz) & (freqs <= max_symbol_rate_hz)
    if not np.any(mask):
        return {"symbol_rate_hz": None, "confidence": 0.0, "method": "power_spectrum_line_search"}

    sub_spec = spectrum[mask]
    sub_freqs = freqs[mask]
    peak_idx = int(np.argmax(sub_spec))
    peak_freq = float(sub_freqs[peak_idx])

    # crude confidence: peak prominence relative to median of the search band
    median_level = np.median(sub_spec) + 1e-9
    prominence = sub_spec[peak_idx] / median_level
    confidence = float(np.clip((prominence - 2) / 10, 0, 1))

    return {"symbol_rate_hz": round(peak_freq, 1), "confidence": round(confidence, 2),
            "method": "power_spectrum_line_search"}
