"""
Train the modulation classifier.

Usage:
    python src/ml/train_modulation.py --dataset dataset --out models/modulation_model.pkl

Uses a RandomForestClassifier (fast, interpretable, no GPU needed -- see
Section 10 of the design brief). Train/test split is NOT a random shuffle:
it uses the `split` column baked into metadata.jsonl by generate_dataset.py,
which holds out high-SNR (20 dB) and large-frequency-offset (+-20kHz)
examples for testing. This tests generalization to conditions not seen
during training rather than measuring memorization of near-duplicate
correlated frames (see Section 11).
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.ml.feature_extractor import build_feature_table, dataframe_to_xy
from src.dsp.features import FEATURE_NAMES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=str, default="dataset")
    ap.add_argument("--out", type=str, default="models/modulation_model.pkl")
    ap.add_argument("--limit", type=int, default=None, help="Limit examples (for a quick smoke run)")
    ap.add_argument("--cache-features", type=str, default="dataset/metadata/features_cache.parquet")
    args = ap.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    dataset_dir = project_root / args.dataset
    cache_path = project_root / args.cache_features

    if cache_path.exists() and args.limit is None:
        import pandas as pd
        print(f"Loading cached features from {cache_path}")
        df = pd.read_parquet(cache_path)
    else:
        print("Extracting DSP features for every training example (this can take a bit)...")
        df = build_feature_table(dataset_dir, limit=args.limit)
        if args.limit is None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(cache_path)

    train_df = df[df["split"] == "train"]
    test_df = df[df["split"] == "test"]
    print(f"Train examples: {len(train_df)}, Test examples: {len(test_df)}")

    X_train, y_train = dataframe_to_xy(train_df)
    X_test, y_test = dataframe_to_xy(test_df)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test) if len(X_test) else X_test

    clf = RandomForestClassifier(
        n_estimators=300, max_depth=20, n_jobs=-1, random_state=42, class_weight="balanced"
    )
    clf.fit(X_train_s, y_train)

    train_acc = clf.score(X_train_s, y_train)
    print(f"Train accuracy: {train_acc:.4f}")
    if len(X_test):
        test_acc = clf.score(X_test_s, y_test)
        print(f"Held-out test accuracy: {test_acc:.4f}")

    out_path = project_root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": clf, "scaler": scaler, "feature_names": FEATURE_NAMES,
                 "classes": list(clf.classes_)}, out_path)
    print(f"Saved model to {out_path}")


if __name__ == "__main__":
    main()
