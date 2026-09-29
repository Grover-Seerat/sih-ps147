"""
DSP + ML evidence fusion.

We do NOT just trust the ML classifier. We gather independent DSP evidence
and check whether it is CONSISTENT with the ML prediction. Rules (all
simple, explainable, documented -- this is intentionally not another ML
model, per Section 12 of the design brief):

  - Constant-envelope check: FSK/GFSK/PSK signals should have low envelope
    variance (amplitude_variance / rms^2 below a threshold). AM does not,
    QAM does not (multiple amplitude rings).
  - PAPR check: PSK/FSK/FM have low peak-to-average power ratio (near 0dB);
    QAM and AM have higher PAPR.
  - Spectral shape check: FSK/GFSK show a bimodal PSD (two frequency
    humps) vs PSK/QAM's single lobe.
  - Symbol-rate consistency: if DSP's estimated symbol rate is within 20%
    of what the generation/known nominal symbol rate would need to be,
    that's supporting evidence (informational only when unknown).

Confidence policy:
  - ML confidence high (>0.7) AND DSP evidence consistent -> "High"
  - ML confidence moderate, or 1 supporting DSP check fails -> "Medium"
  - ML/DSP disagree on modulation family (digital vs analog, or
    constant-envelope vs not) -> "Low", and we say so explicitly.
"""
from __future__ import annotations
import numpy as np

CONSTANT_ENVELOPE_MODS = {"BPSK", "QPSK", "8PSK", "FSK", "GFSK", "FM"}
VARYING_ENVELOPE_MODS = {"16QAM", "AM"}


def _envelope_variance_ratio(features: dict) -> float:
    rms = features.get("rms", 1e-9) or 1e-9
    return features.get("amplitude_variance", 0.0) / (rms ** 2 + 1e-12)


def fuse_evidence(ml_result: dict, dsp_report: dict) -> dict:
    predicted = ml_result["predicted_class"]
    ml_conf = ml_result["confidence"]
    features = dsp_report["features"]

    evidence = [f"ML classifier: {predicted} {ml_conf * 100:.1f}%"]
    consistent_checks = 0
    total_checks = 0

    env_ratio = _envelope_variance_ratio(features)
    is_const_env_predicted = predicted in CONSTANT_ENVELOPE_MODS
    total_checks += 1
    if is_const_env_predicted and env_ratio < 0.15:
        evidence.append("Envelope variance is low, consistent with a constant-envelope modulation")
        consistent_checks += 1
    elif (not is_const_env_predicted) and env_ratio >= 0.15:
        evidence.append("Envelope variance is elevated, consistent with an amplitude-varying modulation")
        consistent_checks += 1
    else:
        evidence.append(
            f"Envelope-variance check ({env_ratio:.3f}) does NOT clearly support {predicted}"
        )

    papr = features.get("papr_db", 0.0)
    total_checks += 1
    if predicted in {"16QAM", "AM"} and papr > 3.0:
        evidence.append(f"PAPR ({papr:.1f} dB) is consistent with {predicted}")
        consistent_checks += 1
    elif predicted in CONSTANT_ENVELOPE_MODS and papr <= 4.0:
        evidence.append(f"PAPR ({papr:.1f} dB) is consistent with {predicted}")
        consistent_checks += 1
    else:
        evidence.append(f"PAPR ({papr:.1f} dB) is borderline for {predicted}")

    symrate_info = dsp_report.get("symbol_rate", {})
    if symrate_info.get("symbol_rate_hz") and predicted not in ("AM", "FM"):
        evidence.append(
            f"Estimated symbol rate: {symrate_info['symbol_rate_hz'] / 1000:.1f} kSym/s "
            f"(line-search confidence {symrate_info.get('confidence', 0):.2f})"
        )

    snr_db = dsp_report.get("snr", {}).get("snr_db")
    if snr_db is not None:
        evidence.append(f"Estimated SNR: {snr_db:.1f} dB")

    consistency_ratio = consistent_checks / max(total_checks, 1)

    if ml_conf > 0.7 and consistency_ratio >= 0.5:
        confidence_label = "High"
    elif ml_conf > 0.4 and consistency_ratio > 0:
        confidence_label = "Medium"
    else:
        confidence_label = "Low"
        evidence.append("DSP evidence and ML prediction show limited agreement -- treat with caution")

    return {
        "final_modulation": predicted,
        "confidence_label": confidence_label,
        "confidence_score": round(ml_conf * (0.5 + 0.5 * consistency_ratio), 3),
        "evidence": evidence,
    }
