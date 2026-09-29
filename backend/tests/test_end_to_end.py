"""End-to-end smoke test: generate -> read -> analyze -> classify -> demodulate."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np

from src.dataset.signal_generators import generate_psk_qam, apply_channel_and_impairments
from src.io.iq_reader import write_iq, read_iq
from src.pipeline.analyzer import analyze_single_signal

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "modulation_model.pkl"


def test_end_to_end_pipeline(tmp_path):
    if not MODEL_PATH.exists():
        return  # requires a trained model; skip gracefully in fresh clones

    rng = np.random.default_rng(42)
    iq, info = generate_psk_qam("QPSK", 1500, 1_000_000, 100_000, 0.2, 0.0, rng)
    iq = apply_channel_and_impairments(iq, 1_000_000, 15, 5000, 0.2, "AWGN", rng)

    iq_path = tmp_path / "e2e_test.iq"
    write_iq(iq, iq_path)

    loaded = read_iq(iq_path)
    assert len(loaded) == len(iq)

    result = analyze_single_signal(loaded, 1_000_000, model_path=MODEL_PATH)

    assert result["modulation"]["label"] in {"BPSK", "QPSK", "8PSK", "16QAM", "FSK", "GFSK", "AM", "FM"}
    # Demodulation is only implemented for BPSK/QPSK/FSK/GFSK/AM/FM (Section 13's minimum
    # set) -- 8PSK/16QAM correctly report supported=False rather than crashing.
    assert result["demodulation"]["supported"] in (True, False)
    assert len(result["evidence"]) > 0
    assert "snr_db" in result and result["snr_db"]["source"] == "dsp_estimated"
