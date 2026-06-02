"""Compute PR description text after generating new questions.

Reads data/samples.json and writes /tmp/pr_body.txt with:
- Number of questions added (vs previous commit)
- Balance warning if any category or subject bucket exceeds 40%
"""

import json
from collections import Counter
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).parent.parent
    samples_path = repo_root / "data" / "samples.json"
    samples: list[dict] = json.loads(samples_path.read_text())

    total = len(samples)

    # Count new questions (those not in the previous commit)
    new_count = _count_new_questions(repo_root, samples)

    # Bucket percentages
    category_counts: Counter[str] = Counter()
    subject_counts: Counter[str] = Counter()
    for s in samples:
        category_counts[s.get("category", "unknown")] += 1
        subject_counts[s.get("subject", "unknown")] += 1

    warnings: list[str] = []
    for bucket_name, counts in [("category", category_counts), ("subject", subject_counts)]:
        for value, count in counts.most_common():
            pct = count / total * 100
            if pct > 40:
                warnings.append(
                    f"- **{bucket_name} `{value}`**: {count}/{total} ({pct:.1f}%) exceeds 40%% threshold"
                )

    lines: list[str] = []
    lines.append(f"**Questions added:** {new_count}")
    lines.append(f"**Total questions in dataset:** {total}")
    if warnings:
        lines.append("")
        lines.append("### ⚠️ Balance Warnings")
        lines.extend(warnings)
    else:
        lines.append("")
        lines.append("✅ All category and subject buckets are within the 40% threshold.")

    body = "\n".join(lines) + "\n"
    Path("/tmp/pr_body.txt").write_text(body)
    print(body)


def _count_new_questions(repo_root: Path, current_samples: list[dict]) -> int:
    """Count questions in current samples.json that weren't in the previous commit."""
    import subprocess  # noqa: S404

    try:
        result = subprocess.run(  # noqa: S603
            ["git", "show", "HEAD:data/samples.json"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            check=False,
        )
        if result.returncode != 0:
            # No previous commit with samples.json — all are new
            return len(current_samples)

        previous: list[dict] = json.loads(result.stdout)
        prev_ids = {r["id"] for r in previous}
        new_ids = [r["id"] for r in current_samples if r["id"] not in prev_ids]
        return len(new_ids)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return len(current_samples)


if __name__ == "__main__":
    main()
