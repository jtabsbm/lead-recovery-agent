#!/usr/bin/env python3
"""Shared transcript feature extraction for Trace the Ace.

Features follow the DrivenData reference blog post ("Productive math talk")
plus a few session-shape extras. Extracted per session_id from transcript CSVs.

Transcript schema: session_id, utterance_id, role (tutor|student|background),
content, timestamp.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?", re.I)
DIGIT_RE = re.compile(r"\d")
QUESTION_RE = re.compile(r"\?", re.I)

# Core reference features (blog) + session-shape extras
FEATURES = [
    "n_student_words",
    "numeric_turns_per_word",
    "digit_chars_per_word",
    "n_turns",
    "student_turn_share",
    "tutor_words_per_student_word",
    "student_question_turns_per_word",
    "avg_student_turn_len",
    "session_minutes",
]


def _safe_div(a: float, b: float) -> float:
    return a / b if b else np.nan


def session_features_from_df(session_id: str, turns: pd.DataFrame) -> dict:
    """Compute features for one session from its transcript DataFrame."""
    content = turns["content"].fillna("").astype(str)
    is_student = turns["role"].eq("student")
    is_tutor = turns["role"].eq("tutor")

    student_turns = content[is_student]
    tutor_text = " ".join(content[is_tutor])
    text = " ".join(student_turns)

    n_words = float(len(WORD_RE.findall(text)))
    n_numeric_turns = float(student_turns.str.contains(r"\d").sum())
    n_question_turns = float(student_turns.str.contains(r"\?").sum())
    digit_chars = float(len(DIGIT_RE.findall(text)))
    n_student_turns = float(len(student_turns))

    # session duration in minutes from timestamps if parseable
    minutes = np.nan
    if "timestamp" in turns.columns:
        try:
            ts = pd.to_datetime(turns["timestamp"], errors="coerce")
            if ts.notna().sum() >= 2:
                minutes = float((ts.max() - ts.min()).total_seconds() / 60.0)
        except Exception:
            pass

    n_turns = float(len(turns))
    feat = {
        "session_id": session_id,
        "n_turns": n_turns,
        "n_student_words": n_words if n_words else np.nan,
        "numeric_turns_per_word": _safe_div(n_numeric_turns, n_words),
        "digit_chars_per_word": _safe_div(digit_chars, n_words),
        "student_turn_share": _safe_div(n_student_turns, n_turns),
        "tutor_words_per_student_word": _safe_div(
            float(len(WORD_RE.findall(tutor_text))), n_words
        ),
        "student_question_turns_per_word": _safe_div(n_question_turns, n_words),
        "avg_student_turn_len": _safe_div(n_words, n_student_turns),
        "session_minutes": minutes,
    }
    return feat


def build_session_features(
    features_csv: Path, transcripts_dir: Path, max_sessions: int | None = None
) -> pd.DataFrame:
    """Load per-response features CSV, compute session features once per session."""
    df = pd.read_csv(features_csv)
    session_ids = df["session_id"].unique()
    if max_sessions is not None:
        session_ids = session_ids[:max_sessions]

    rows = []
    for sid in session_ids:
        path = transcripts_dir / f"{sid}.csv"
        try:
            turns = pd.read_csv(path)
        except FileNotFoundError:
            # missing transcript -> all-NaN features (falls back to prior at predict)
            rows.append({"session_id": sid, **{k: np.nan for k in FEATURES}})
            continue
        rows.append(session_features_from_df(sid, turns))

    sessions = pd.DataFrame(rows)
    return df.merge(sessions, on="session_id", how="left")
