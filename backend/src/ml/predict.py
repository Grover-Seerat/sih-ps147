"""Single-signal ML inference: IQ array -> modulation class probabilities."""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
import joblib
import numpy as np

from src.dsp.features import extract_features, features_to_vector


@lru_cache(maxsize=1)
def _load_model(model_path: str):
    return joblib.load(model_path)


def predict_modulation(iq: np.ndarray, sample_rate_hz: float, model_path: str | Path) -> dict:
    bundle = _load_model(str(model_path))
    clf, scaler, classes = bundle["model"], bundle["scaler"], bundle["classes"]

    feats = extract_features(iq, sample_rate_hz)
    vec = features_to_vector(feats).reshape(1, -1)
    vec_s = scaler.transform(vec)

    proba = clf.predict_proba(vec_s)[0]
    class_probs = {cls: float(round(p, 4)) for cls, p in zip(classes, proba)}
    ranked = sorted(class_probs.items(), key=lambda x: -x[1])

    return {
        "predicted_class": ranked[0][0],
        "confidence": ranked[0][1],
        "top_3_candidates": ranked[:3],
        "class_probabilities": class_probs,
        "features": feats,
    }
