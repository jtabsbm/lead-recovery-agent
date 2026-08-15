#!/usr/bin/env python3
"""Train the Trace the Ace baseline: transcript features -> logistic regression.

Follows the official DrivenData reference blog validation design:
  - split BY SESSION (GroupShuffleSplit) so no session leaks across train/val
  - compare against constant-prior baseline (the log-loss floor)
Model: StandardScaler + LogisticRegression on 9 session features.
Outputs model.pkl (scikit-learn Pipeline) + val_scores.json.
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
from src.features import FEATURES, build_session_features  # noqa: E402


def main() -> None:
    data_dir = ROOT / "data"
    print("Building session features from transcripts ...")
    df = build_session_features(
        data_dir / "train_features.csv", data_dir / "train_transcripts"
    )
    labels = pd.read_csv(data_dir / "train_labels.csv")
    # accept either `correct` (rules page) or `is_correct` (blog) as label column
    label_col = "correct" if "correct" in labels.columns else "is_correct"
    df = df.merge(labels.rename(columns={label_col: "y"}), on="response_id")
    print(f"responses={len(df)} sessions={df.session_id.nunique()} "
          f"base_rate={df.y.mean():.4f}")

    train_idx, val_idx = next(
        GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=3).split(
            df, df.y, groups=df.session_id
        )
    )
    tr, va = df.iloc[train_idx], df.iloc[val_idx]

    med = tr[FEATURES].median()
    X_tr = tr[FEATURES].fillna(med)
    X_va = va[FEATURES].fillna(med)

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(X_tr, tr.y)
    p_va = model.predict_proba(X_va)[:, 1]

    base = tr.y.mean()
    scores = {
        "n_train": int(len(tr)),
        "n_val": int(len(va)),
        "base_log_loss": round(float(log_loss(va.y, np.full(len(va), base))), 4),
        "model_log_loss": round(float(log_loss(va.y, p_va)), 4),
        "model_auc": round(float(roc_auc_score(va.y, p_va)), 4),
        "features": FEATURES,
    }
    print(json.dumps(scores, indent=2))

    with open(ROOT / "model.pkl", "wb") as f:
        pickle.dump({"model": model, "medians": med.to_dict(), "prior": float(base)}, f)
    (ROOT / "val_scores.json").write_text(json.dumps(scores, indent=2))
    print("Saved model.pkl + val_scores.json")


if __name__ == "__main__":
    main()
