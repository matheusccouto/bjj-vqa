---
sdk: gradio
sdk_version: 5.29.0
app_file: eval_demo.py
python_version: "3.13"
---

# BJJ-VQA Evaluation Demo

Interactive Gradio app showing how VLMs perform on the BJJ-VQA benchmark.

## Features

- **Leaderboard**: Overall, per-category, per-experience-level, and per-subject accuracy
- **Question Browser**: Every question with its image, choices, correct answer, and per-model results

## Quick Start

```bash
cd app/
pip install -r requirements.txt
python eval_demo.py
```

## Adding Evaluation Results

Create `app/eval_results.json` with the following schema:

```json
[
  {
    "model": "gpt-4o",
    "results": {
      "overall": {"accuracy": 0.72, "total": 57, "correct": 41},
      "by_category": {
        "gi": {"accuracy": 0.75, "total": 40, "correct": 30},
        "no_gi": {"accuracy": 0.65, "total": 17, "correct": 11}
      },
      "by_experience_level": {
        "beginner": {"accuracy": 0.80, "total": 20, "correct": 16},
        "intermediate": {"accuracy": 0.70, "total": 20, "correct": 14},
        "advanced": {"accuracy": 0.59, "total": 17, "correct": 10}
      },
      "by_subject": {
        "guard": {"accuracy": 0.70, "total": 10, "correct": 7},
        "passing": {"accuracy": 0.75, "total": 8, "correct": 6}
      },
      "per_question": {
        "00001": "B",
        "00002": "C"
      }
    }
  }
]
```

Only `model`, `results.overall`, and `results.per_question` are required. Breakdowns are optional.

## Deploy to HuggingFace Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces) (choose **Gradio** SDK)
2. Copy the `app/` directory contents into the Space repo root
3. Push — the Space auto-installs from `requirements.txt` and launches `eval_demo.py`

```bash
# From inside app/
cp -r . /path/to/space-repo/
cd /path/to/space-repo/
git add . && git commit -m "deploy" && git push
```

For persistent results across deployments, upload `eval_results.json` as a
[HuggingFace Dataset](https://huggingface.co/docs/datasets) and load it via
`load_dataset()` instead of a local file.