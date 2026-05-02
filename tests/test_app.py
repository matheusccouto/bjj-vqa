"""Tests for the Gradio leaderboard app."""

from pathlib import Path
from unittest.mock import patch

import pytest
from inspect_ai.log import (
    EvalConfig,
    EvalDataset,
    EvalLog,
    EvalMetric,
    EvalPlan,
    EvalResults,
    EvalSample,
    EvalScore,
    EvalSpec,
    EvalStats,
    write_eval_log,
)
from inspect_ai.scorer import Score


def _make_eval_log(
    model: str,
    accuracy: float,
    per_category: dict | None = None,
    per_subject: dict | None = None,
    samples: list[dict] | None = None,
) -> EvalLog:
    """Create a minimal EvalLog for testing."""
    metrics: dict[str, EvalMetric] = {
        "accuracy": EvalMetric(name="accuracy", value=accuracy),
    }
    if per_category:
        metrics["accuracy[grouped=category]"] = EvalMetric(
            name="accuracy[grouped=category]",
            value=0,
            metadata={"value": per_category},
        )
    if per_subject:
        metrics["accuracy[grouped=subject]"] = EvalMetric(
            name="accuracy[grouped=subject]",
            value=0,
            metadata={"value": per_subject},
        )

    eval_samples = [
        EvalSample(
            id=s.get("id", f"q{i}"),
            epoch=1,
            input=[{"role": "user", "content": [{"type": "text", "text": "test?"}]}],  # ty: ignore[invalid-argument-type]
            choices=["A", "B"],
            target=s.get("target", "A"),
            output={"message": {"role": "assistant", "content": s.get("target", "A")}},  # ty: ignore[invalid-argument-type]
            score=Score(value=s.get("score", "A"), answer=s.get("target", "A")),  # ty: ignore[unknown-argument]
            metadata=s.get("metadata", {}),
        )
        for i, s in enumerate(samples or [])
    ]

    return EvalLog(
        version=2,
        status="success",
        eval=EvalSpec(
            eval_id="test-1",
            run_id="test-run-1",
            created="2026-05-01T12:00:00Z",
            task="bjj_vqa",
            task_version=0,
            task_file="src/bjj_vqa/task.py",
            task_id="test-1",
            task_args={},
            task_args_passed={},
            dataset=EvalDataset(
                name="samples.json",
                location="data/samples.json",
                samples=3,
            ),
            model=model,
            model_generate_config={},  # ty: ignore[invalid-argument-type]
            model_args={},
            config=EvalConfig(),
            packages={"inspect_ai": "0.3.0"},
        ),
        plan=EvalPlan(
            name="plan",
            steps=[{"solver": "multiple_choice", "params": {}}],  # ty: ignore[invalid-argument-type]
            config={},  # ty: ignore[invalid-argument-type]
        ),
        results=EvalResults(
            total_samples=len(eval_samples),
            completed_samples=len(eval_samples),
            scores=[
                EvalScore(
                    name="accuracy",
                    scorer="choice",
                    reducer=None,
                    scored_samples=len(eval_samples),
                    unscored_samples=0,
                    params={},
                    metrics=metrics,
                ),
            ],
        ),
        stats=EvalStats(
            started_at="2026-05-01T12:00:00Z",
            completed_at="2026-05-01T12:00:30Z",
        ),
        samples=eval_samples,
        tags=[],
    )


@pytest.fixture
def logs_with_results(tmp_path: Path) -> Path:
    """Create a temporary logs directory with a valid eval log."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    log = _make_eval_log(
        model="openrouter/google/gemma-4-31b-it",
        accuracy=0.75,
        per_category={"gi": 0.8, "no_gi": 0.5},
        per_subject={"guard": 1.0, "passing": 0.5},
        samples=[
            {
                "id": "q1",
                "target": "A",
                "score": "A",
                "metadata": {"category": "gi", "subject": "guard"},
            },
            {
                "id": "q2",
                "target": "A",
                "score": "B",
                "metadata": {"category": "gi", "subject": "passing"},
            },
            {
                "id": "q3",
                "target": "B",
                "score": "B",
                "metadata": {"category": "no_gi", "subject": "guard"},
            },
            {
                "id": "q4",
                "target": "B",
                "score": "A",
                "metadata": {"category": "no_gi", "subject": "passing"},
            },
        ],
    )
    write_eval_log(
        log,
        logs_dir / "openrouter_google_gemma-4-31b-it.eval",
        format="json",
    )
    return logs_dir


@pytest.fixture
def empty_logs(tmp_path: Path) -> Path:
    """Create an empty logs directory."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()
    return logs_dir


class TestLeaderboard:
    """Tests for the leaderboard data builder."""

    def test_builds_leaderboard_with_logs(self, logs_with_results: Path):
        """Leaderboard renders with existing logs."""
        from app.app import build_leaderboard

        with patch("app.app.LOGS_DIR", logs_with_results):
            data, headers = build_leaderboard()

        assert headers == ["Model", "Overall", "By Category", "By Subject"]
        assert len(data) == 1
        assert data[0][0] == "openrouter/google/gemma-4-31b-it"
        assert data[0][1] == "75.0%"

    def test_empty_logs_returns_empty_table(self, empty_logs: Path):
        """App renders without crashing on empty logs."""
        from app.app import build_leaderboard

        with patch("app.app.LOGS_DIR", empty_logs):
            data, headers = build_leaderboard()

        assert data == []
        assert headers == ["Model", "Overall", "By Category", "By Subject"]

    def test_accuracy_computed_correctly(self, logs_with_results: Path):
        """Accuracy values computed correctly from fixture log data."""
        from app.app import _extract_accuracy

        log_path = logs_with_results / "openrouter_google_gemma-4-31b-it.eval"
        data = _extract_accuracy(log_path)

        assert data["model"] == "openrouter/google/gemma-4-31b-it"
        assert data["accuracy"] == 0.75
        assert data["per_category"] == {"gi": 0.8, "no_gi": 0.5}
        assert data["per_subject"] == {"guard": 1.0, "passing": 0.5}

    def test_app_creates_without_error(self, logs_with_results: Path):
        """Gradio app creates without error."""
        from app.app import create_app

        with patch("app.app.LOGS_DIR", logs_with_results):
            app = create_app()
        assert app is not None
