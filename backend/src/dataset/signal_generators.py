"""
Physically-meaningful synthetic complex-baseband IQ signal generators.

Every generator returns a numpy.ndarray[np.complex64] plus a dict of the
ground-truth parameters actually used, so the caller can build metadata
that is 100% accurate (because we generated the signal, we KNOW these
values -- this is the one case where "ground truth" is legitimate).
"""
from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rrc_filter(beta: float, span_symbols: int, sps: int) -> np.ndarray:
    """Root-raised-cosine pulse shaping filter (time domain taps)."""
    n = np.arange(-span_symbols * sps / 2, span_symbols * sps / 2 + 1)
    t = n / sps
    h = np.zeros_like(t)
    for i, ti in enumerate(t):
        if np.isclose(ti, 0.0):
            h[i] = 1.0 - beta + 4 * beta / np.pi
        elif beta != 0 and np.isclose(abs(ti), 1 / (4 * beta)):
            h[i] = (beta / np.sqrt(2)) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta))
            )
        else:
            num = np.sin(np.pi * ti * (1 - beta)) + 4 * beta * ti * np.cos(np.pi * ti * (1 + beta))
            den = np.pi * ti * (1 - (4 * beta * ti) ** 2)
            h[i] = num / den
    h /= np.sqrt(np.sum(h ** 2))
    return h.astype(np.float64)


def gaussian_filter(bt: float, span_symbols: int, sps: int) -> np.ndarray:
    """Gaussian filter taps for GFSK, parameterized by BT (bandwidth-time product)."""
    n = np.arange(-span_symbols * sps / 2, span_symbols * sps / 2 + 1)
    t = n / sps
    alpha = np.sqrt(np.log(2) / 2) / bt
    h = (1 / (np.sqrt(2 * np.pi) * alpha)) * np.exp(-(t ** 2) / (2 * alpha ** 2))
    h /= np.sum(h)
    return h


def apply_awgn(iq: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    sig_power = np.mean(np.abs(iq) ** 2)
    if sig_power == 0:
        sig_power = 1e-12
    snr_linear = 10 ** (snr_db / 10)
    noise_power = sig_power / snr_linear
    noise = rng.normal(0, np.sqrt(noise_power / 2), iq.shape) + 1j * rng.normal(
        0, np.sqrt(noise_power / 2), iq.shape
    )
    return iq + noise


def apply_rayleigh(iq: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Flat Rayleigh fading (single-tap, slowly varying)."""
    n_blocks = max(1, len(iq) // 200)
    block_len = int(np.ceil(len(iq) / n_blocks))
    gains = (rng.normal(0, 1, n_blocks) + 1j * rng.normal(0, 1, n_blocks)) / np.sqrt(2)
    gains = np.repeat(gains, block_len)[: len(iq)]
    return iq * gains


def apply_multipath(iq: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Simple 2-3 tap static multipath channel."""
    n_taps = rng.integers(2, 4)
    delays = np.sort(rng.integers(0, 8, n_taps))
    gains = (rng.normal(0, 1, n_taps) + 1j * rng.normal(0, 1, n_taps))
    gains[0] = max(abs(gains[0]), 0.7)  # dominant tap
    gains /= np.sqrt(np.sum(np.abs(gains) ** 2))
    out = np.zeros_like(iq)
    for d, g in zip(delays, gains):
        shifted = np.roll(iq, d)
        if d > 0:
            shifted[:d] = 0
        out += g * shifted
    return out


def apply_carrier_offset_and_phase(
    iq: np.ndarray, sample_rate_hz: float, carrier_offset_hz: float, phase_offset_rad: float
) -> np.ndarray:
    t = np.arange(len(iq)) / sample_rate_hz
    return iq * np.exp(1j * (2 * np.pi * carrier_offset_hz * t + phase_offset_rad))


def apply_timing_offset(symbols: np.ndarray, timing_offset: float) -> np.ndarray:
    """Fractional symbol timing offset via linear interpolation before pulse shaping."""
    if timing_offset == 0:
        return symbols
    idx = np.arange(len(symbols))
    shifted_idx = idx + timing_offset
    shifted_idx = np.clip(shifted_idx, 0, len(symbols) - 1)
    real = np.interp(shifted_idx, idx, symbols.real)
    imag = np.interp(shifted_idx, idx, symbols.imag)
    return real + 1j * imag


# ---------------------------------------------------------------------------
# Symbol mappers
# ---------------------------------------------------------------------------

def map_bpsk(bits: np.ndarray) -> np.ndarray:
    return np.where(bits == 0, -1.0, 1.0).astype(np.complex128)


def map_qpsk(bits: np.ndarray) -> np.ndarray:
    bits = bits[: len(bits) - (len(bits) % 2)]
    pairs = bits.reshape(-1, 2)
    gray = {(0, 0): 1 + 1j, (0, 1): -1 + 1j, (1, 1): -1 - 1j, (1, 0): 1 - 1j}
    syms = np.array([gray[tuple(p)] for p in pairs], dtype=np.complex128)
    return syms / np.sqrt(2)


def map_8psk(bits: np.ndarray) -> np.ndarray:
    bits = bits[: len(bits) - (len(bits) % 3)]
    triples = bits.reshape(-1, 3)
    idx = triples[:, 0] * 4 + triples[:, 1] * 2 + triples[:, 2]
    # gray-ish mapping onto 8 phase states
    gray_map = [0, 1, 3, 2, 7, 6, 4, 5]
    phases = np.array([gray_map[i] for i in idx]) * (2 * np.pi / 8)
    return np.exp(1j * phases)


def map_16qam(bits: np.ndarray) -> np.ndarray:
    bits = bits[: len(bits) - (len(bits) % 4)]
    quads = bits.reshape(-1, 4)
    levels = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}
    i_vals = np.array([levels[tuple(q[0:2])] for q in quads])
    q_vals = np.array([levels[tuple(q[2:4])] for q in quads])
    syms = (i_vals + 1j * q_vals) / np.sqrt(10)
    return syms


# ---------------------------------------------------------------------------
# Main per-modulation generators
# All return (iq: complex128 ndarray, info: dict of ground-truth params)
# ---------------------------------------------------------------------------

def _pulse_shape_upsample(symbols: np.ndarray, sps: int, beta: float = 0.35, span: int = 8) -> np.ndarray:
    h = rrc_filter(beta, span, sps)
    upsampled = np.zeros(len(symbols) * sps, dtype=np.complex128)
    upsampled[::sps] = symbols
    shaped = np.convolve(upsampled, h, mode="same")
    return shaped


def generate_psk_qam(
    modulation: str,
    n_symbols: int,
    sample_rate_hz: float,
    symbol_rate_hz: float,
    phase_offset_rad: float,
    timing_offset: float,
    rng: np.random.Generator,
    rolloff: float = 0.35,
) -> tuple[np.ndarray, dict]:
    sps = int(round(sample_rate_hz / symbol_rate_hz))
    sps = max(sps, 2)
    bits_per_sym = {"BPSK": 1, "QPSK": 2, "8PSK": 3, "16QAM": 4}[modulation]
    bits = rng.integers(0, 2, n_symbols * bits_per_sym)
    mapper = {"BPSK": map_bpsk, "QPSK": map_qpsk, "8PSK": map_8psk, "16QAM": map_16qam}[modulation]
    symbols = mapper(bits)
    symbols = apply_timing_offset(symbols, timing_offset)
    iq = _pulse_shape_upsample(symbols, sps, beta=rolloff)
    iq *= np.exp(1j * phase_offset_rad)
    actual_symbol_rate = sample_rate_hz / sps
    info = {
        "pulse_shape": "RRC",
        "rolloff": rolloff,
        "symbol_rate_hz": actual_symbol_rate,
        "samples_per_symbol": sps,
    }
    return iq, info


def generate_fsk(
    n_symbols: int,
    sample_rate_hz: float,
    symbol_rate_hz: float,
    phase_offset_rad: float,
    rng: np.random.Generator,
    mod_index: float = 0.5,
    gaussian: bool = False,
    bt: float = 0.5,
) -> tuple[np.ndarray, dict]:
    sps = max(int(round(sample_rate_hz / symbol_rate_hz)), 2)
    bits = rng.integers(0, 2, n_symbols)
    symbol_vals = np.where(bits == 0, -1.0, 1.0)
    freq_dev_hz = mod_index * symbol_rate_hz / 2.0

    nrz = np.repeat(symbol_vals, sps)
    if gaussian:
        h = gaussian_filter(bt, span_symbols=4, sps=sps)
        nrz = np.convolve(nrz, h, mode="same")

    inst_freq = nrz * freq_dev_hz
    phase = 2 * np.pi * np.cumsum(inst_freq) / sample_rate_hz + phase_offset_rad
    iq = np.exp(1j * phase)
    info = {
        "pulse_shape": "gaussian" if gaussian else "none",
        "rolloff": None,
        "symbol_rate_hz": sample_rate_hz / sps,
        "samples_per_symbol": sps,
        "freq_deviation_hz": freq_dev_hz,
        "bt": bt if gaussian else None,
    }
    return iq, info


def generate_am(
    duration_seconds: float,
    sample_rate_hz: float,
    audio_freq_hz: float,
    mod_index: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict]:
    n = int(duration_seconds * sample_rate_hz)
    t = np.arange(n) / sample_rate_hz
    # sum of a couple of tones to look like a real baseband audio-ish message
    message = (
        0.6 * np.sin(2 * np.pi * audio_freq_hz * t)
        + 0.3 * np.sin(2 * np.pi * (audio_freq_hz * 2.3) * t)
    )
    message /= np.max(np.abs(message))
    envelope = 1 + mod_index * message
    iq = envelope.astype(np.complex128)  # baseband AM: information in the envelope, phase = 0
    info = {"pulse_shape": "none", "rolloff": None, "symbol_rate_hz": None, "audio_freq_hz": audio_freq_hz,
            "mod_index": mod_index}
    return iq, info


def generate_fm(
    duration_seconds: float,
    sample_rate_hz: float,
    audio_freq_hz: float,
    freq_dev_hz: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict]:
    n = int(duration_seconds * sample_rate_hz)
    t = np.arange(n) / sample_rate_hz
    message = (
        0.7 * np.sin(2 * np.pi * audio_freq_hz * t)
        + 0.3 * np.sin(2 * np.pi * (audio_freq_hz * 1.7) * t)
    )
    message /= np.max(np.abs(message))
    phase = 2 * np.pi * freq_dev_hz * np.cumsum(message) / sample_rate_hz
    iq = np.exp(1j * phase)
    info = {"pulse_shape": "none", "rolloff": None, "symbol_rate_hz": None, "audio_freq_hz": audio_freq_hz,
            "freq_deviation_hz": freq_dev_hz}
    return iq, info


def apply_channel_and_impairments(
    iq: np.ndarray,
    sample_rate_hz: float,
    snr_db: float,
    carrier_offset_hz: float,
    phase_offset_rad: float,
    channel: str,
    rng: np.random.Generator,
) -> np.ndarray:
    if channel == "rayleigh":
        iq = apply_rayleigh(iq, rng)
    elif channel == "multipath":
        iq = apply_multipath(iq, rng)
    iq = apply_carrier_offset_and_phase(iq, sample_rate_hz, carrier_offset_hz, 0.0)
    iq = apply_awgn(iq, snr_db, rng)
    # normalize average power to 1 so downstream features are comparable
    p = np.mean(np.abs(iq) ** 2)
    if p > 0:
        iq = iq / np.sqrt(p)
    return iq
