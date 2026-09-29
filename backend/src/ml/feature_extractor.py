"""Batch feature extraction: turns the generated dataset into an (X, y) matrix
for training, using the same src/dsp/features.py used at inference time --
this is important: train/inference feature parity avoids silent skew bugs."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

from src.dsp.features import extract_features, features_to_vector, FEATURE_NAMES
from src.io.iq_reader import read_iq


def build_feature_table(dataset_dir: str | Path, limit: int | None = None) -> pd.DataFrame:
    dataset_dir = Path(dataset_dir)
    jsonl_path = dataset_dir / "metadata" / "metadata.jsonl"
    records = []
    with open(jsonl_path) as f:
        lines = f.readlines()
    if limit:
        lines = lines[:limit]

    for i, line in enumerate(lines):
        meta = json.loads(line)
        iq_path = dataset_dir / meta["file"]
        iq = read_iq(iq_path)
        feats = extract_features(iq, meta["sample_rate_hz"])
        row = {"sample_id": meta["sample_id"], "modulation": meta["modulation"], "split": meta["split"]}
        row.update(feats)
        records.append(row)
        if (i + 1) % 200 == 0:
            print(f"  extracted features for {i + 1}/{len(lines)}")

    df = pd.DataFrame(records)
    return df


def dataframe_to_xy(df: pd.DataFrame):
    X = df[FEATURE_NAMES].values
    y = df["modulation"].values
    return X, y
