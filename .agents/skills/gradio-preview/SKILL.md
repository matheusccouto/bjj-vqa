---
name: gradio-preview
description: Visually test the Gradio leaderboard app using Playwright headless screenshots. Use when developing the Gradio app, verifying the UI renders correctly, or checking that eval data displays properly.
---

# Gradio Preview

Launch the BJJ-VQA Gradio app in headless mode, take a screenshot, and analyze it visually.

## Prerequisites

```bash
uv sync --dev --extra spaces
uv run playwright install --with-deps chromium  # first time only
```

## Workflow

### 1. Take a screenshot

```bash
uv run --env-file .env .agents/skills/gradio-preview/scripts/screenshot_gradio.py screenshot.png
```

### 2. Analyze the screenshot

Examine `screenshot.png` directly. Check:

- Title and header visible
- Data table populated with model names and accuracy values
- No error messages or blank content
- Correct sort order (highest accuracy at top)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `OSError: Cannot find empty port` | Run `fuser -k 7860/tcp` then retry |
| Empty leaderboard shown | Make sure `--env-file .env` is used (sets `BJJ_VQA_LOGS_DIR`) |
| Playwright browser error | Run `uv run playwright install --with-deps chromium` |
