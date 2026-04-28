"""Load and manipulate BJJ-VQA evaluation results."""

import json
from pathlib import Path
from typing import Any

# Path to results file — can be overridden by env var
_RESULTS_DIR = Path(__file__).parent.parent


def load_results() -> dict[str, Any]:
    """Load evaluation results JSON."""
    results_path = _RESULTS_DIR / "results.json"
    with open(results_path) as f:
        return json.load(f)


def model_names(results: dict) -> list[str]:
    """Return sorted list of model names."""
    return sorted(results["models"].keys())


def per_model_accuracy(results: dict) -> dict[str, float]:
    """Return overall accuracy per model."""
    return {m: d["accuracy"] for m, d in results["models"].items()}


def per_category_accuracy(results: dict) -> dict[str, dict[str, float]]:
    """Return accuracy per model x category."""
    return {m: d.get("by_category", {}) for m, d in results["models"].items()}


def per_subject_accuracy(results: dict) -> dict[str, dict[str, float]]:
    """Return accuracy per model x subject."""
    return {m: d.get("by_subject", {}) for m, d in results["models"].items()}


def per_experience_accuracy(results: dict) -> dict[str, dict[str, float]]:
    """Return accuracy per model x experience level."""
    return {m: d.get("by_experience_level", {}) for m, d in results["models"].items()}


def per_question_correctness(results: dict) -> dict[str, dict[str, bool]]:
    """Return correctness per model x question_id."""
    return {m: d.get("questions", {}) for m, d in results["models"].items()}


def category_sample_counts(results: dict) -> dict[str, int]:
    """Return number of samples per category."""
    return results.get("sample_counts", {}).get("by_category", {})


def subject_sample_counts(results: dict) -> dict[str, int]:
    """Return number of samples per subject."""
    return results.get("sample_counts", {}).get("by_subject", {})


def experience_sample_counts(results: dict) -> dict[str, int]:
    """Return number of samples per experience level."""
    return results.get("sample_counts", {}).get("by_experience_level", {})
