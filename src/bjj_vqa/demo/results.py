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


MODEL_NAMES = [
    "GPT-4V",
    "Gemini Pro Vision",
    "Claude 3 Opus",
    "Qwen-VL-Max",
    "LLaVA-34B",
]


def _load_placeholder_results(
    samples: list[dict],
) -> dict[str, list[ModelResult]]:
    """Generate placeholder results for multiple models.

    Uses deterministic pseudo-randomness so results are stable across reloads.
    """
    results: dict[str, list[ModelResult]] = {m: [] for m in MODEL_NAMES}

    for sample in samples:
        sid = sample["id"]
        target = sample["answer"]
        choices = sample["choices"]
        seed = int(sid) if sid.isdigit() else hash(sid) & 0xFFFFFFFF

        for mi, model in enumerate(MODEL_NAMES):
            # GPT-4V ~70%, Gemini ~65%, Claude ~72%, Qwen ~60%, LLaVA ~45%
            base_acc = [0.70, 0.65, 0.72, 0.60, 0.45][mi]
            rand_val = ((seed * (mi + 1) * 17 + 31 * (mi + 1)) % 100) / 100.0
            correct = rand_val < base_acc

            if correct:
                predicted = target
            else:
                wrong = [c for i, c in enumerate(choices) if chr(65 + i) != target]
                idx = (seed + mi) % len(wrong)
                predicted = wrong[idx]

            results[model].append(
                ModelResult(
                    sample_id=sid,
                    correct=correct,
                    predicted=predicted,
                    target=target,
                ),
            )

    return results


def _compute_summaries(
    models: dict[str, list[ModelResult]],
    samples: list[dict],
) -> list[ModelSummary]:
    """Compute per-model accuracy summaries."""
    summaries: list[ModelSummary] = []
    sample_map = {s["id"]: s for s in samples}

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
                    k: sum(1 for c, _ in v if c) / len(v)
                    for k, v in by_subject.items()
                },
                by_level={
                    k: sum(1 for c, _ in v if c) / len(v)
                    for k, v in by_level.items()
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
    """Parse inspect-ai eval log into per-model results.

    Expected format:
    { "bjj_vqa": [ { "samples": [ { "id":..., "scores": {...} } ] } ] }
    """
    models: dict[str, list[ModelResult]] = {}
    sample_map = {s["id"]: s for s in samples}

    task_results = raw.get("bjj_vqa", [raw]) if isinstance(raw, dict) else [raw]
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
