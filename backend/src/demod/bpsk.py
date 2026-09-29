"""BPSK demodulator: matched-filter-free simple coherent demod for the demo.

Steps: 1) coarse carrier offset correction (from DSP estimate),
       2) downsample at estimated samples-per-symbol,
       3) slice sign(I) -> bits.
This is a simplified, non-loop-based demodulator suitable for showing
"recovered bits" in a hackathon demo, not a production-grade timing/carrier
recovery loop (documented explicitly as a limitation).
"""
from __future__ import annotations
import numpy as np


def demodulate_bpsk(iq: np.ndarray, sample_rate_hz: float, symbol_rate_hz: float,
                     carrier_offset_hz: float = 0.0) -> dict:
    t = np.arange(len(iq)) / sample_rate_hz
    corrected = iq * np.exp(-1j * 2 * np.pi * carrier_offset_hz * t)

    sps = max(int(round(sample_rate_hz / symbol_rate_hz)), 1)
    # phase-correct using the mean phase of the strongest component
    mean_phase = np.angle(np.mean(corrected ** 2)) / 2
    corrected *= np.exp(-1j * mean_phase)

    symbols = corrected[::sps]
    bits = (symbols.real > 0).astype(int)
    return {"bits": bits.tolist()[:2000], "num_bits": len(bits), "samples_per_symbol": sps}
