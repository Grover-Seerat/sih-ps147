"""
End-to-end analysis pipeline. This is what api/main.py calls.

    RAW IQ/WAV -> universal_reader -> detector -> [per-signal: dsp features,
    ML predict, fusion, demod] -> standardized result schema (Section 16).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np

from src.io.universal_reader import load_signal
from src.pipeline.detector import detect_signals, extract_signal_region
from src.dsp.features import extract_features, extract_full_dsp_report
from src.dsp.frequency_offset import estimate_carrier_offset
from src.ml.predict import predict_modulation
from src.pipeline.fusion import fuse_evidence
from src.demod.bpsk import demodulate_bpsk
from src.demod.qpsk import demodulate_qpsk
from src.demod.fsk import demodulate_fsk
from src.demod.gfsk import demodulate_gfsk
from src.demod.am import demodulate_am
from src.demod.fm import demodulate_fm

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "modulation_model.pkl"


def _run_demod(modulation: str, iq: np.ndarray, sample_rate_hz: float, symbol_rate_hz: float | None,
                carrier_offset_hz: float) -> dict:
    try:
        if modulation == "BPSK":
            return {"supported": True, "status": "success",
                     "result": demodulate_bpsk(iq, sample_rate_hz, symbol_rate_hz or 100_000, carrier_offset_hz)}
        if modulation == "QPSK":
            return {"supported": True, "status": "success",
                     "result": demodulate_qpsk(iq, sample_rate_hz, symbol_rate_hz or 100_000, carrier_offset_hz)}
        if modulation == "FSK":
            return {"supported": True, "status": "success",
                     "result": demodulate_fsk(iq, sample_rate_hz, symbol_rate_hz or 100_000, carrier_offset_hz)}
        if modulation == "GFSK":
            return {"supported": True, "status": "success",
                     "result": demodulate_gfsk(iq, sample_rate_hz, symbol_rate_hz or 100_000, carrier_offset_hz)}
        if modulation == "AM":
            return {"supported": True, "status": "success",
                     "result": demodulate_am(iq, sample_rate_hz, carrier_offset_hz)}
        if modulation == "FM":
            return {"supported": True, "status": "success",
                     "result": demodulate_fm(iq, sample_rate_hz, carrier_offset_hz)}
        return {"supported": False, "status": "not_implemented_for_this_modulation", "result": None}
    except Exception as e:  # pragma: no cover - defensive, never crash the demo on one signal
        return {"supported": True, "status": f"error: {e}", "result": None}


def analyze_single_signal(iq: np.ndarray, sample_rate_hz: float, signal_id: int = 1,
                           center_frequency_hz: float = 0.0, model_path: Path | str = DEFAULT_MODEL_PATH) -> dict:
    dsp_report = extract_full_dsp_report(iq, sample_rate_hz)
    ml_result = predict_modulation(iq, sample_rate_hz, model_path)

    # refine carrier offset estimate now that we know the likely modulation family
    offset_refined = estimate_carrier_offset(iq, sample_rate_hz, ml_result["predicted_class"])
    dsp_report["carrier_offset"] = offset_refined

    fused = fuse_evidence(ml_result, dsp_report)
    modulation = fused["final_modulation"]

    symbol_rate_hz = dsp_report["symbol_rate"].get("symbol_rate_hz")
    demod = _run_demod(modulation, iq, sample_rate_hz, symbol_rate_hz, offset_refined["carrier_offset_hz"])

    return {
        "id": signal_id,
        "center_frequency_hz": center_frequency_hz,
        "bandwidth_hz": {"value": dsp_report["bandwidth"]["bandwidth_hz"], "source": "dsp_estimated"},
        "snr_db": {"value": dsp_report["snr"]["snr_db"], "source": "dsp_estimated"},
        "symbol_rate_hz": {
            "value": symbol_rate_hz,
            "source": "dsp_estimated" if modulation not in ("AM", "FM") else "not_applicable",
            "estimator_confidence": dsp_report["symbol_rate"].get("confidence"),
        },
        "carrier_offset_hz": {"value": offset_refined["carrier_offset_hz"], "source": "dsp_estimated"},
        "modulation": {
            "label": modulation,
            "confidence": fused["confidence_score"],
            "confidence_label": fused["confidence_label"],
            "source": "ml_dsp_fusion",
            "top_candidates": ml_result["top_3_candidates"],
        },
        "evidence": fused["evidence"],
        "demodulation": demod,
        "dsp_features": dsp_report["features"],
    }


def analyze_file(path: str | Path, assumed_sample_rate_hz: float | None = None,
                  model_path: Path | str = DEFAULT_MODEL_PATH, wideband: bool = False) -> dict:
    loaded = load_signal(path, assumed_sample_rate_hz=assumed_sample_rate_hz)
    iq = loaded.iq
    sample_rate_hz = loaded.sample_rate_hz

    file_info = {
        "name": Path(path).name,
        "format": loaded.format,
        "sample_count": int(len(iq)),
        "sample_rate_hz": sample_rate_hz,
        "sample_rate_source": loaded.sample_rate_source,
        "duration_seconds": (len(iq) / sample_rate_hz) if sample_rate_hz else None,
    }

    if sample_rate_hz is None:
        return {
            "file": file_info,
            "signals": [],
            "error": (
                "Sample rate is unknown for this file (no sidecar metadata, no WAV header, "
                "none supplied). Analysis requires a sample rate -- pass --sample-rate or "
                "provide a metadata.json sidecar. Refusing to guess."
            ),
        }

    if wideband:
        detections = detect_signals(iq, sample_rate_hz)
        signals = []
        for i, det in enumerate(detections, start=1):
            region_iq = extract_signal_region(
                iq, sample_rate_hz, det["center_frequency_hz"], det["bandwidth_hz"]
            )
            # decimate the extracted baseband region to speed up feature extraction
            result = analyze_single_signal(
                region_iq, sample_rate_hz, signal_id=i,
                center_frequency_hz=det["center_frequency_hz"], model_path=model_path,
            )
            result["detected_bandwidth_hz"] = det["bandwidth_hz"]
            result["detection_peak_power_db"] = det["peak_power_db"]
            signals.append(result)
        return {"file": file_info, "signals": signals}
    else:
        result = analyze_single_signal(iq, sample_rate_hz, signal_id=1, center_frequency_hz=0.0,
                                        model_path=model_path)
        return {"file": file_info, "signals": [result]}
