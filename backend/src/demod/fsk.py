"""FSK/GFSK demodulator: carrier-offset correction + instantaneous-frequency
discrimination (differentiate the phase), then threshold at zero to recover
bits. Works for both FSK and GFSK (Gaussian filtering only smooths the
transitions, the discriminator approach is the same)."""
from __future__ import annotations
import numpy as np


def demodulate_fsk(iq: np.ndarray, sample_rate_hz: float, symbol_rate_hz: float,
                    carrier_offset_hz: float = 0.0) -> dict:
    t = np.arange(len(iq)) / sample_rate_hz
    corrected = iq * np.exp(-1j * 2 * np.pi * carrier_offset_hz * t)

    phase = np.unwrap(np.angle(corrected))
    inst_freq = np.diff(phase) / (2 * np.pi) * sample_rate_hz
    inst_freq = np.concatenate([[inst_freq[0]], inst_freq])

    sps = max(int(round(sample_rate_hz / symbol_rate_hz)), 1)
    # average instantaneous frequency over each symbol period for robustness
    n_symbols = len(inst_freq) // sps
    symbol_freqs = inst_freq[: n_symbols * sps].reshape(n_symbols, sps).mean(axis=1)
    bits = (symbol_freqs > np.median(symbol_freqs)).astype(int)

    return {"bits": bits.tolist()[:2000], "num_bits": len(bits), "samples_per_symbol": sps}
