---
title: BJJ-VQA Evaluation Demo
emoji: 🥋
colorFrom: indigo
colorTo: gray
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
license: gpl-3.0
---

# BJJ-VQA Evaluation Demo

Interactive demo showing how Vision-Language Models perform on the
[BJJ-VQA benchmark](https://github.com/matheusccouto/bjj-vqa).

## Features

- **Leaderboard**: Compare model accuracy overall and broken down by
  category (gi/no-gi), subject, and experience level
- **Question Browser**: Explore individual questions with images,
  answer choices, and per-model correctness

## Data

Results shown are **placeholder/simulated** unless a real `results.json`
is provided. Real evaluation results will be substituted when models
are evaluated against the benchmark.
