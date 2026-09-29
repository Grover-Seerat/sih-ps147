"""
Generate the 5 demo test recordings described in Section 22 of the design brief.

Usage:
    python demo_generate.py

Produces files under demo_data/:
    test1_qpsk.iq / .json
    test2_bpsk.iq / .json
    test3_16qam.iq / .json
    test4_fm.iq / .json
    test5_wideband.iq / .json   <-- the headline demo file (BPSK+FM+QPSK)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

from src.dataset.signal_generators import (
    generate_psk_qam, generate_fm, apply_channel_and_impairments,
)

OUT_DIR = Path(__file__).resolve().parent / "demo_data"


def save(iq: np.ndarray, sample_rate_hz: int, name: str, extra_meta: dict):
    OUT_DIR.mkdir(exist_ok=True)
    iq = iq.astype(np.complex64)
    iq_path = OUT_DIR / f"{name}.iq"
    iq.tofile(iq_path)
    meta = {"sample_rate_hz": sample_rate_hz, "num_samples": len(iq),
            "duration_seconds": len(iq) / sample_rate_hz, **extra_meta}
    (OUT_DIR / f"{name}.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {iq_path} ({len(iq)} samples, {sample_rate_hz} Hz)")


def main():
    rng = np.random.default_rng(7)

    # TEST 1: QPSK, 10dB, 100kSym/s, +5kHz offset
    sr = 1_000_000
    iq, info = generate_psk_qam("QPSK", 3000, sr, 100_000, 0.3, 0.1, rng)
    iq = apply_channel_and_impairments(iq, sr, snr_db=10, carrier_offset_hz=5000,
                                        phase_offset_rad=0.3, channel="AWGN", rng=rng)
    save(iq, sr, "test1_qpsk", {"modulation": "QPSK", "snr_db": 10, "symbol_rate_hz": 100_000,
                                 "carrier_offset_hz": 5000})

    # TEST 2: BPSK, 15dB, 50kSym/s, -5kHz offset
    iq, info = generate_psk_qam("BPSK", 3000, sr, 50_000, 0.1, 0.0, rng)
    iq = apply_channel_and_impairments(iq, sr, snr_db=15, carrier_offset_hz=-5000,
                                        phase_offset_rad=0.1, channel="AWGN", rng=rng)
    save(iq, sr, "test2_bpsk", {"modulation": "BPSK", "snr_db": 15, "symbol_rate_hz": 50_000,
                                 "carrier_offset_hz": -5000})

    # TEST 3: 16QAM, 15dB, 250kSym/s
    sr3 = 2_000_000
    iq, info = generate_psk_qam("16QAM", 3000, sr3, 250_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, sr3, snr_db=15, carrier_offset_hz=0,
                                        phase_offset_rad=0.0, channel="AWGN", rng=rng)
    save(iq, sr3, "test3_16qam", {"modulation": "16QAM", "snr_db": 15, "symbol_rate_hz": 250_000,
                                   "carrier_offset_hz": 0})

    # TEST 4: FM
    iq, info = generate_fm(1.0, sr, audio_freq_hz=1000, freq_dev_hz=8000, rng=rng)
    iq = apply_channel_and_impairments(iq, sr, snr_db=15, carrier_offset_hz=0,
                                        phase_offset_rad=0.0, channel="AWGN", rng=rng)
    save(iq, sr, "test4_fm", {"modulation": "FM", "snr_db": 15})

    # TEST 5: WIDEBAND multi-signal recording: BPSK ~100kHz, FM ~350kHz, QPSK ~650kHz
    # 0-1MHz span -> use sample_rate = 2 MS/s (Nyquist covers -1..+1 MHz for complex baseband)
    sr5 = 2_000_000
    n = 400_000  # 0.2s

    def place_signal(base_iq, center_hz):
        t = np.arange(len(base_iq)) / sr5
        return base_iq * np.exp(1j * 2 * np.pi * center_hz * t)

    bpsk_iq, _ = generate_psk_qam("BPSK", 3000, sr5, 50_000, 0.2, 0.0, rng)
    bpsk_iq = apply_channel_and_impairments(bpsk_iq, sr5, 15, 0, 0.2, "AWGN", rng)
    bpsk_iq = place_signal(bpsk_iq, 100_000)

    fm_iq, _ = generate_fm(len(bpsk_iq) / sr5, sr5, audio_freq_hz=1200, freq_dev_hz=10000, rng=rng)
    fm_iq = apply_channel_and_impairments(fm_iq, sr5, 15, 0, 0.0, "AWGN", rng)
    fm_iq = place_signal(fm_iq, 350_000)

    qpsk_iq, _ = generate_psk_qam("QPSK", 4000, sr5, 100_000, 0.1, 0.0, rng)
    qpsk_iq = apply_channel_and_impairments(qpsk_iq, sr5, 15, 0, 0.1, "AWGN", rng)
    qpsk_iq = place_signal(qpsk_iq, 650_000)

    max_len = max(len(bpsk_iq), len(fm_iq), len(qpsk_iq))

    def pad(x):
        out = np.zeros(max_len, dtype=np.complex128)
        out[: len(x)] = x
        return out

    wideband = pad(bpsk_iq) + pad(fm_iq) + pad(qpsk_iq)
    wideband += (rng.normal(0, 0.05, max_len) + 1j * rng.normal(0, 0.05, max_len))  # channel noise floor
    save(wideband.astype(np.complex64), sr5, "test5_wideband", {
        "modulation": "MULTI-SIGNAL",
        "signals": [
            {"modulation": "BPSK", "center_frequency_hz": 100_000},
            {"modulation": "FM", "center_frequency_hz": 350_000},
            {"modulation": "QPSK", "center_frequency_hz": 650_000},
        ],
    })

    print("\nAll demo files written to", OUT_DIR)


if __name__ == "__main__":
    main()
