"""BJJ-VQA Evaluation Demo — interactive leaderboard & question browser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import gradio as gr
from datasets import load_dataset

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RESULTS_PATH = Path(__file__).parent / "eval_results.json"
DEMO_TITLE = "BJJ-VQA — How well do VLMs understand Jiu-Jitsu?"
DEMO_DESC = (
    "Explore model performance on the **Brazilian Jiu-Jitsu Visual Q&A** benchmark. "
    "Compare accuracy across models, categories, experience levels, and subjects, "
    "then browse individual questions to see which models got them right or wrong.",
)

CATEGORIES = ["gi", "no_gi"]
LEVELS = ["beginner", "intermediate", "advanced"]
SUBJECTS = [
    "guard",
    "passing",
    "submissions",
    "controls",
    "escapes",
    "takedowns",
]

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _load_results() -> list[dict[str, Any]]:
    """Load evaluation results from eval_results.json."""
    if RESULTS_PATH.exists():
        return json.loads(RESULTS_PATH.read_text())
    return []


def _load_dataset() -> Any:
    """Load BJJ-VQA dataset from HuggingFace Hub."""
    try:
        return load_dataset(
            "couto/bjj-vqa",
            split="test",
            trust_remote_code=True,
        )
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Leaderboard builders
# ---------------------------------------------------------------------------


def _build_overall_df(results: list[dict[str, Any]]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for entry in results:
        r = entry.get("results", {}).get("overall", {})
        rows.append(
            [
                entry.get("model", "?"),
                f"{r.get('accuracy', 0):.1%}",
                r.get("correct", 0),
                r.get("total", 0),
            ],
        )
    return rows


def _build_breakdown_df(
    results: list[dict[str, Any]],
    dimension: str,
    keys: list[str],
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for entry in results:
        model = entry.get("model", "?")
        by_dim = entry.get("results", {}).get(f"by_{dimension}", {})
        row = [model] + [f"{by_dim.get(k, {}).get('accuracy', 0):.1%}" for k in keys]
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Question browser
# ---------------------------------------------------------------------------


def _build_question_rows(dataset: Any) -> list[list[Any]]:
    if dataset is None:
        return []
    return [
        [
            s["id"],
            s["category"],
            s["subject"],
            s["experience_level"],
            s["question"],
        ]
        for s in dataset
    ]


def _format_choices(choices: list[str], answer: str) -> str:
    lines = []
    for letter, text in zip("ABCD", choices, strict=False):
        marker = " ✅" if letter == answer else ""
        lines.append(f"**{letter}.** {text}{marker}")
    return "\n".join(lines)


def _get_question_detail(
    qid: str,
    results: list[dict[str, Any]],
    dataset: Any,
) -> tuple[Any, str, str, str]:
    """Return (image, question_md, tags_md, models_md) for a question ID."""
    if dataset is None:
        return None, "No dataset loaded", "", ""

    sample = None
    for s in dataset:
        if s["id"] == qid:
            sample = s
            break
    if sample is None:
        return None, f"Question {qid} not found", "", ""

    choices_md = _format_choices(sample["choices"], sample["answer"])
    question_md = f"### {sample['question']}\n\n{choices_md}"
    tags_md = (
        f"**Category:** {sample['category']} | "
        f"**Subject:** {sample['subject']} | "
        f"**Level:** {sample['experience_level']}"
    )

    right_models: list[str] = []
    wrong_models: list[str] = []
    for entry in results:
        model = entry.get("model", "?")
        pred = entry.get("results", {}).get("per_question", {}).get(qid)
        if pred == sample["answer"]:
            right_models.append(model)
        elif pred is not None:
            wrong_models.append(model)

    models_md = ""
    if right_models:
        models_md += f"✅ Correct: {', '.join(right_models)}\n\n"
    if wrong_models:
        models_md += f"❌ Wrong: {', '.join(wrong_models)}"

    return sample["image"], question_md, tags_md, models_md


# ---------------------------------------------------------------------------
# Build the app
# ---------------------------------------------------------------------------


def build_app() -> gr.Blocks:
    """Build and return the Gradio Blocks app."""
    results = _load_results()
    dataset = _load_dataset()
    question_rows = _build_question_rows(dataset)

    with gr.Blocks(title="BJJ-VQA Demo", theme=gr.themes.Soft()) as app:
        gr.Markdown(f"# {DEMO_TITLE}\n\n{DEMO_DESC}")

        with gr.Tabs():
            # -- Leaderboard --
            with gr.TabItem("🏆 Leaderboard"):
                gr.Markdown("## Overall Accuracy")
                gr.Dataframe(
                    headers=["Model", "Accuracy", "Correct", "Total"],
                    value=_build_overall_df(results),
                    interactive=False,
                    column_widths=[200, 120, 100, 80],
                )

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### By Category")
                        gr.Dataframe(
                            headers=["Model", *CATEGORIES],
                            value=_build_breakdown_df(
                                results,
                                "category",
                                CATEGORIES,
                            ),
                            interactive=False,
                        )
                    with gr.Column():
                        gr.Markdown("### By Experience Level")
                        gr.Dataframe(
                            headers=["Model", *LEVELS],
                            value=_build_breakdown_df(
                                results,
                                "experience_level",
                                LEVELS,
                            ),
                            interactive=False,
                        )
                    with gr.Column():
                        gr.Markdown("### By Subject")
                        gr.Dataframe(
                            headers=["Model", *SUBJECTS],
                            value=_build_breakdown_df(
                                results,
                                "subject",
                                SUBJECTS,
                            ),
                            interactive=False,
                        )

            # -- Question Browser --
            with gr.TabItem("🔍 Question Browser"):
                question_table = gr.Dataframe(
                    headers=["ID", "Category", "Subject", "Level", "Question"],
                    value=question_rows,
                    interactive=False,
                    column_widths=[60, 80, 100, 100, None],
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        detail_image = gr.Image(
                            label="Question Image",
                            height=350,
                        )
                    with gr.Column(scale=1):
                        detail_question = gr.Markdown(
                            "Select a question above ↗",
                        )
                        detail_tags = gr.Markdown()
                        detail_models = gr.Markdown()

                def on_select(
                    evt: gr.SelectData,
                ) -> tuple[Any, str, str, str]:
                    if evt.row_value is None:
                        return None, "", "", ""
                    qid = evt.row_value[0]
                    img, q_md, tags_md, models_md = _get_question_detail(
                        qid,
                        results,
                        dataset,
                    )
                    return img, q_md, tags_md, models_md

                question_table.select(
                    on_select,
                    outputs=[
                        detail_image,
                        detail_question,
                        detail_tags,
                        detail_models,
                    ],
                )

        gr.Markdown(
            "Built with ❤️ for the BJJ community | "
            "[GitHub](https://github.com/matheusccouto/bjj-vqa) | "
            "[Dataset](https://huggingface.co/datasets/couto/bjj-vqa)",
        )

    return app


if __name__ == "__main__":
    build_app().launch()
