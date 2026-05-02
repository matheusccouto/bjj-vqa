"""Gradio leaderboard app for BJJ-VQA eval results."""

from pathlib import Path

import gradio as gr
from inspect_ai.log import EvalLog, read_eval_log

LOGS_DIR = Path(__file__).parent.parent.parent / "logs"


def _find_eval_logs(logs_dir: Path) -> list[Path]:
    """Return sorted list of .eval log files in the logs directory."""
    if not logs_dir.is_dir():
        return []
    return sorted(logs_dir.glob("*.eval"))


def _extract_accuracy(log_path: Path) -> dict:
    """Extract overall and grouped accuracy from an eval log.

    Returns dict with:
    - model: model identifier string
    - accuracy: overall accuracy (float or None)
    - per_category: {category: accuracy}
    - per_subject: {subject: accuracy}
    """
    log = read_eval_log(log_path, format="json")
    model = log.eval.model if hasattr(log.eval, "model") else str(log.eval.model)

    result: dict = {
        "model": model,
        "accuracy": None,
        "per_category": {},
        "per_subject": {},
    }

    if not log.results or not log.results.scores:
        return result

    scores = log.results.scores[0]
    metrics = scores.metrics

    # Overall accuracy
    if "accuracy" in metrics:
        result["accuracy"] = metrics["accuracy"].value

    # Grouped metrics (e.g., accuracy[grouped=category])
    for name, metric in metrics.items():
        if name.startswith("accuracy[grouped="):
            group = name.split("grouped=")[1].rstrip("]")
            if "value" in (metric.metadata or {}):
                groups_data = metric.metadata["value"]
            else:
                # Try to compute from samples
                groups_data = _compute_grouped_accuracy(log, group)

            if isinstance(groups_data, dict):
                key = f"per_{group}"
                if key in result:
                    result[key] = groups_data

    # If grouped metrics weren't in the log, compute from samples
    if not result["per_category"]:
        result["per_category"] = _compute_grouped_accuracy(log, "category")
    if not result["per_subject"]:
        result["per_subject"] = _compute_grouped_accuracy(log, "subject")

    return result


def _compute_grouped_accuracy(
    log: "EvalLog",
    group: str,
) -> dict[str, float]:
    """Compute accuracy per group from per-sample results."""
    if not log.samples:
        return {}

    groups: dict[str, list[int]] = {}
    for sample in log.samples:
        if sample.score is None:
            continue
        group_val = sample.metadata.get(group, "unknown")
        is_correct = 1 if sample.score.value == 1 else 0
        groups.setdefault(group_val, []).append(is_correct)

    return {k: sum(v) / len(v) for k, v in groups.items()}


def build_leaderboard() -> tuple[list[list], list]:
    """Build leaderboard data from eval logs.

    Returns (data, headers) for gr.Dataframe.
    Data rows: [model, overall_accuracy, category_accuracy_str, subject_accuracy_str]
    """
    eval_logs = _find_eval_logs(LOGS_DIR)

    if not eval_logs:
        return [], ["Model", "Overall", "By Category", "By Subject"]

    rows = []
    for log_path in eval_logs:
        data = _extract_accuracy(log_path)
        acc = f"{data['accuracy']:.1%}" if data["accuracy"] is not None else "N/A"

        cat_parts = []
        for cat, val in sorted(data["per_category"].items()):
            cat_parts.append(f"{cat}: {val:.1%}")
        cat_str = "\n".join(cat_parts) if cat_parts else "N/A"

        sub_parts = []
        for sub, val in sorted(data["per_subject"].items()):
            sub_parts.append(f"{sub}: {val:.1%}")
        sub_str = "\n".join(sub_parts) if sub_parts else "N/A"

        rows.append([data["model"], acc, cat_str, sub_str])

    headers = ["Model", "Overall", "By Category", "By Subject"]
    return rows, headers


def create_app() -> gr.Blocks:
    """Create the Gradio leaderboard app."""
    data, headers = build_leaderboard()

    with gr.Blocks(title="BJJ-VQA Leaderboard") as app:
        gr.Markdown("# BJJ-VQA Leaderboard")
        gr.Markdown(
            "Model accuracy on the BJJ-VQA benchmark. "
            "Accuracy is broken down by category (gi/no-gi) and subject.",
        )
        gr.Dataframe(
            headers=headers,
            value=data or None,
            datatype=["str", "str", "str", "str"],
        )
        if not data:
            gr.Markdown(
                "*No eval results yet. "
                "Run `uv run inspect eval src/bjj_vqa/task.py --model <model>` "
                "and place the `.eval` log in `logs/`.*",
            )

    return app


if __name__ == "__main__":
    create_app().launch()
