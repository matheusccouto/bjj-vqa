"""Generate placeholder evaluation results for the demo app.

Reads samples.json and creates synthetic model evaluation results
so the demo looks realistic without requiring real evals to have run.
"""

import json
import random
from pathlib import Path
from typing import Any

random.seed(42)


def load_samples(data_dir: Path) -> list[dict[str, Any]]:
    with open(data_dir / "samples.json") as f:
        return json.load(f)


def build_sample_counts(samples: list[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {
        "by_category": {},
        "by_subject": {},
        "by_experience_level": {},
    }
    for s in samples:
        for key, field in [
            ("by_category", "category"),
            ("by_subject", "subject"),
            ("by_experience_level", "experience_level"),
        ]:
            val = s[field]
            counts[key][val] = counts[key].get(val, 0) + 1
    return counts


def simulate_model(
    name: str,
    samples: list[dict],
    base_accuracy: float,
    category_mods: dict[str, float],
    subject_mods: dict[str, float],
    experience_mods: dict[str, float],
) -> dict[str, Any]:
    """Simulate one model's evaluation results.

    Applies base accuracy plus per-category/subject/experience modifiers
    to determine whether each question is answered correctly.
    """
    random.seed(hash(name) % 2**32)

    questions: dict[str, bool] = {}
    per_cat: dict[str, list[bool]] = {}
    per_subj: dict[str, list[bool]] = {}
    per_exp: dict[str, list[bool]] = {}

    for s in samples:
        cat = s["category"]
        subj = s["subject"]
        exp = s["experience_level"]

        prob = (
            base_accuracy
            + category_mods.get(cat, 0)
            + subject_mods.get(subj, 0)
            + experience_mods.get(exp, 0)
        )
        prob = max(0.0, min(1.0, prob))
        correct = random.random() < prob

        questions[s["id"]] = correct
        per_cat.setdefault(cat, []).append(correct)
        per_subj.setdefault(subj, []).append(correct)
        per_exp.setdefault(exp, []).append(correct)

    correct_count = sum(questions.values())
    accuracy = correct_count / len(samples)

    return {
        "accuracy": round(accuracy, 4),
        "correct": correct_count,
        "total": len(samples),
        "by_category": {
            k: round(sum(v) / len(v), 4) for k, v in sorted(per_cat.items())
        },
        "by_subject": {
            k: round(sum(v) / len(v), 4) for k, v in sorted(per_subj.items())
        },
        "by_experience_level": {
            k: round(sum(v) / len(v), 4) for k, v in sorted(per_exp.items())
        },
        "questions": questions,
    }


def main() -> None:
    """Generate placeholder results and write to stdout or file."""
    repo_root = Path(__file__).parent.parent.parent
    data_dir = repo_root / "data"
    output_dir = repo_root / "demo"

    samples = load_samples(data_dir)
    counts = build_sample_counts(samples)

    models = {
        "Claude Opus 4.5": simulate_model(
            "Claude Opus 4.5",
            samples,
            base_accuracy=0.72,
            category_mods={"gi": 0.02, "no_gi": -0.04},
            subject_mods={
                "submissions": 0.03,
                "guard": 0.01,
                "controls": 0.02,
                "takedowns": -0.05,
                "passing": -0.08,
                "escapes": -0.10,
            },
            experience_mods={
                "advanced": -0.10,
                "intermediate": -0.02,
                "beginner": 0.10,
            },
        ),
        "Gemini 2.5 Pro": simulate_model(
            "Gemini 2.5 Pro",
            samples,
            base_accuracy=0.68,
            category_mods={"gi": 0.01, "no_gi": -0.02},
            subject_mods={
                "submissions": 0.05,
                "guard": -0.02,
                "controls": -0.03,
                "takedowns": 0.02,
                "passing": -0.06,
                "escapes": 0.00,
            },
            experience_mods={
                "advanced": -0.12,
                "intermediate": -0.01,
                "beginner": 0.08,
            },
        ),
        "GPT-4o": simulate_model(
            "GPT-4o",
            samples,
            base_accuracy=0.58,
            category_mods={"gi": 0.01, "no_gi": -0.03},
            subject_mods={
                "submissions": -0.02,
                "guard": 0.02,
                "controls": 0.01,
                "takedowns": -0.02,
                "passing": -0.10,
                "escapes": -0.05,
            },
            experience_mods={
                "advanced": -0.15,
                "intermediate": -0.03,
                "beginner": 0.12,
            },
        ),
        "Llama 4 Maverick": simulate_model(
            "Llama 4 Maverick",
            samples,
            base_accuracy=0.42,
            category_mods={"gi": 0.02, "no_gi": -0.03},
            subject_mods={
                "submissions": 0.04,
                "guard": -0.03,
                "controls": 0.01,
                "takedowns": -0.02,
                "passing": -0.12,
                "escapes": -0.05,
            },
            experience_mods={"advanced": -0.18, "intermediate": 0.02, "beginner": 0.06},
        ),
        "Random Baseline": simulate_model(
            "Random Baseline",
            samples,
            base_accuracy=0.25,
            category_mods={},
            subject_mods={},
            experience_mods={},
        ),
    }

    results = {
        "models": models,
        "sample_counts": counts,
        "total_samples": len(samples),
    }

    output_path = output_dir / "results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {len(models)} models × {len(samples)} samples to {output_path}")


if __name__ == "__main__":
    main()
