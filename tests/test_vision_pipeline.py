"""End-to-end test verifying images are sent to and processed by the model.

Skipped automatically when OPENROUTER_API_KEY is not set.
Run explicitly: uv run pytest tests/test_vision_pipeline.py -v -m vision
"""

import os

import pytest
from inspect_ai import eval as inspect_eval

from scripts.verify_vision import QUESTIONS, build_task

MODEL = "openrouter/google/gemma-4-31b-it"


@pytest.mark.vision
@pytest.mark.skipif(not os.getenv("OPENROUTER_API_KEY"), reason="requires API key")
def test_images_are_processed_by_model(tmp_path):
    """Model must score 100% on trivially visual questions.

    If any answer is wrong, images are not reaching the model correctly.
    """
    task = build_task(tmp_path)
    logs = inspect_eval(task, model=MODEL)

    assert logs, "Eval returned no results"
    assert logs[0].status != "error", "Eval did not complete successfully"
    accuracy = logs[0].results.scores[0].metrics["accuracy"].value
    n = len(QUESTIONS)
    assert accuracy == 1.0, (
        f"Model scored {round(accuracy * n)}/{n} on trivial visual questions — "
        "images are likely not being sent or processed correctly."
    )
