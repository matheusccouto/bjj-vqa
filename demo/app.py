"""BJJ-VQA Evaluation Demo — interactive Gradio app.

Shows how VLMs perform on Brazilian Jiu-Jitsu Visual Q&A:
- Leaderboard: accuracy per model, per category, per subject
- Question Browser: each question with image, choices, answer, model results
"""

import json
import os
import sys
from pathlib import Path

import gradio as gr

# Add src to path so we can import results module
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load samples and results
_DATA_DIR = Path(__file__).parent.parent / "data"
_SAMPLES = []
with open(_DATA_DIR / "samples.json") as f:
    _SAMPLES = json.load(f)

# Build lookup by id
_BY_ID: dict[str, dict] = {s["id"]: s for s in _SAMPLES}

from results import (  # noqa: E402
    category_sample_counts,
    experience_sample_counts,
    load_results,
    model_names,
    per_category_accuracy,
    per_experience_accuracy,
    per_model_accuracy,
    per_question_correctness,
    per_subject_accuracy,
    subject_sample_counts,
)

_results = load_results()


def _count_display(counts: dict[str, int], key: str) -> str:
    """Format a count with n= annotation."""
    n = counts.get(key, 0)
    return f"{key} (n={n})"


# ── Leaderboard helpers ──────────────────────────────────────────


def _build_leaderboard_data() -> list[list]:
    """Build horizontal leaderboard: one row per model, columns per dimension."""
    models = model_names(_results)
    overall = per_model_accuracy(_results)
    by_cat = per_category_accuracy(_results)
    by_subj = per_subject_accuracy(_results)
    by_exp = per_experience_accuracy(_results)

    cat_counts = category_sample_counts(_results)
    subj_counts = subject_sample_counts(_results)
    exp_counts = experience_sample_counts(_results)

    cats = sorted(cat_counts.keys())
    subjs = sorted(subj_counts.keys())
    exps = sorted(exp_counts.keys())

    rows = []
    for model in models:
        row = [
            model,
            overall[model],
        ]
        for cat in cats:
            row.append(by_cat.get(model, {}).get(cat, 0))
        for subj in subjs:
            row.append(by_subj.get(model, {}).get(subj, 0))
        for exp in exps:
            row.append(by_exp.get(model, {}).get(exp, 0))
        rows.append(row)

    return rows


def _make_leaderboard() -> gr.Dataframe:
    """Create the leaderboard dataframe component."""
    cat_counts = category_sample_counts(_results)
    subj_counts = subject_sample_counts(_results)
    exp_counts = experience_sample_counts(_results)

    cats = sorted(cat_counts.keys())
    subjs = sorted(subj_counts.keys())
    exps = sorted(exp_counts.keys())

    headers = ["Model", "Overall"]
    headers += [_count_display(cat_counts, c) for c in cats]
    headers += [_count_display(subj_counts, s) for s in subjs]
    headers += [_count_display(exp_counts, e) for e in exps]

    data = _build_leaderboard_data()

    return gr.Dataframe(
        headers=headers,
        value=data,
        datatype=["str"] + ["number"] * (len(headers) - 1),
        interactive=False,
        wrap=True,
    )


# ── Question Browser helpers ─────────────────────────────────────


def _build_question_list() -> list[str]:
    """Build list of question labels for the dropdown."""
    return [f"{s['id']}: {s['question'][:80]}..." for s in _SAMPLES]


_question_labels = _build_question_list()
_question_label_to_id = {label: label.split(":")[0] for label in _question_labels}


def _render_question(selected_label: str) -> tuple:
    """Render a single question with all model results."""
    if not selected_label:
        return "", None, "", "", "", "", ""

    qid = _question_label_to_id.get(selected_label, selected_label)
    sample = _BY_ID.get(qid)
    if sample is None:
        return "Question not found", None, "", "", "", "", ""

    models = model_names(_results)
    correctness = per_question_correctness(_results)

    # Question metadata
    meta = (
        f"**ID:** {sample['id']}  |  "
        f"**Category:** {sample['category']}  |  "
        f"**Subject:** {sample['subject']}  |  "
        f"**Level:** {sample['experience_level']}\n\n"
    )

    # Full question text
    question_text = f"### Question\n{sample['question']}"

    # Choices
    choices_lines = []
    correct_letter = sample["answer"]
    abc = "ABCD"
    for i, choice in enumerate(sample["choices"]):
        letter = abc[i]
        marker = " ✓ (correct)" if letter == correct_letter else ""
        choices_lines.append(f"- **{letter}:** {choice}{marker}")
    choices_text = "### Choices\n" + "\n".join(choices_lines)

    # Source
    source_text = f"\n\n**Source:** {sample['source']}"

    # Model results
    results_lines = ["### Model Results"]
    for model in models:
        correct = correctness.get(model, {}).get(qid, None)
        if correct is True:
            icon = "✅"
        elif correct is False:
            icon = "❌"
        else:
            icon = "—"
        results_lines.append(f"- {icon} **{model}**")
    results_text = "\n".join(results_lines)

    # Image path
    image_path = str(_DATA_DIR / sample["image"])
    if not os.path.exists(image_path):
        image_path = None

    return meta, image_path, question_text, choices_text, results_text, source_text, ""


def _make_summary_panel() -> str:
    """Build summary statistics panel."""
    total = _results["total_samples"]
    n_models = len(_results["models"])
    model_list = ", ".join(model_names(_results))

    cats = category_sample_counts(_results)
    subjs = subject_sample_counts(_results)
    exps = experience_sample_counts(_results)

    cat_str = ", ".join(f"{k}: {v}" for k, v in cats.items())
    subj_str = ", ".join(f"{k}: {v}" for k, v in subjs.items())
    exp_str = ", ".join(f"{k}: {v}" for k, v in exps.items())

    return f"""
### BJJ-VQA Benchmark

**{total}** questions across **{n_models}** models.

**Models:** {model_list}

**Categories:** {cat_str}

**Subjects:** {subj_str}

**Experience Levels:** {exp_str}

> Select a question below to browse individual results. Use the Leaderboard tab for aggregate comparisons.
"""


# ── App ───────────────────────────────────────────────────────────


def create_app() -> gr.Blocks:
    with gr.Blocks(
        title="BJJ-VQA Evaluation Demo",
        theme=gr.themes.Soft(),
        css="""
        .leaderboard table { font-size: 0.9em; }
        .gradio-container { max-width: 1200px; margin: auto; }
        """,
    ) as app:
        gr.Markdown(
            """
        # 🥋 BJJ-VQA Evaluation Demo

        **Can AI understand Brazilian Jiu-Jitsu?**

        This benchmark tests whether Vision-Language Models can reason about
        BJJ mechanics from still frames — not just recognize technique names.
        Every question requires both the image and domain knowledge to answer correctly.
        """
        )

        with gr.Tabs():
            # ── Leaderboard Tab ──────────────────────────────────
            with gr.Tab("📊 Leaderboard"):
                gr.Markdown(
                    """
                ### Model Comparison

                Accuracy per model across all dimensions. Random guessing (4-choice MCQ)
                yields 25% accuracy. Categories with small sample counts (n<5)
                should be interpreted cautiously.
                """
                )
                leaderboard = _make_leaderboard()

            # ── Question Browser Tab ──────────────────────────────
            with gr.Tab("🔍 Question Browser"):
                with gr.Row():
                    gr.Markdown(_make_summary_panel())

                with gr.Row():
                    question_dropdown = gr.Dropdown(
                        choices=_question_labels,
                        label="Select a question",
                        interactive=True,
                    )

                with gr.Row():
                    with gr.Column(scale=1):
                        question_image = gr.Image(
                            label="Image",
                            type="filepath",
                            height=400,
                        )
                    with gr.Column(scale=2):
                        question_meta = gr.Markdown("")
                        question_text = gr.Markdown("")
                        choices_md = gr.Markdown("")
                        results_md = gr.Markdown("")
                        source_md = gr.Markdown("")

                question_dropdown.change(
                    fn=_render_question,
                    inputs=[question_dropdown],
                    outputs=[
                        question_meta,
                        question_image,
                        question_text,
                        choices_md,
                        results_md,
                        source_md,
                    ],
                )

            # ── About Tab ────────────────────────────────────────
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                ### About BJJ-VQA

                BJJ-VQA is an open-source benchmark for evaluating
                Vision-Language Models on Brazilian Jiu-Jitsu visual reasoning.

                **Key facts:**
                - **57 questions** sourced from CC BY-SA instructional videos
                - **Multiple-choice format** (A/B/C/D) — random baseline = 25%
                - **6 subjects:** guard, passing, submissions, controls, escapes, takedowns
                - **3 experience levels:** beginner, intermediate, advanced
                - **Gi and no-gi** categories

                #### How it works

                Each question shows a still frame from a BJJ instructional video
                and asks *why* a specific visible detail matters. The correct answer
                requires both the image (to identify position, roles, and technique detail)
                and BJJ domain knowledge (to reason about why that detail matters).

                #### Important caveats

                - **Small dataset:** 57 questions — categories with <5 samples are
                  not statistically significant
                - **Single-frame:** temporal context (motion, transitions) is not captured
                - **English only:** questions and answers are in English
                - **Source diversity:** all questions from Cobrinha BJJ videos

                #### Links

                - [GitHub Repository](https://github.com/matheusccouto/bjj-vqa)
                - [HuggingFace Dataset](https://huggingface.co/datasets/couto/bjj-vqa)
                - [Methodology](https://github.com/matheusccouto/bjj-vqa/blob/main/docs/methodology.md)
                """
                )

    return app


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    app.launch()
