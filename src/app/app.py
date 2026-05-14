"""Gradio leaderboard app for BJJ-VQA eval results."""

import os
from pathlib import Path

import gradio as gr
from inspect_ai.log import read_eval_log

LOGS_DIR = Path(os.getenv("BJJ_VQA_LOGS_DIR", ".eval_results"))

EMPTY_MSG = (
    "*No eval results yet. "
    "Run `uv run inspect eval src/bjj_vqa/task.py --model <model>` "
    "and place the `.eval` log in `logs/`.*"
)


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
    model = log.eval.model

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
            metadata = metric.metadata or {}
            if "value" in metadata:
                groups_data = metadata["value"]
                if isinstance(groups_data, dict):
                    key = f"per_{group}"
                    if key in result:
                        result[key] = groups_data

    return result


def build_leaderboard() -> tuple[dict, str]:
    """Build leaderboard data from eval logs.

    Returns (dataframe_kwargs, empty_msg) for gr.Dataframe and gr.Markdown.
    """
    eval_logs = _find_eval_logs(LOGS_DIR)

    headers = ["Model", "Overall", "By Category", "By Subject"]

    if not eval_logs:
        return {"headers": headers, "value": None}, EMPTY_MSG

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

    return {"headers": headers, "value": rows}, ""


def create_app() -> gr.Blocks:
    """Create the Gradio leaderboard app."""
    with gr.Blocks(title="BJJ-VQA Leaderboard") as app:
        gr.Markdown("# BJJ-VQA Leaderboard")
        gr.Markdown(
            "Model accuracy on the BJJ-VQA benchmark. "
            "Accuracy is broken down by category (gi/no-gi) and subject.",
        )
        df = gr.Dataframe()
        empty_msg = gr.Markdown(EMPTY_MSG, visible=False)
        app.load(fn=build_leaderboard, outputs=[df, empty_msg])

    return app


if __name__ == "__main__":
    create_app().launch()
