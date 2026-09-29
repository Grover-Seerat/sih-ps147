import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.dsp.fft import compute_fft, freq_axis
from src.dsp.bandwidth import estimate_occupied_bandwidth
from src.dsp.snr import estimate_snr
from src.dsp.features import extract_features, features_to_vector, FEATURE_NAMES
from src.dataset.signal_generators import generate_psk_qam, apply_channel_and_impairments


def _tone(freq_hz, sample_rate_hz=1_000_000, n=10000):
    t = np.arange(n) / sample_rate_hz
    return np.exp(1j * 2 * np.pi * freq_hz * t).astype(np.complex64)


def test_fft_peak_at_correct_frequency():
    sig = _tone(50_000)
    spec = compute_fft(sig)
    freqs = freq_axis(len(sig), 1_000_000)
    peak_freq = freqs[np.argmax(np.abs(spec))]
    assert abs(peak_freq - 50_000) < 200  # within one FFT bin roughly


def test_bandwidth_estimator_runs():
    rng = np.random.default_rng(0)
    iq, info = generate_psk_qam("QPSK", 1000, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 15, 0, 0.0, "AWGN", rng)
    result = estimate_occupied_bandwidth(iq, 1_000_000)
    assert result["bandwidth_hz"] > 0
    assert "method" in result


def test_snr_estimator_reasonable():
    rng = np.random.default_rng(1)
    iq, info = generate_psk_qam("BPSK", 1000, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq_high_snr = apply_channel_and_impairments(iq, 1_000_000, 20, 0, 0.0, "AWGN", rng)
    iq_low_snr = apply_channel_and_impairments(iq, 1_000_000, 0, 0, 0.0, "AWGN", rng)
    snr_high = estimate_snr(iq_high_snr, 1_000_000)["snr_db"]
    snr_low = estimate_snr(iq_low_snr, 1_000_000)["snr_db"]
    assert snr_high > snr_low  # higher injected SNR should measure higher


def test_feature_extraction_shape():
    rng = np.random.default_rng(2)
    iq, info = generate_psk_qam("16QAM", 500, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 10, 0, 0.0, "AWGN", rng)
    feats = extract_features(iq, 1_000_000)
    assert set(feats.keys()) == set(FEATURE_NAMES)
    vec = features_to_vector(feats)
    assert vec.shape == (len(FEATURE_NAMES),)
    assert not np.any(np.isnan(vec))
