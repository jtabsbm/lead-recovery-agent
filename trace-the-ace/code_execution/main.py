#!/usr/bin/env python3
"""Trace the Ace inference entrypoint (competition submission format).

Runtime layout expected by the platform:
  code_execution/
  ├── data/
  │   ├── submission_format.csv
  │   ├── test_features.csv
  │   └── test_transcripts/{session_id}.csv
  ├── main.py            <- this file, at archive root
  ├── assets/model.pkl   <- trained sklearn pipeline + medians + prior
  └── submission.csv     <- written by this script

Prediction strategy:
  - extract per-session transcript features (src/features.py)
  - fall back to training prior for responses with missing/quiet transcripts
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(SRC_ROOT))

from src.features import FEATURES, build_session_features  # noqa: E402

DATA_DIR = Path("data")
SUBMISSION_PATH = Path("submission.csv")
ASSET_PATH = SRC_ROOT / "assets" / "model.pkl"


def main() -> None:
    submission_format = pd.read_csv(DATA_DIR / "submission_format.csv")
    print(f"loaded submission_format: {submission_format.shape}")

    features = pd.read_csv(DATA_DIR / "test_features.csv")
    print(f"loaded test_features: {features.shape}")

    df = build_session_features(DATA_DIR / "test_features.csv",
                                DATA_DIR / "test_transcripts")
    print(f"built session features for {df.session_id.nunique()} sessions")

    with open(ASSET_PATH, "rb") as f:
        bundle = pickle.load(f)
    model, medians, prior = bundle["model"], bundle["medians"], bundle["prior"]

    med = pd.Series(medians)
    X = df[FEATURES].fillna(med)
    p = model.predict_proba(X)[:, 1]
    # rows with no transcript at all -> prior
    no_transcript = df[FEATURES].isna().all(axis=1)
    p = np.where(no_transcript, prior, p)
    df["probability"] = p

    preds = submission_format[["response_id"]].merge(
        df[["response_id", "probability"]], on="response_id", how="left"
    )
    preds["probability"] = preds["probability"].fillna(prior).clip(0.02, 0.98)
    preds.to_csv(SUBMISSION_PATH, index=False)
    print(f"wrote {SUBMISSION_PATH} with {len(preds)} rows")


if __name__ == "__main__":
    main()
