"""QPSK demodulator: carrier-offset correction + 4th-power phase de-rotation
+ symbol slicing into Gray-coded bit pairs. Simplified (no PLL/timing loop),
documented limitation for future work."""
from __future__ import annotations
import numpy as np


def demodulate_qpsk(iq: np.ndarray, sample_rate_hz: float, symbol_rate_hz: float,
                     carrier_offset_hz: float = 0.0) -> dict:
    t = np.arange(len(iq)) / sample_rate_hz
    corrected = iq * np.exp(-1j * 2 * np.pi * carrier_offset_hz * t)

    mean_phase = np.angle(np.mean(corrected ** 4)) / 4
    corrected *= np.exp(-1j * mean_phase)

    sps = max(int(round(sample_rate_hz / symbol_rate_hz)), 1)
    symbols = corrected[::sps]

    bits = []
    inv_gray = {(1, 1): (0, 0), (-1, 1): (0, 1), (-1, -1): (1, 1), (1, -1): (1, 0)}
    for s in symbols:
        key = (1 if s.real >= 0 else -1, 1 if s.imag >= 0 else -1)
        bits.extend(inv_gray[key])

    return {"bits": bits[:2000], "num_bits": len(bits), "samples_per_symbol": sps}
