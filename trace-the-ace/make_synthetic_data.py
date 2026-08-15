#!/usr/bin/env python3
"""Generate synthetic Trace the Ace data matching published dataset statistics.

Real data requires login; this mirrors it so the full pipeline can be validated
end-to-end locally. Published stats (DrivenData reference blog, Jul 2026):
  - 35,072 responses / 22,821 sessions / 398 learning objectives
  - base rate (share correct) = 0.702
  - median 267 turns/session; n_student_words mean 1003, std 431, min 1, max 3385
  - numeric_turns_per_word mean 0.0448; digit_chars_per_word mean 0.2004
  - features move correctness ~66.5% (quiet quintile) to ~74% (talky)

We generate sessions with realistic transcript structure, then response-level
labels via a logistic model whose coefficients reproduce the published direction
(numeric_turns_per_word strongest negative, n_student_words / digit_chars positive).
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

TOPICS = [
    "Knowing the value of each digit in numbers with up to 2 decimal places.",
    "Adding and subtracting tens to a 2-digit number.",
    "Comparing and ordering fractions by finding a common denominator.",
    "Comparing fractions using reasoning.",
    "Counting in multiples.",
    "Multiplying and dividing whole numbers and decimals by 10 and 100.",
    "Adding and subtracting fractions with different denominators.",
    "Finding fractions of an amount.",
    "Rounding numbers to the nearest 100 and 1,000.",
    "Using place value to order and compare numbers.",
]

TUTOR_OPENERS = [
    "Hello, are you ready to get started today?",
    "Hi! Great to see you again. Shall we begin?",
    "Good afternoon! Today we are going to look at a new topic.",
]
TUTOR_PROMPTS = [
    "So let me ask you first. Do you know what a fact family is?",
    "What do you notice about these two numbers?",
    "Can you talk me through how you got that answer?",
    "Uh-huh. And what would you do next?",
    "Good thinking. Now, is that answer reasonable?",
    "Let's try a similar one. What is 30 times 4?",
    "Remember what we said about the denominator. What happens here?",
]
STUDENT_THINKING = [
    "I think we need to make the bottom numbers the same before we add.",
    "So 2000 plus 725 would be 2725, and then I take away 25 to get 2700.",
    "Hmm, the 4 is in the tens column so it means 40 really.",
    "I would divide it by 100, so the answer is 3.45.",
    "Wait, wait. So if I'm adding 25 onto it, then it becomes 95?",
    "Maybe I should compare them as decimals first.",
    "I'm not sure. Is it because 10 has one zero?",
]
STUDENT_NUMERIC = ["12.", "Is it 4?", "6?", "75.", "Half?", "300?", "Yes", "Okay", "No"]
STUDENT_WORDS_BANK = [
    "because", "then", "maybe", "I think", "so", "it", "the", "number", "times",
    "divide", "add", "take away", "left", "right", "answer", "easy", "hard",
    "wait", "hmm", "well", "actually", "remember", "we", "did", "this", "last week",
]


def rid(prefix: str, n: int) -> list[str]:
    """Random 7-char lowercase ids."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    out = []
    for _ in range(n):
        out.append("".join(RNG.choice(list(alphabet), size=7)))
    return out


def make_transcript(sid: str, n_turns: int, quiet: bool) -> pd.DataFrame:
    rows = []
    t = 0
    roles, contents = [], []
    contents.append("[unclear]"); roles.append("background"); t += 8
    contents.append(random.choice(TUTOR_OPENERS)); roles.append("tutor"); t += 8
    contents.append("Yes, I think so."); roles.append("student"); t += 8
    for i in range(max(0, n_turns - 4)):
        if roles[-1] == "tutor":
            use_numeric = RNG.random() < (0.45 if quiet else 0.18)
            contents.append(
                random.choice(STUDENT_NUMERIC) if use_numeric
                else random.choice(STUDENT_THINKING)
            )
            roles.append("student")
        else:
            contents.append(random.choice(TUTOR_PROMPTS)); roles.append("tutor")
        t += 8
    contents.append("Great work today. See you next time!"); roles.append("tutor")
    timestamps = [f"00:{(t // 60) % 60:02d}:{t % 60:02d}" if t < 3600
                  else f"{t // 3600:02d}:{(t // 60) % 60:02d}:{t % 60:02d}" for t in range(0, len(roles) * 8, 8)]
    df = pd.DataFrame({
        "session_id": sid,
        "utterance_id": range(len(roles)),
        "role": roles,
        "content": contents,
        "timestamp": timestamps[: len(roles)],
    })
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data")
    ap.add_argument("--n-responses", type=int, default=6000)
    ap.add_argument("--n-sessions", type=int, default=4000)
    args = ap.parse_args()

    random.seed(7)
    out = Path(args.out_dir)
    (out / "train_transcripts").mkdir(parents=True, exist_ok=True)

    # --- features file ---
    session_ids = rid("s", args.n_sessions)
    objective_ids = rid("o", 60)
    response_ids = rid("r", args.n_responses)

    # n_turns ~ median 267 (lognormal), quiet sessions get fewer student words
    n_turns_arr = np.clip(np.round(RNG.lognormal(5.55, 0.35, args.n_sessions)), 20, 700).astype(int)
    quiet_arr = RNG.random(args.n_sessions) < 0.05

    rows = []
    sid_to_turns = dict(zip(session_ids, n_turns_arr))
    sid_to_quiet = dict(zip(session_ids, quiet_arr))
    for resp in response_ids:
        sid = str(RNG.choice(session_ids))
        oid = str(RNG.choice(objective_ids))
        rows.append({
            "response_id": resp,
            "session_id": sid,
            "learning_objective_id": oid,
            "learning_objective": TOPICS[hash(oid) % len(TOPICS)],
        })
    feats = pd.DataFrame(rows)

    # --- transcripts ---
    for sid in session_ids:
        make_transcript(sid, int(sid_to_turns[sid]), bool(sid_to_quiet[sid])).to_csv(
            out / "train_transcripts" / f"{sid}.csv", index=False
        )

    # --- labels from transcript-derived features (same generator the blog describes) ---
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from src.features import session_features_from_df

    lab_rows = []
    base = np.log(0.702 / 0.298)  # intercept from published base rate
    coef = {  # standardized-ish, matches published directions
        "n_student_words": +0.07,
        "numeric_turns_per_word": -0.21,
        "digit_chars_per_word": +0.08,
    }
    for sid in session_ids:
        turns = pd.read_csv(out / "train_transcripts" / f"{sid}.csv")
        f = session_features_from_df(sid, turns)
        z = {k: 0.0 for k in coef}
        z["n_student_words"] = (f["n_student_words"] - 1000) / 430
        z["numeric_turns_per_word"] = (f["numeric_turns_per_word"] - 0.045) / 0.019
        z["digit_chars_per_word"] = (f["digit_chars_per_word"] - 0.20) / 0.085
        eta = base + sum(coef[k] * z[k] for k in coef)
        p = float(1 / (1 + np.exp(-eta)))
        # learning-objective difficulty noise per response
        resp = feats.loc[feats.session_id == sid, "response_id"]
        for r in resp:
            p_r = np.clip(p + RNG.normal(0, 0.02), 0.02, 0.98)
            lab_rows.append({"response_id": r, "is_correct": float(RNG.random() < p_r)})
    labels = pd.DataFrame(lab_rows)
    labels.to_csv(out / "train_labels.csv", index=False)
    feats.to_csv(out / "train_features.csv", index=False)

    # --- test split (for local submission-format practice) ---
    test_resp = feats.sample(frac=0.2, random_state=1)
    test_idx = labels.response_id.isin(test_resp.response_id)
    submission_format = pd.DataFrame({
        "response_id": labels.loc[test_idx, "response_id"],
        "probability": 0.5,
    })
    submission_format.to_csv(out / "submission_format.csv", index=False)
    # hold out test transcripts by copying all sessions (test uses same session pool)
    print(f"responses={len(feats)} sessions={args.n_sessions} "
          f"labels={len(labels)} base_rate={labels.is_correct.mean():.3f}")


if __name__ == "__main__":
    main()
