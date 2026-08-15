#!/usr/bin/env bash
# Package and test the Trace the Ace submission exactly as the platform runs it.
# Usage: bash package_and_test.sh [data_dir]
#   data_dir: directory containing submission_format.csv, test_features.csv, test_transcripts/
#             (defaults to the official data-demo from the runtime repo)
set -euo pipefail
cd "$(dirname "$0")"
ROOT_DIR="$(pwd)"

DATA_DIR="${1:-tutoring-outcomes-runtime/data-demo}"

rm -rf build submission
mkdir -p build/assets submission

# layout required by the platform: main.py at archive ROOT
cp main.py build/
cp -r src build/src
cp model.pkl build/assets/model.pkl

cd build && zip -qr ../submission/submission.zip . -x "*__pycache__*" && cd ..
echo "packed submission/submission.zip:"
unzip -l submission/submission.zip

# replicate the runtime layout: unzip into code_execution/, run python main.py
rm -rf code_execution
mkdir -p code_execution
cp -r "$DATA_DIR" code_execution/data
# data-demo uses CRLF; strip to be safe
find code_execution/data -name '*.csv' -exec dos2unix {} \; 2>/dev/null || true

cd code_execution
unzip -q ../submission/submission.zip
echo "--- running inference ---"
"$ROOT_DIR/.venv/bin/python" main.py
echo "--- submission.csv head ---"
head -6 submission.csv
echo "--- validation ---"
cd ..
.venv/bin/python - <<'PY'
import pandas as pd
sf = pd.read_csv("code_execution/data/submission_format.csv")
sub = pd.read_csv("code_execution/submission.csv")
assert list(sf.response_id) == list(sub.response_id), "response_id mismatch"
assert "probability" in sub.columns and len(sub) == len(sf)
p = sub.probability
assert p.between(0, 1).all(), "probabilities out of range"
print(f"VALID: {len(sub)} rows, ids match submission_format, probs in [0,1], "
      f"mean={p.mean():.4f} min={p.min():.3f} max={p.max():.3f}")
PY
