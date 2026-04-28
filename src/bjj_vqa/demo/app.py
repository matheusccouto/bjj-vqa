"""BJJ-VQA Evaluation Demo — Gradio web app.

Usage:
    bjj-vqa demo                  # Start the demo app
    bjj-vqa demo --results PATH   # Load results from a specific file
"""

from __future__ import annotations

import base64
import io
import argparse
from pathlib import Path

import gradio as gr  # type: ignore[import-untyped]
from PIL import Image

from bjj_vqa.demo.results import ModelSummary, load_results
from bjj_vqa.schema import get_data_dir

# Color palette
_COLORS = [
    "#2563eb",
    "#dc2626",
    "#16a34a",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#be185d",
]
_HEADER_COLOR = "#1e293b"
_BAR_GREEN = "#16a34a"
_BAR_ORANGE = "#ea580c"
_BAR_RED = "#dc2626"


def _accuracy_bar(value: float) -> str:
    """Render an HTML accuracy bar with percentage."""
    pct = value * 100
    if pct >= 70:
        bar_color = _BAR_GREEN
    elif pct >= 50:
        bar_color = _BAR_ORANGE
    else:
        bar_color = _BAR_RED
    return (
        '<div style="display:flex;align-items:center;gap:8px">'
        '<div style="flex:1;background:#e2e8f0;border-radius:4px;height:18px">'
        f'<div style="width:{pct}%;background:{bar_color};'
        'border-radius:4px;height:100%"></div>'
        "</div>"
        '<span style="width:50px;text-align:right;'
        f'font-variant-numeric:tabular-nums">{pct:.1f}%</span>'
        "</div>"
    )


def _build_leaderboard(summaries: list[ModelSummary]) -> str:
    """Build an HTML leaderboard table."""
    if not summaries:
        return "<p>No results available.</p>"

    all_cats = sorted({str(cat) for s in summaries for cat in s.by_category})
    all_subs = sorted({str(sub) for s in summaries for sub in s.by_subject})

    rows: list[str] = []
    for i, s in enumerate(summaries):
        color = _COLORS[i % len(_COLORS)]
        cat_cells = "".join(_accuracy_bar(s.by_category.get(c, 0.0)) for c in all_cats)
        sub_cells = "".join(
            _accuracy_bar(s.by_subject.get(sub, 0.0)) for sub in all_subs
        )
        rows.append(
            "<tr>"
            f'<td><span style="font-weight:600;color:{color}">{s.model}</span></td>'
            f"<td>{_accuracy_bar(s.overall)}</td>"
            f"<td>{cat_cells}</td>"
            f"<td>{sub_cells}</td>"
            "</tr>",
        )

    cat_headers = "".join(
        '<th style="padding:8px 12px;font-size:12px">'
        f"{c.replace('_', ' ').title()}</th>"
        for c in all_cats
    )
    sub_headers = "".join(
        '<th style="padding:8px 12px;font-size:12px">'
        f"{s.replace('_', ' ').title()}</th>"
        for s in all_subs
    )

    css_rules = (
        ".leaderboard { width:100%; border-collapse:collapse; font-size:14px; "
        "font-family:system-ui,sans-serif; }"
        f".leaderboard th {{ background:{_HEADER_COLOR}; color:white; "
        "padding:10px 12px; text-align:left; font-weight:600; }"
        ".leaderboard td { padding:10px 12px; border-bottom:1px solid #e2e8f0; }"
        ".leaderboard tr:hover td { background:#f1f5f9; }"
    )

    return f"""
    <style>{css_rules}</style>
    <table class="leaderboard">
        <thead>
            <tr>
                <th>Model</th>
                <th>Overall</th>
                <th colspan="{len(all_cats)}">By Category</th>
                <th colspan="{len(all_subs)}">By Subject</th>
            </tr>
            <tr>
                <th></th>
                <th></th>
                {cat_headers}
                {sub_headers}
            </tr>
        </thead>
        <tbody>
            {"".join(rows)}
        </tbody>
    </table>
    """


def _image_to_html(image_path: str, data_dir: Path) -> str:
    """Convert an image file to an HTML img tag."""
    img_full = data_dir / image_path
    if not img_full.exists():
        return (
            '<div style="width:400px;height:225px;background:#e2e8f0;'
            "display:flex;align-items:center;justify-content:center;"
            'color:#94a3b8">No Image</div>'
        )

    img = Image.open(img_full)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (
        f'<img src="data:image/jpeg;base64,{b64}" '
        'style="max-width:500px;max-height:350px;border-radius:8px;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.1)" />'
    )


def _build_question_card(
    sample: dict,
    summaries: list[ModelSummary],
    data_dir: Path,
) -> str:
    """Build an HTML card for a single question with model results."""
    qid = sample["id"]
    question = sample["question"]
    choices = sample["choices"]
    answer = sample["answer"]
    answer_idx = ord(answer) - ord("A")
    answer_text = choices[answer_idx] if 0 <= answer_idx < len(choices) else "?"

    category = sample.get("category", "?")
    subject = sample.get("subject", "?")
    level = sample.get("experience_level", "?")
    image_rel = sample.get("image", "")
    if isinstance(image_rel, list):
        image_rel = image_rel[0] if image_rel else ""

    image_html = _image_to_html(image_rel, data_dir)

    # Build model results
    model_rows: list[str] = []
    models_correct = 0
    models_wrong = 0
    for s in summaries:
        mr = s.per_question.get(qid)
        if mr is None:
            continue
        icon = "✅" if mr.correct else "❌"
        if mr.correct:
            models_correct += 1
        else:
            models_wrong += 1
        model_rows.append(
            "<tr>"
            f'<td style="padding:6px 12px">{icon}</td>'
            f'<td style="padding:6px 12px;font-weight:500">{s.model}</td>'
            f'<td style="padding:6px 12px;font-family:monospace">{mr.predicted}</td>'
            "</tr>",
        )

    total_models = models_correct + models_wrong
    model_summary = (
        f"{models_correct}/{total_models} correct" if total_models else "No results"
    )

    choice_html = "".join(
        f'<div class="choice"><strong>{chr(65 + i)}.</strong> {c}</div>'
        for i, c in enumerate(choices)
    )

    return f"""
    <style>
        .question-card {{
            background:white; border-radius:12px; padding:24px;
            margin-bottom:16px;
            box-shadow:0 1px 3px rgba(0,0,0,0.08);
            font-family:system-ui,sans-serif;
            border:1px solid #e2e8f0;
        }}
        .question-card .meta {{
            display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;
        }}
        .question-card .tag {{
            background:#e2e8f0; padding:3px 10px; border-radius:12px;
            font-size:12px; font-weight:500; color:#475569;
        }}
        .question-card h3 {{
            font-size:16px; margin:0 0 8px 0; color:#1e293b;
        }}
        .question-card .question {{
            font-size:15px; margin-bottom:16px; line-height:1.5;
        }}
        .question-card .choices {{ margin-bottom:16px; }}
        .question-card .choice {{ padding:6px 0; font-size:14px; }}
        .question-card .answer {{
            background:#f0fdf4; border:1px solid #bbf7d0;
            border-radius:8px; padding:10px 16px; margin-bottom:16px;
            color:#166534; font-weight:500;
        }}
        .question-card .model-results table {{
            width:100%; border-collapse:collapse;
        }}
        .question-card .model-results th {{
            background:#f8fafc; padding:8px 12px; text-align:left;
            font-size:12px; color:#64748b; font-weight:600;
            text-transform:uppercase;
        }}
        .question-card .model-results td {{
            border-top:1px solid #f1f5f9;
        }}
    </style>
    <div class="question-card">
        <div class="meta">
            <span class="tag">#{qid}</span>
            <span class="tag">{category.replace("_", " ").title()}</span>
            <span class="tag">{subject.title()}</span>
            <span class="tag">{level.title()}</span>
        </div>
        {image_html}
        <h3>Question</h3>
        <div class="question">{question}</div>
        <h3>Choices</h3>
        <div class="choices">{choice_html}</div>
        <div class="answer">
            Correct Answer: <strong>{answer}. {answer_text}</strong>
        </div>
        <div class="model-results">
            <h4>Model Results ({model_summary})</h4>
            <table>
                <thead><tr><th></th><th>Model</th><th>Answer</th></tr></thead>
                <tbody>{"".join(model_rows)}</tbody>
            </table>
        </div>
    </div>
    """


def create_demo(results_path: Path | str | None = None) -> gr.Blocks:
    """Create the Gradio demo interface."""
    samples, summaries = load_results(results_path)
    data_dir = get_data_dir()

    css = """
    #app-title { text-align: center; margin-bottom: 8px; }
    #app-subtitle { text-align: center; color: #64748b; margin-bottom: 24px; }
    .gradio-container { max-width: 1100px !important; margin: 0 auto; }
    footer { visibility: hidden; }
    """

    categories = ["All", *sorted({s.get("category", "") for s in samples})]
    subjects = ["All", *sorted({s.get("subject", "") for s in samples})]
    levels = [
        "All",
        *sorted({s.get("experience_level", "") for s in samples}),
    ]

    with gr.Blocks(
        css=css,
        title="BJJ-VQA Benchmark Demo",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# 🥋 BJJ-VQA Benchmark Demo",
            elem_id="app-title",
        )
        gr.Markdown(
            "Visual Question Answering benchmark for Brazilian Jiu-Jitsu. "
            "See how different vision-language models perform "
            "on BJJ reasoning tasks.",
            elem_id="app-subtitle",
        )

        with gr.Tabs():
            # ── Leaderboard Tab ──
            with gr.TabItem("📊 Leaderboard"):
                gr.HTML(
                    value=_build_leaderboard(summaries),
                    label="Model Comparison",
                )
                if results_path is None:
                    gr.Markdown(
                        "⚠️ _Showing placeholder results. "
                        "Run real evaluations to replace these._",
                    )
                else:
                    gr.Markdown(
                        "_Results loaded from eval log._",
                    )

            # ── Question Browser Tab ──
            with gr.TabItem("🔍 Browse Questions"):
                with gr.Row():
                    category_filter = gr.Dropdown(
                        choices=categories,
                        value="All",
                        label="Category",
                        scale=1,
                    )
                    subject_filter = gr.Dropdown(
                        choices=subjects,
                        value="All",
                        label="Subject",
                        scale=1,
                    )
                    level_filter = gr.Dropdown(
                        choices=levels,
                        value="All",
                        label="Level",
                        scale=1,
                    )
                    search_box = gr.Textbox(
                        label="Search",
                        placeholder="Search questions...",
                        scale=2,
                    )

                question_list = gr.HTML(
                    value="".join(
                        _build_question_card(s, summaries, data_dir) for s in samples
                    ),
                )

                def _filter_questions(
                    category: str,
                    subject: str,
                    level: str,
                    query: str,
                ) -> str:
                    """Filter and rebuild question cards."""
                    filtered = samples
                    if category != "All":
                        filtered = [
                            s for s in filtered if s.get("category") == category
                        ]
                    if subject != "All":
                        filtered = [s for s in filtered if s.get("subject") == subject]
                    if level != "All":
                        filtered = [
                            s for s in filtered if s.get("experience_level") == level
                        ]
                    if query.strip():
                        ql = query.lower()
                        filtered = [
                            s
                            for s in filtered
                            if ql in s.get("question", "").lower()
                            or ql in s.get("id", "")
                        ]
                    return "".join(
                        _build_question_card(s, summaries, data_dir) for s in filtered
                    )

                inputs = [
                    category_filter,
                    subject_filter,
                    level_filter,
                    search_box,
                ]
                category_filter.change(
                    _filter_questions,
                    inputs=inputs,
                    outputs=question_list,
                )
                subject_filter.change(
                    _filter_questions,
                    inputs=inputs,
                    outputs=question_list,
                )
                level_filter.change(
                    _filter_questions,
                    inputs=inputs,
                    outputs=question_list,
                )
                search_box.change(
                    _filter_questions,
                    inputs=inputs,
                    outputs=question_list,
                )

            # ── About Tab ──
            with gr.TabItem("ℹ️ About"):
                gr.Markdown(
                    f"""### BJJ-VQA: Brazilian Jiu-Jitsu Visual Q&A Benchmark

This demo shows how vision-language models perform on BJJ-VQA,
a multiple-choice visual question answering benchmark
for Brazilian Jiu-Jitsu.

#### What's tested
- **{len(samples)} questions** across **6 subjects**
  (guard, passing, submissions, controls, escapes, takedowns)
- **2 categories** (gi, no-gi)
- **3 experience levels** (beginner, intermediate, advanced)
- Each question pairs a real BJJ instructional frame with
  a domain-specific question

#### Why it matters
Models that can answer from text alone,
or that merely describe what they see, will not score well.
BJJ-VQA measures true visual reasoning in a specialized domain.

#### Data
- Dataset:
  [couto/bjj-vqa](https://huggingface.co/datasets/couto/bjj-vqa)
- Code:
  [matheusccouto/bjj-vqa](https://github.com/matheusccouto/bjj-vqa)
""",
                )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BJJ-VQA Evaluation Demo",
    )
    parser.add_argument(
        "--results",
        type=Path,
        help="Path to eval results JSON file",
        default=None,
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to listen on",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public share link",
    )
    args = parser.parse_args()

    demo = create_demo(args.results)
    demo.launch(server_port=args.port, share=args.share)
