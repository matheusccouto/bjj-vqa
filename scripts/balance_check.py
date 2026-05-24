"""Check category and subject balance in samples.json.

Prints a warning string if any bucket exceeds 40% of total, or empty string if balanced.
"""

import json
import sys
from collections import Counter
from pathlib import Path

THRESHOLD = 0.4

data_dir = Path(__file__).parent.parent / "data"
samples_path = data_dir / "samples.json"

if not samples_path.exists():
    sys.exit(0)

samples = json.loads(samples_path.read_text())
total = len(samples)
if total == 0:
    sys.exit(0)

categories = Counter(s.get("category", "unknown") for s in samples)
subjects = Counter(s.get("subject", "unknown") for s in samples)

warnings: list[str] = []

for bucket_name, counts in [("category", categories), ("subject", subjects)]:
    for name, count in counts.items():
        pct = count / total
        if pct > THRESHOLD:
            warnings.append(f"{bucket_name}={name} is {pct:.0%} ({count}/{total})")

if warnings:
    print("; ".join(warnings))
