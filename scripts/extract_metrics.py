"""Extract evaluation metrics from inspect-ai JSON log."""

import json
import sys
from pathlib import Path


def main(log_dir: str) -> None:
    """Extract accuracy from eval results and output to GITHUB_OUTPUT."""
    results_dir = Path(log_dir)
    eval_files = list(results_dir.glob("*.json"))

    if not eval_files:
        print("No eval results found")
        sys.exit(1)

    with eval_files[0].open() as f:
        data = json.load(f)

    scores = data.get("results", {}).get("scores", [])
    if not scores:
        print("No scores found")
        sys.exit(1)

    accuracy = scores[0].get("metrics", {}).get("accuracy", {}).get("value", 0)
    print(f"accuracy={accuracy}")

    # Output to GITHUB_OUTPUT if available
    github_output = sys.environ.get("GITHUB_OUTPUT")
    if github_output:
        with Path(github_output).open("a") as f:
            f.write(f"accuracy={accuracy}\n")

    # Print per-category breakdowns
    for score in scores:
        for metric_name, metric_data in score.get("metrics", {}).items():
            if "grouped" in metric_name:
                value = metric_data.get("value", "N/A")
                print(f"{metric_name}={value}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval_results")
