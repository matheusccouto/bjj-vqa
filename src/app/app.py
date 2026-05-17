"""Gradio leaderboard app for BJJ-VQA eval results."""

import os
from pathlib import Path

import gradio as gr
import pandas as pd
from inspect_ai.log import read_eval_log

LOGS_DIR = os.getenv("BJJ_VQA_LOGS_DIR", "logs")


class EvalLogRecord:
    """Wraps an eval log file and exposes convenient accessors."""

    def __init__(self, log_path: Path) -> None:
        """Initialize from an eval log file path."""
        self._log_path = log_path
        self._log = read_eval_log(log_path)

    @property
    def model_name(self) -> str:
        """Model name with 'openrouter/' prefix stripped."""
        return self._log.eval.model.replace("openrouter/", "")

    @property
    def overall_accuracy(self) -> float | None:
        """Overall accuracy, or None if the run has no results."""
        results = self._log.results
        if not results or not results.scores:
            return None
        metrics = results.scores[0].metrics
        if "accuracy" not in metrics:
            return None
        return metrics["accuracy"].value

    @property
    def timestamp(self) -> str:
        """ISO timestamp from the eval log metadata."""
        return str(self._log.eval.created)

    def to_record(self) -> dict:
        """Return a dict suitable for DataFrame.from_records."""
        return {
            "Model": self.model_name,
            "Accuracy": self.overall_accuracy,
            "Timestamp": self.timestamp,
        }


def load() -> pd.DataFrame:
    """Load leaderboard data."""
    logs = [EvalLogRecord(file) for file in Path(LOGS_DIR).glob("*.eval")]
    records = [log.to_record() for log in logs]

    return (
        pd.DataFrame.from_records(records)
        .dropna(subset="Accuracy")
        .sort_values("Timestamp", ascending=False)
        .drop_duplicates(subset="Model", keep="last")
        .sort_values("Accuracy", ascending=False)[["Model", "Accuracy"]]
        .style.format({"Accuracy": "{:.1%}"})
    )


def main() -> gr.Blocks:
    """BJJ-VQA leaderboard Gradio app."""
    with gr.Blocks(title="BJJ-VQA Leaderboard") as app:
        gr.Markdown("# BJJ-VQA Leaderboard")
        gr.Dataframe(value=load(), interactive=False)

    return app


if __name__ == "__main__":
    main().launch()
