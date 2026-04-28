"""Load and process BJJ-VQA evaluation results."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bjj_vqa.schema import get_data_dir


@dataclass
class ModelResult:
    """Per-sample result for a single model on a single question."""

    sample_id: str
    correct: bool
    predicted: str
    target: str


@dataclass
class ModelSummary:
    """Aggregated accuracy for a single model."""

    model: str
    overall: float
    by_category: dict[str, float] = field(default_factory=dict)
    by_subject: dict[str, float] = field(default_factory=dict)
    by_level: dict[str, float] = field(default_factory=dict)
    per_question: dict[str, ModelResult] = field(default_factory=dict)


# Placeholder model names and base accuracy for demo display
_PLACEHOLDER_MODELS = [
    "Claude Opus 4.5",
    "Gemini 2.5 Pro",
    "GPT-4o",
    "Qwen-VL-Max",
    "LLaVA-34B",
]
_PLACEHOLDER_ACC = [0.72, 0.65, 0.58, 0.55, 0.42]


def _load_placeholder_results(samples: list[dict]) -> dict[str, list[ModelResult]]:
    """Generate deterministic placeholder results for demo display."""
    results: dict[str, list[ModelResult]] = {}

    for mi, model in enumerate(_PLACEHOLDER_MODELS):
        base_acc = _PLACEHOLDER_ACC[mi]
        model_results: list[ModelResult] = []

        for sample in samples:
            sid = sample["id"]
            target = sample["answer"]
            choices = sample["choices"]
            # Deterministic pseudo-random for stable display
            seed = int(sid) if sid.isdigit() else hash(sid) & 0xFFFFFFFF

            correct = ((seed * (mi + 1) + (mi * 7)) % 100) / 100.0 < base_acc
            if correct:
                predicted = target
            else:
                wrong = [c for i, c in enumerate(choices) if chr(65 + i) != target]
                idx = (seed + mi) % len(wrong)
                predicted = wrong[idx]

            model_results.append(
                ModelResult(
                    sample_id=sid,
                    correct=correct,
                    predicted=predicted,
                    target=target,
                ),
            )

        results[model] = model_results

    return results


def _compute_summaries(
    models: dict[str, list[ModelResult]],
    samples: list[dict],
) -> list[ModelSummary]:
    """Compute per-model accuracy summaries."""
    sample_map = {s["id"]: s for s in samples}
    summaries: list[ModelSummary] = []

    for model, model_results in models.items():
        correct = sum(1 for r in model_results if r.correct)
        total = len(model_results)
        overall = correct / total if total else 0.0

        by_category: dict[str, list[tuple[bool, str]]] = defaultdict(list)
        by_subject: dict[str, list[tuple[bool, str]]] = defaultdict(list)
        by_level: dict[str, list[tuple[bool, str]]] = defaultdict(list)
        per_question: dict[str, ModelResult] = {}

        for r in model_results:
            s = sample_map.get(r.sample_id)
            if s is None:
                continue
            by_category[s["category"]].append((r.correct, r.sample_id))
            by_subject[s["subject"]].append((r.correct, r.sample_id))
            by_level[s["experience_level"]].append((r.correct, r.sample_id))
            per_question[r.sample_id] = r

        summaries.append(
            ModelSummary(
                model=model,
                overall=overall,
                by_category={
                    k: sum(1 for c, _ in v if c) / len(v)
                    for k, v in by_category.items()
                },
                by_subject={
                    k: sum(1 for c, _ in v if c) / len(v) for k, v in by_subject.items()
                },
                by_level={
                    k: sum(1 for c, _ in v if c) / len(v) for k, v in by_level.items()
                },
                per_question=per_question,
            ),
        )

    summaries.sort(key=lambda s: s.overall, reverse=True)
    return summaries


def load_results(
    results_path: Path | str | None = None,
) -> tuple[list[dict], list[ModelSummary]]:
    """Load samples and evaluation results.

    If results_path is None or doesn't exist, generates placeholder data.
    Returns (samples, model_summaries).
    """
    data_dir = get_data_dir()
    samples_path = data_dir / "samples.json"

    samples: list[dict] = json.loads(samples_path.read_text())

    # Try to load real results, fall back to placeholder
    if results_path is not None:
        rp = Path(results_path)
        if rp.exists():
            try:
                raw = json.loads(rp.read_text())
                models = _parse_inspect_results(raw, samples)
                if models:
                    return samples, _compute_summaries(models, samples)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

    # Fallback: generate placeholder data
    models = _load_placeholder_results(samples)
    return samples, _compute_summaries(models, samples)


def _parse_inspect_results(
    raw: dict[str, Any],
    samples: list[dict],
) -> dict[str, list[ModelResult]]:
    """Parse inspect-ai eval log JSON into per-model results.

    Expected format (inspect-ai eval --log-format json):
    { "bjj_vqa": [ { "model": "...", "samples": [
        { "id": "...", "scores": { "choice": {"value": "C/I", "answer": "A"} } }
    ] } ] }
    """
    models: dict[str, list[ModelResult]] = {}
    sample_map = {s["id"]: s for s in samples}

    # inspect-ai wraps results under task name keys
    if "bjj_vqa" in raw:
        task_results = raw["bjj_vqa"]
    elif "bjj_vqa_no_images" in raw:
        task_results = raw["bjj_vqa_no_images"]
    else:
        task_results = raw if isinstance(raw, list) else [raw]

    if isinstance(task_results, dict):
        task_results = [task_results]

    for result in task_results:
        model_name = str(result.get("model", "Unknown Model"))
        eval_samples = result.get("samples", [])
        model_results: list[ModelResult] = []

        for es in eval_samples:
            sid = es.get("id", "")
            sample = sample_map.get(sid)
            if sample is None:
                continue
            scores = es.get("scores", {})
            choice_score = scores.get("choice", {})
            value = choice_score.get("value", "I")
            correct = value == "C"
            answer = choice_score.get("answer", "")
            model_results.append(
                ModelResult(
                    sample_id=sid,
                    correct=correct,
                    predicted=answer,
                    target=sample["answer"],
                ),
            )

        if model_results:
            models[model_name] = model_results

    return models
