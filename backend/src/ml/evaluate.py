"""
Evaluate the trained model on the held-out test split.

Usage:
    python src/ml/evaluate.py --dataset dataset --model models/modulation_model.pkl
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.ml.feature_extractor import dataframe_to_xy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=str, default="dataset")
    ap.add_argument("--model", type=str, default="models/modulation_model.pkl")
    ap.add_argument("--cache-features", type=str, default="dataset/metadata/features_cache.parquet")
    args = ap.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    bundle = joblib.load(project_root / args.model)
    clf, scaler = bundle["model"], bundle["scaler"]

    cache_path = project_root / args.cache_features
    if not cache_path.exists():
        raise SystemExit("Feature cache not found -- run train_modulation.py first.")
    df = pd.read_parquet(cache_path)
    test_df = df[df["split"] == "test"]

    X_test, y_test = dataframe_to_xy(test_df)
    X_test_s = scaler.transform(X_test)
    y_pred = clf.predict(X_test_s)

    print("=== Held-out test set (SNR=20dB and/or |offset|=20kHz, NOT seen in training) ===")
    print(classification_report(y_test, y_pred, digits=3))

    print("Confusion matrix (rows=true, cols=predicted):")
    labels = sorted(set(y_test) | set(y_pred))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    header = "        " + " ".join(f"{l[:6]:>7}" for l in labels)
    print(header)
    for label, row in zip(labels, cm):
        print(f"{label[:7]:>7} " + " ".join(f"{v:>7d}" for v in row))


if __name__ == "__main__":
    main()
