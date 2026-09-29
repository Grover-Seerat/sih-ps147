import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.dataset.signal_generators import (
    generate_psk_qam, generate_fsk, generate_am, generate_fm, apply_channel_and_impairments,
)


def test_generate_all_digital_mods_are_distinguishable():
    rng = np.random.default_rng(0)
    results = {}
    for mod in ["BPSK", "QPSK", "8PSK", "16QAM"]:
        iq, info = generate_psk_qam(mod, 500, 1_000_000, 100_000, 0.0, 0.0, rng)
        assert iq.dtype in (np.complex128, np.complex64)
        assert len(iq) > 0
        assert not np.any(np.isnan(iq))
        results[mod] = iq
    # different modulations should not produce identical signals
    assert not np.allclose(results["BPSK"], results["QPSK"][: len(results["BPSK"])])


def test_generate_fsk_gfsk():
    rng = np.random.default_rng(1)
    iq_fsk, _ = generate_fsk(300, 1_000_000, 100_000, 0.0, rng, gaussian=False)
    iq_gfsk, _ = generate_fsk(300, 1_000_000, 100_000, 0.0, rng, gaussian=True)
    assert len(iq_fsk) == len(iq_gfsk)
    assert np.allclose(np.abs(iq_fsk), 1.0, atol=1e-6)  # constant envelope


def test_generate_am_fm():
    rng = np.random.default_rng(2)
    am, _ = generate_am(0.01, 1_000_000, 1000, 0.5, rng)
    fm, _ = generate_fm(0.01, 1_000_000, 1000, 5000, rng)
    assert len(am) == len(fm)
    assert np.std(np.abs(am)) > 0  # AM envelope varies
    assert np.allclose(np.abs(fm), 1.0, atol=1e-6)  # FM constant envelope


def test_randomness_no_identical_repeats():
    rng = np.random.default_rng(3)
    iq1, _ = generate_psk_qam("QPSK", 200, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq2, _ = generate_psk_qam("QPSK", 200, 1_000_000, 100_000, 0.0, 0.0, rng)
    assert not np.allclose(iq1, iq2)


def test_channel_impairments_change_signal():
    rng = np.random.default_rng(4)
    iq, _ = generate_psk_qam("BPSK", 300, 1_000_000, 100_000, 0.0, 0.0, rng)
    noisy = apply_channel_and_impairments(iq, 1_000_000, snr_db=0, carrier_offset_hz=1000,
                                           phase_offset_rad=0.5, channel="AWGN", rng=rng)
    assert not np.allclose(iq, noisy)
    assert len(noisy) == len(iq)
