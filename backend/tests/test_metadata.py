import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.dataset.metadata_schema import SignalMetadata, MODULATIONS


def test_metadata_roundtrip():
    m = SignalMetadata(
        sample_id="sample_000001", file="raw/iq/sample_000001.iq", format="complex64",
        modulation="QPSK", sample_rate_hz=1_000_000.0, symbol_rate_hz=100_000.0, snr_db=10.0,
        carrier_frequency_hz=0.0, carrier_offset_hz=5000.0, bandwidth_hz=120_000.0,
        num_samples=102400, duration_seconds=0.1024, pulse_shape="RRC", rolloff=0.35,
        channel="AWGN", phase_offset_rad=0.42, timing_offset=0.13,
    )
    d = m.to_dict()
    assert d["modulation"] == "QPSK"
    assert d["fec"] == "none"
    assert d["split"] == "train"


def test_all_modulations_listed():
    assert set(MODULATIONS) == {"BPSK", "QPSK", "8PSK", "16QAM", "FSK", "GFSK", "AM", "FM"}
