---
title: BJJ-VQA
emoji: 🥋
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.0.0
app_file: eval_demo.py
pinned: false
license: cc-by-sa-4.0
---

# BJJ-VQA: Can AI Understand Jiu-Jitsu?

A benchmark that tests whether Vision-Language Models can reason about Brazilian Jiu-Jitsu mechanics — not just recognize technique names.

**What you'll find here:**
- 🏆 **Leaderboard** — compare models on overall accuracy and per-category breakdowns
- 🔍 **Question Browser** — browse every question in the benchmark, see the image, choices, correct answer, and which models got it right

**How to deploy your own:**
1. Fork [matheusccouto/bjj-vqa](https://github.com/matheusccouto/bjj-vqa)
2. Create a new Space on Hugging Face, select Gradio SDK
3. Upload `app/eval_demo.py`, `app/requirements.txt`, `data/`, and `eval_results/`
4. Replace `eval_results/placeholder_results.json` with real evaluation results

Built with [Gradio](https://gradio.app) and deployed on [Hugging Face Spaces](https://huggingface.co/spaces).
