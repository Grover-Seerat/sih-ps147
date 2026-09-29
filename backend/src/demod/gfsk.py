"""GFSK demodulator: same discriminator approach as FSK, re-exported under
its own name because the pipeline dispatches by modulation label and the
Gaussian pre-filtering only affects the transmitter, not the receiver
algorithm needed here."""
from __future__ import annotations
from src.demod.fsk import demodulate_fsk


def demodulate_gfsk(iq, sample_rate_hz, symbol_rate_hz, carrier_offset_hz=0.0):
    return demodulate_fsk(iq, sample_rate_hz, symbol_rate_hz, carrier_offset_hz)
