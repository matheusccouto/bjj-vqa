"""BJJ-VQA Evaluation Demo — interactive Gradio app.

Shows a model leaderboard and a question browser so BJJ practitioners
can see how VLMs perform on the benchmark.
"""

import json
from pathlib import Path

import gradio as gr
from PIL import Image

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "eval_results"


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def load_questions() -> list[dict]:
    """Load the benchmark questions from data/samples.json."""
    with open(DATA_DIR / "samples.json", encoding="utf-8") as f:
        return json.load(f)


def load_results() -> dict:
    """Load evaluation results from a JSON file.

    Falls back to placeholder data if no real results exist.
    Tries ``eval_results/results.json`` first, then the placeholder file.
    """
    real = RESULTS_DIR / "results.json"
    placeholder = RESULTS_DIR / "placeholder_results.json"
    path = real if real.exists() else placeholder
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Leaderboard helpers
# ---------------------------------------------------------------------------

SUBJECTS = ["guard", "passing", "submissions", "controls", "escapes", "takedowns"]
EXPERIENCE = ["beginner", "intermediate", "advanced"]


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_leaderboard_table(results: dict) -> list[list]:
    """Build a row list for the leaderboard dataframe."""
    rows = []
    for m in sorted(
        results["models"], key=lambda x: x["overall_accuracy"], reverse=True,
    ):
        row = [
            m["name"],
            _fmt_pct(m["overall_accuracy"]),
            _fmt_pct(m["accuracy_by_category"]["gi"]),
            _fmt_pct(m["accuracy_by_category"]["no_gi"]),
            _fmt_pct(m["accuracy_by_experience"].get("beginner", 0)),
            _fmt_pct(m["accuracy_by_experience"].get("intermediate", 0)),
            _fmt_pct(m["accuracy_by_experience"].get("advanced", 0)),
        ]
        row += [_fmt_pct(m["accuracy_by_subject"].get(s, 0)) for s in SUBJECTS]
        rows.append(row)
    return rows


def build_leaderboard_headers() -> list[str]:
    return [
        "Model",
        "Overall",
        "Gi",
        "No-Gi",
        "Beginner",
        "Intermediate",
        "Advanced",
    ] + [s.capitalize() for s in SUBJECTS]


# ---------------------------------------------------------------------------
# Question browser helpers
# ---------------------------------------------------------------------------


def _question_choices(question: dict) -> str:
    """Build a markdown summary of the question section (no answer revealed)."""
    lines = []
    for i, choice in enumerate(question["choices"]):
        letter = chr(ord("A") + i)
        lines.append(f"- **{letter}** {choice}")
    return "\n".join(lines)


def build_question_list(questions: list[dict]) -> list[str]:
    """Return dropdown labels like '00001 — submissions (intermediate)'."""
    items = []
    for q in questions:
        label = (
            f"{q['id']} — {q['subject']} "
            f"({q['experience_level']}, {q['category'].replace('_', '-')})"
        )
        items.append(label)
    return items


def load_question_image(image_rel: str) -> Image.Image | None:
    """Load a question image, returning None on failure."""
    path = DATA_DIR / image_rel
    if not path.exists():
        return None
    return Image.open(path)


def render_question(question_idx: int) -> tuple:
    """Render a question card for the browser.

    Returns (image, question_text, choices_md, answer, metadata).
    """
    questions = load_questions()
    if question_idx < 0 or question_idx >= len(questions):
        return (None, "", "", "", "")

    q = questions[question_idx]
    img = load_question_image(q["image"])
    meta = (
        f"**Subject:** {q['subject']}  |  "
        f"**Level:** {q['experience_level']}  |  "
        f"**Category:** {q['category'].replace('_', '-')}"
    )
    return (
        img,
        q["question"],
        _question_choices(q),
        q["answer"],
        meta,
    )


def render_model_performance(question_idx: int) -> list[list]:
    """Build a table showing which models got this question right/wrong."""
    questions = load_questions()
    if question_idx < 0 or question_idx >= len(questions):
        return []

    q = questions[question_idx]
    results = load_results()
    rows = []
    for m in sorted(
        results["models"], key=lambda x: x["overall_accuracy"], reverse=True,
    ):
        correct = m["per_question"].get(q["id"], None)
        if correct is True:
            status = "✅"
        elif correct is False:
            status = "❌"
        else:
            status = "—"
        rows.append([m["name"], status])
    return rows


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------


def _leaderboard_tab() -> gr.Column:
    """Build the leaderboard tab."""
    results = load_results()
    headers = build_leaderboard_headers()
    data = build_leaderboard_table(results)

    gr.Markdown(
        "## 🏆 Model Comparison\n"
        "Models ranked by overall accuracy on the BJJ-VQA benchmark. "
        "Breakdowns by category, experience level, and subject.",
    )
    table = gr.Dataframe(
        headers=headers,
        values=data,
        interactive=False,
        wrap=True,
        column_widths=["200px"] + ["80px"] * (len(headers) - 1),
    )
    gr.Markdown(
        "💡 *Results shown are placeholder data. Replace "
        "`eval_results/placeholder_results.json` with real evaluation outputs.*",
    )
    return table


def _question_browser_tab() -> gr.Column:
    """Build the question browser tab."""
    questions = load_questions()
    question_labels = build_question_list(questions)

    with gr.Column():
        gr.Markdown("## 🔍 Question Browser")
        dropdown = gr.Dropdown(
            choices=question_labels,
            label="Select a question",
            value=question_labels[0],
            interactive=True,
        )

        with gr.Row():
            with gr.Column(scale=1):
                image_display = gr.Image(
                    label="Frame", type="pil", height=400, width=600,
                )
            with gr.Column(scale=2):
                question_text = gr.Markdown("")
                choices_md = gr.Markdown("")
                metadata = gr.Markdown("")
                answer_display = gr.Textbox(
                    label="Correct Answer", interactive=False, visible=True,
                )

        gr.Markdown("### Per-Model Performance")
        model_table = gr.Dataframe(
            headers=["Model", "Correct?"],
            interactive=False,
        )

    def _on_select(evt: gr.SelectData | str) -> tuple:
        label = evt.value if isinstance(evt, gr.SelectData) else evt
        idx = question_labels.index(label) if label in question_labels else 0
        img, q_text, choices, answer, meta = render_question(idx)
        perf = render_model_performance(idx)
        return (img, q_text, choices, answer, meta, perf)

    dropdown.select(
        fn=_on_select,
        inputs=[dropdown],
        outputs=[
            image_display,
            question_text,
            choices_md,
            answer_display,
            metadata,
            model_table,
        ],
    )

    # Initial render
    img, q_text, choices, answer, meta = render_question(0)
    perf = render_model_performance(0)
    return (
        dropdown,
        image_display,
        question_text,
        choices_md,
        answer_display,
        metadata,
        model_table,
        img,
        q_text,
        choices,
        answer,
        meta,
        perf,
    )


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------


def create_app() -> gr.Blocks:
    """Create and return the Gradio Blocks app."""
    with gr.Blocks(
        title="BJJ-VQA — Can AI understand Jiu-Jitsu?",
        theme=gr.themes.Soft(),
        css="""
        .question-image { max-height: 400px; }
        """,
    ) as app:
        gr.Markdown(
            "# 🥋 BJJ-VQA: Can AI Understand Jiu-Jitsu?\n"
            "A Visual Question Answering benchmark that tests whether "
            "Vision-Language Models can reason about Brazilian Jiu-Jitsu "
            "mechanics, not just recognize technique names.",
        )

        with gr.Tabs():
            with gr.TabItem("🏆 Leaderboard"):
                _leaderboard_tab()

            with gr.TabItem("🔍 Question Browser"):
                _question_browser_tab()

        gr.Markdown(
            "---\n"
            "📊 [Dataset on HuggingFace]"
            "(https://huggingface.co/datasets/couto/bjj-vqa) · "
            "💻 [GitHub](https://github.com/matheusccouto/bjj-vqa) · "
            "📄 [Methodology](https://github.com/matheusccouto/bjj-vqa/blob/main/docs/methodology.md)",
        )

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    app = create_app()
    app.launch()


if __name__ == "__main__":
    main()
