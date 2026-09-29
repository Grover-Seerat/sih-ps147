import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.dataset.signal_generators import generate_psk_qam, generate_fm, apply_channel_and_impairments
from src.ml.predict import predict_modulation
from src.demod.bpsk import demodulate_bpsk
from src.demod.qpsk import demodulate_qpsk
from src.demod.fm import demodulate_fm

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "modulation_model.pkl"


def test_ml_inference_runs():
    if not MODEL_PATH.exists():
        return  # model not trained yet in this environment; skip gracefully
    rng = np.random.default_rng(0)
    iq, info = generate_psk_qam("QPSK", 1000, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 15, 0, 0.0, "AWGN", rng)
    result = predict_modulation(iq, 1_000_000, MODEL_PATH)
    assert "predicted_class" in result
    assert 0 <= result["confidence"] <= 1
    assert len(result["top_3_candidates"]) == 3


def test_bpsk_demod_runs():
    rng = np.random.default_rng(1)
    iq, info = generate_psk_qam("BPSK", 500, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 20, 0, 0.0, "AWGN", rng)
    result = demodulate_bpsk(iq, 1_000_000, info["symbol_rate_hz"], carrier_offset_hz=0.0)
    assert result["num_bits"] > 0
    assert set(result["bits"]) <= {0, 1}


def test_qpsk_demod_runs():
    rng = np.random.default_rng(2)
    iq, info = generate_psk_qam("QPSK", 500, 1_000_000, 100_000, 0.0, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 20, 0, 0.0, "AWGN", rng)
    result = demodulate_qpsk(iq, 1_000_000, info["symbol_rate_hz"], carrier_offset_hz=0.0)
    assert result["num_bits"] > 0


def test_fm_demod_runs():
    rng = np.random.default_rng(3)
    iq, info = generate_fm(0.01, 1_000_000, 1000, 5000, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 20, 0, 0.0, "AWGN", rng)
    result = demodulate_fm(iq, 1_000_000, carrier_offset_hz=0.0)
    assert result["num_samples"] > 0
    assert len(result["audio"]) > 0
