# PRD: BJJ-VQA v0.1

## Problem Statement

BJJ-VQA has 57 unreviewed questions with known quality issues: stem leak, shallow reasoning, and wrong answers. Question production is fully manual with no quality enforcement. The benchmark cannot be taken seriously until it has a repeatable, validated pipeline and a public-facing result.

## Solution

Rebuild BJJ-VQA from scratch with two parallel approaches to automated question generation, a DeepEval-powered quality gate, a Gradio leaderboard, and HuggingFace discoverability. The existing 57 questions are wiped. v0.1 ships only validated questions.

**Track A — Simple pipeline:** trigger with a YouTube URL via `workflow_dispatch`. Gemini Flash generates structured questions and suggests timestamps. Frames are extracted and everything is committed directly to `data/`. A PR is opened. CI runs quality evals. Human reviews and merges.

**Track B — Agentic loop:** an OpenCode agent (Qwen 3.6 Plus or any vision-capable model) orchestrates Gemini iteratively — calling `bjj-vqa generate`, running `bjj-vqa evals`, re-prompting with `--instructions` and `--previous` until questions pass or the retry limit is reached, then calling `bjj-vqa add` and opening a PR.

Both tracks run in parallel. The maintainer reviews results and promotes whichever produces better questions.

## User Stories

1. As a benchmark maintainer, I want to trigger question generation with a YouTube URL, so that I can produce candidate questions without manual effort
2. As a benchmark maintainer, I want Gemini to decide how many questions a video contains (3-8 range), so that I get as many good concepts as the video supports and no padded filler
3. As a benchmark maintainer, I want Gemini to suggest frame timestamps alongside each question, so that frame extraction is fully automated
4. As a benchmark maintainer, I want generated questions to arrive as a PR against data/, so that I can review and merge with a single click
5. As a benchmark maintainer, I want the PR to include an eval report showing which questions passed and which failed, so that I can make an informed merge decision
6. As a benchmark maintainer, I want CI to block a PR on data/samples.json if any question fails the quality evals, so that bad questions cannot be merged silently
7. As a benchmark maintainer, I want to override a failing CI eval gate on GitHub, so that I can accept a question I disagree with on valid grounds
8. As a benchmark maintainer, I want to re-trigger generation for a URL with free-form instructions, so that I can guide Gemini toward better questions on a retry (Track B)
9. As a benchmark maintainer, I want the agentic loop to pass previous output alongside new instructions to Gemini, so that Gemini revises rather than regenerates from scratch (Track B)
10. As a benchmark maintainer, I want the agentic loop to stop after a fixed number of retries and flag unresolved failures in the PR, so that the pipeline does not run indefinitely
11. As a benchmark maintainer, I want to run `bjj-vqa evals` on a question locally, so that I can check quality before opening a PR
12. As a benchmark maintainer, I want quality evals to use a cheap model (Gemma 4 31B, free on OpenRouter), so that the pipeline has no meaningful cost
13. As a benchmark maintainer, I want to run `bjj-vqa add` to commit a reviewed tmp directory to the dataset, so that the merge step is always explicit and agent-controlled
14. As a benchmark maintainer, I want `bjj-vqa validate` to pass on every commit to main, so that data/ is always in a consistent state
15. As a benchmark maintainer, I want the scripts/ directory removed and any useful functionality folded into the bjj-vqa CLI, so that the codebase has a single discoverable entry point
16. As a benchmark maintainer, I want CONTEXT.md at the repo root summarising the domain model and architecture, so that AI agents and new contributors have a reliable starting point
17. As a researcher, I want to discover BJJ-VQA in the HuggingFace Community Evals directory, so that I can run the benchmark on my own models
18. As a researcher, I want to compare model accuracy on a leaderboard broken down by category and subject, so that I can understand where models succeed and fail
19. As a researcher, I want to run the inspect-ai eval pipeline manually against any model via OpenRouter, so that I can benchmark a model without writing code
20. As a benchmark maintainer, I want the PR to warn if any dataset bucket exceeds 40%, so that I can keep the benchmark statistically balanced

## Implementation Decisions

### Two parallel development tracks

Track A and Track B are developed concurrently as independent GitHub Issues. Agents are unaware of the competition. The maintainer reviews both PRs and decides which approach produces better questions. The losing track is closed without merge.

### Inference

All model calls use OpenRouter. OpenRouter supports YouTube URL passthrough for Gemini models natively, so no Google AI Studio SDK is required. The single credential is `OPENROUTER_API_KEY`.

- **Generator**: Gemini 3 Flash via OpenRouter — processes YouTube URLs directly, returns structured output
- **Eval reviewer**: Gemma 4 31B via OpenRouter — free, sufficient for quality judgement
- **Benchmark eval models**: Gemma 4 31B (open-weight baseline), Gemini 3 Flash (proprietary baseline)

### Generation pipeline

Gemini 3 Flash receives a YouTube URL and a base system prompt (stored in the generate module alongside the Python code). It returns a JSON array matching the existing `SampleRecord` schema — structured output enforced by Pydantic. Gemini decides how many questions the video supports (3-8 guidance, not a hard limit). Each question includes a suggested timestamp.

Frames are extracted at Gemini's suggested timestamps using yt-dlp and ffmpeg. Output writes to a tmp directory mirroring the data/ layout — `questions.json` + `images/`. Nothing touches `data/` until `bjj-vqa add` is called explicitly.

**CLI:**
- `bjj-vqa generate <url>` — generates questions + extracts frames to tmp dir, prints tmp path
- `bjj-vqa generate <url> --instructions <str> --previous <path>` — Track B: injects previous output and agent guidance into the Gemini prompt
- `bjj-vqa add <tmpdir>` — assigns sequential IDs, moves images to data/images/, appends to data/samples.json, runs validate
- `bjj-vqa evals <tmpdir or question.json>` — runs DeepEval GEval against the criteria in evals/, returns structured pass/fail with reasoning

### Quality evals

`evals/` at the repo root contains DeepEval GEval test files — parallel to `tests/` for code. Each eval criterion from the methodology maps to a GEval metric. The same eval files are used in two contexts:

- **Generation loop**: `bjj-vqa evals` invokes DeepEval programmatically, returns structured JSON feedback the agent can use to guide re-prompting
- **CI quality gate**: `deepeval test run evals/` runs on every PR that touches data/samples.json

DeepEval is in its own `evals` dependency group — not a runtime dependency of the published package.

### Project structure

```
evals/            — DeepEval GEval criteria (parallel to tests/)
src/
  app/
    app.py        — Gradio leaderboard (HF Spaces entry point)
  bjj_vqa/
    cli.py        — all subcommands
    schema.py     — SampleRecord, Source (unchanged)
    task.py       — inspect-ai benchmark task (unchanged)
    generate/
      __init__.py
      prompt.md   — Gemini system prompt
CONTEXT.md        — domain model + architecture (replaces architecture.md + methodology.md)
docs/adr/         — decision records (kept, ADR-0005 and ADR-0006 updated)
```

`scripts/` is deleted entirely. `tools/` is deleted (empty). `prompts/` is deleted (prompt moves into generate/).

### Demo app

Gradio app on HuggingFace Spaces. v0.1 ships a single leaderboard tab reading from `data/samples.json` and `logs/`. No mock data — the existing questions serve as the fixture. No empty tabs. Question browser and "take the test" are post-v0.1.

HF Spaces `app_file` points to `src/app/app.py`.

### CI/CD

Three jobs:

1. **Fast** (every push): lint, type check, unit tests — no API calls
2. **Quality gate** (PRs touching data/samples.json): `deepeval test run evals/` against new/changed questions — blocks merge on failure, human can override on GitHub
3. **Release** (on tag): `bjj-vqa publish` to HuggingFace Hub

Track A also adds a **generation workflow** triggered by `workflow_dispatch` with a URL input.

### Track B — OpenCode skill

A `SKILL.md` file in `.agents/skills/generate/` instructs the OpenCode agent on the full iterative loop: call `bjj-vqa generate`, inspect output, call `bjj-vqa evals`, decide whether to re-call with `--instructions` and `--previous`, and finally call `bjj-vqa add` and open a PR.

### Documentation

`CONTEXT.md` at the repo root consolidates `architecture.md` and `methodology.md`. It is the single file agents read before working in this repo. ADRs remain in `docs/adr/` as permanent decision records. `docs/agents/domain.md` is simplified to ~8 lines pointing agents to `CONTEXT.md` and relevant ADRs.

### Dataset

- Existing 57 questions remain as v0.1 fixtures — they will be replaced during v1 mass production, not before
- Target: 80-100 validated questions for v1
- Soft balance warning in PR description if any bucket exceeds 40%
- Schema: existing `SampleRecord` — backward-compatible only
- Frames: JPEGs in data/images/, named with short UUID hex (e.g. `a3f7b9c1.jpg`) — no sequential IDs, no renaming needed when questions are removed

### Versioning

- **v0.1**: current 57 questions — development fixture set, used to validate pipeline and demo
- **v1**: mass-produced, fully validated questions generated by the new pipeline

## Testing Decisions

Good tests assert observable external behaviour — CLI exit codes, file system state, JSON output shape — not internal implementation. Tests never make real API calls unless marked `@pytest.mark.vision`.

- **`tests/`**: unit and integration tests for CLI subcommands, schema validation, and task loading. Follow conventions in existing `test_schema.py`, `test_cli.py`, `test_task.py`.
- **`evals/`**: DeepEval GEval tests for question quality. These are data tests, not code tests — they run against actual question records.
- **generate module**: tested with a mocked OpenRouter response returning fixture data from existing `samples.json`. No real API calls in unmarked tests.
- **`bjj-vqa add`**: tested by running against a known tmp fixture and asserting data/samples.json and data/images/ state.
- **`bjj-vqa evals`**: tested with a mocked DeepEval response to verify structured output format and exit code behaviour.
- **app**: tested with real data from samples.json — no mock data layer needed.
- All new subcommands follow the CLI test pattern in `test_cli.py`.

## Out of Scope

- Video temporal reasoning (single-frame only)
- Multilingual support (English only)
- Multi-image questions
- Hard dataset balance enforcement (soft warning only)
- Frontier model evaluation (deferred until question quality validated)
- No-image ablation (deferred to post-v0.1)
- Question browser and "take the test" demo tabs (post-v0.1)
- Release automation (manual checklist)
- Fixing pre-existing `ty check` CI failures on main

## Further Notes

- HF Community Evals PR is already open at huggingface/community-evals — no internal work needed
- Each GitHub Issue must be self-contained: the issue body is the agent's entire context. No cross-issue references for implementation details.
- Development runs on OpenClaw (Qwen 3.6 Plus): agents pick up `ready-for-agent` issues independently, open PRs, and do not share context between sessions
- `uv run bjj-vqa validate` must pass on every commit that touches data/
- ADR-0005 updated: OpenRouter scope extended from CI-only to all inference including generation
- ADR-0006 updated: references CONTEXT.md instead of the now-deleted methodology.md
