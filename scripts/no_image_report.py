"""Aggregate no-images eval log into a stem-leak diagnostic report.

Usage:
    uv run python scripts/no_image_report.py <log_dir>

log_dir should contain the JSON log output from:
    uv run inspect eval src/bjj_vqa/task.py@bjj_vqa_no_images --log-format json

Outputs a Markdown report to stdout.
"""

import json
import sys
from pathlib import Path


def _load_log(log_dir: Path) -> dict:
    """Load the most recent JSON eval log from a directory."""
    logs = sorted(log_dir.glob("*.json"))
    if not logs:
        print(f"ERROR: No JSON log files found in {log_dir}", file=sys.stderr)
        sys.exit(1)
    return json.loads(logs[-1].read_text())


def _is_correct(sample: dict) -> bool:
    return sample.get("score", {}).get("value") == 1


def _accuracy(samples: list[dict]) -> float:
    """Compute overall accuracy from sample results."""
    if not samples:
        return 0.0
    return sum(1 for s in samples if _is_correct(s)) / len(samples)


def _group_accuracy(samples: list[dict], key: str) -> dict[str, tuple[int, int]]:
    """Compute (correct, total) per group value for a metadata key."""
    groups: dict[str, list[int]] = {}
    for s in samples:
        val = s.get("metadata", {}).get(key, "unknown")
        score = s.get("score", {}).get("value", 0)
        groups.setdefault(val, []).append(score)
    return {grp: (sum(scores), len(scores)) for grp, scores in sorted(groups.items())}


def main() -> None:
    """Parse a no-images eval log and print a stem-leak diagnostic report."""
    if len(sys.argv) < 2:
        print(
            "Usage: uv run python scripts/no_image_report.py <log_dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    log_dir = Path(sys.argv[1])
    log = _load_log(log_dir)

    samples = log.get("samples", [])
    total = len(samples)
    overall = _accuracy(samples)

    lines = [
        "# No-Image Ablation Report",
        "",
        f"Eval log: `{log_dir}`",
        f"Total questions: {total}",
        f"Overall accuracy (no image): **{overall:.1%}**",
        "",
        "> Questions answered correctly without the image are candidates"
        " for stem-leak review.",
        "",
    ]

    # Breakdown tables
    for group_key in ("subject", "category", "experience_level"):
        groups = _group_accuracy(samples, group_key)
        lines.append(f"## By {group_key}")
        lines.append("")
        lines.append(f"| {group_key} | Correct | Total | Accuracy |")
        lines.append("|---|---|---|---|")
        for val, (correct, count) in groups.items():
            acc = correct / count if count else 0
            lines.append(f"| {val} | {correct} | {count} | {acc:.1%} |")
        lines.append("")

    # Individual questions answered correctly (stem leak candidates)
    correct_samples = [s for s in samples if _is_correct(s)]

    lines.append("## Stem-leak candidates (answered correctly without image)")
    lines.append("")
    if correct_samples:
        lines.append("| ID | Subject | Experience | Question (truncated) |")
        lines.append("|---|---|---|---|")
        for s in sorted(correct_samples, key=lambda x: x.get("id", "")):
            sid = s.get("id", "?")
            subj = s.get("metadata", {}).get("subject", "?")
            exp = s.get("metadata", {}).get("experience_level", "?")
            # question text may be in input messages
            q = ""
            for msg in s.get("input", []):
                for part in msg.get("content", []):
                    if isinstance(part, dict) and part.get("type") == "text":
                        q = part["text"][:60].replace("\n", " ")
                        break
                if q:
                    break
            lines.append(f"| {sid} | {subj} | {exp} | {q}... |")
    else:
        lines.append("None — no questions answered correctly without the image.")

    lines.append("")
    lines.append("---")
    lines.append(
        "_Run `uv run bjj-vqa rubric <id>` on each candidate to determine "
        "whether it is a true stem leak or a coincidental correct guess._",
    )

    print("\n".join(lines))


if __name__ == "__main__":
    main()
