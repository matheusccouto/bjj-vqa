# PRD: BJJ-VQA v0.1

## Problem Statement

BJJ-VQA currently has 57 unreviewed test questions with known quality issues (stem leak, shallow reasoning, uniform patterns, wrong answers). The question generation process is ad-hoc — there is no automated pipeline to produce benchmark-quality questions. The existing issues were created without careful planning, and the dependency graph is messy. The benchmark needs a complete replanning from scratch to reach a v0.1 release with validated questions, evaluation results, a public demo, and HuggingFace discoverability.

## Solution

Rebuild BJJ-VQA from scratch with an adversarial, automated question generation pipeline that produces ~80-100 validated questions via an orchestrated loop: Gemini 3 Flash processes full YouTube URLs in a single pass to generate questions, a different LLM reviews them against defined evals via inspect-ai's LLM-as-judge, and the loop continues until each question meets the quality threshold. All wrapped in an OpenCode skill triggered via GitHub Actions. The demo app, eval harness, and HF listing proceed in parallel tracks. The existing 57 questions are wiped — v0.1 starts from a clean slate with only validated questions.

## User Stories

1. As a benchmark maintainer, I want to pass a YouTube URL to a pipeline and receive validated VQA questions, so that I can scale question production without manual effort
2. As a benchmark maintainer, I want the pipeline to open a PR with new questions and their image frames, so that I can review and merge with a single click
3. As a benchmark maintainer, I want each generated question to be scored against defined evals by an adversarial reviewer LLM, so that quality is enforced before any question reaches the dataset
4. As a benchmark maintainer, I want to trigger question generation both manually via workflow_dispatch and by labeling an issue, so that I can choose the most convenient workflow
5. As a researcher, I want to discover BJJ-VQA in the HuggingFace Community Evals directory, so that I can run the benchmark on my own models
6. As a BJJ creator, I want to see a visual demo of VLMs failing at BJJ reasoning questions, so that I understand why this benchmark matters and grant permission for my content
7. As a researcher, I want to compare multiple models on a leaderboard with accuracy per category and subject, so that I can understand model strengths and weaknesses
8. As a user, I want to browse individual questions with their images, choices, and which models got them right/wrong, so that I can analyze failure modes
9. As a BJJ practitioner, I want to take the test myself and compare my answers against model performance, so that I can engage with the benchmark interactively
10. As a benchmark maintainer, I want the pipeline to warn me if new questions would unbalance the dataset (any bucket >40%), so that I can maintain statistical validity
11. As a benchmark maintainer, I want the pipeline to retry transient failures (rate limits, timeouts) before flagging for human review, so that I maximize automation
12. As a developer, I want to run `bjj-vqa generate <url>` to produce candidate questions with frames in a single command, so that I can test the pipeline locally
13. As a benchmark maintainer, I want all generated questions to include both COMPLETION and CLASSIFICATION stem types, so that the dataset has format diversity
14. As a benchmark maintainer, I want the pipeline to respect the methodology in docs/methodology.md, so that every question satisfies the core validity criterion (both image and BJJ knowledge required)
15. As a researcher, I want to run the benchmark against multiple models manually using the existing inspect-ai pipeline, so that I can establish baseline results
16. As a benchmark maintainer, I want the project's scripts directory to be pruned and relevant functionality consolidated into the `bjj-vqa` CLI, so that the codebase stays clean and discoverable

## Implementation Decisions

### Architecture
- **Single repository**: the private repo's pipeline code is merged into `bjj-vqa` at `src/bjj_vqa/generate/`, but barely reused — the existing private repo code is of low quality and will be largely rewritten
- **Three parallel development tracks**: (A) question pipeline, (B) Gradio demo app, (C) HF Community Evals listing (already submitted via PR #5)
- **Incremental delivery**: each slice ships working, testable code before the next starts. TDD enforced on all slices. No waterfall.
- **Vertical slices**: each issue is a thin end-to-end slice that an agent can pick up independently with no shared context between sessions

### Question Generation Pipeline
- **Gemini 3 Flash** (via Google AI Studio) as the question generator, processing full YouTube URLs directly in a single pass — no intermediate extraction step
- **Sequential processing** within a video (full context is required for each question, wall-clock time does not matter for background runs)
- **Full YouTube URL per API call** (not segment-only), because technique understanding requires the full setup/execution context
- **Frame extraction** via `yt-dlp` + `ffmpeg` at Gemini-suggested timestamps, automated and included in the same PR as the questions
- **Adversarial review loop**: a different model reviews generated questions against the defined evals via a custom inspect-ai scorer
- **Review scoring**: inspect-ai custom scorer using `get_model()` for structured LLM-as-judge evaluation. If quality proves poor, pivot to deepeval `GEval`
- **Quality threshold and max retry attempts**: defined during implementation, not pre-specified
- **Mock-first approach**: the generate CLI starts with a mock Gemini that returns data from existing `samples.json` as a fixture, making the first slice fully testable without API keys
- **OpenCode skill** is a `SKILL.md` markdown file written alongside the CLI it wraps — not a separate PR. Skills are reusable instruction bundles, not code deliverables.

### Orchestrator
- **OpenCode** as the orchestrator, with a custom skill wrapping the Python pipeline CLI
- **GitHub Actions** triggered by both `workflow_dispatch` (manual) and issue labeling
- **PR-based output**: pipeline opens a PR to `data/samples.json` + `data/images/` in the same commit
- **No MCP** — CLI + Skill approach is cheaper on tokens, more debuggable, and sufficient for a single-user workflow

### Evaluation
- **Multi-model evaluation**: manual process using existing `inspect eval` pipeline. No new CLI needed. Run against each model, store results in `logs/` as JSON for the demo app to consume
- **No-image ablation**: skipped for v0.1. Will be revisited after question quality is validated
- **Eval models for v0.1**: Gemma 4 31B (free on OpenRouter) as open-weight baseline, Gemini 3 Flash (cheap via OpenRouter) as proprietary baseline. Frontier models (Opus 4.7, Gemini 3 Pro) deferred until question quality validated

### Demo App
- **Gradio** on HuggingFace Spaces (free hosting, native HF ecosystem)
- **Scrap existing PR #25** and rebuild from scratch using vertical slices
- **3 tabs, built incrementally**:
  1. Leaderboard — accuracy per model, per category, per subject
  2. Question browser — image, choices, correct answer, model right/wrong
  3. Take the Test — interactive user participation
- **Mock data for immediate demo** — leaderboard tab ships with placeholder data so the app is demonstrable before eval results exist

### Dataset
- **Target**: ~80-100 validated questions for v0.1
- **Wipe existing 57 questions**: they are test data with known quality issues, not benchmark data
- **Balance enforcement**: soft warning in PR description if any bucket exceeds 40%, not a hard gate
- **Schema**: existing `SampleRecord` in `src/bjj_vqa/schema.py` — backward-compatible only
- **Frame storage**: JPEGs committed to `data/images/` (repo is small enough)

### Technical Decisions
- **inspect-ai** for LLM-as-judge (no new dependency, already in pyproject.toml)
- **Pydantic** for structured output enforcement from Gemini API
- **yt-dlp** (Unlicense license, GPL-compatible) + **ffmpeg** for frame extraction
- **OpenRouter** as the primary inference provider (can use Google AI Studio key via OpenRouter)
- **CLI approach over MCP**: 4-32x fewer tokens per call, debuggable with stdout/stderr, LLM already knows Unix composability patterns
- **Existing `ty check` CI failure**: ignored for now — new slices focus on functionality, type errors fixed when code is touched

### Legacy Cleanup
- **Scripts directory**: audit aggressively. Delete unused scripts. Fold useful logic into `bjj-vqa` CLI subcommands
- **No-image ablation script**: can be deleted (skipped for v0.1)
- **Submit HF script**: check if subsumed by existing `bjj-vqa publish` command

### HuggingFace Community Evals
- PR #5 already open at `huggingface/community-evals` (3 additions, awaiting review)
- `eval.yaml` already valid and conformant
- No internal work needed — tracked externally

### Release
- **Manual checklist**: tag, HF publish, README update, CI green, TODO.md update — no automation needed for v0.1

## Testing Decisions

- **TDD enforced on all slices**: write failing tests first, implement until green, then refactor
- **Tests in `tests/` directory**, following existing conventions in `tests/test_schema.py`, `tests/test_cli.py`, `tests/test_task.py`
- **Mock-first for pipeline**: the generate CLI uses a mock Gemini returning fixture data from existing `samples.json` — fully testable without API keys
- **Review scorer tested with mocked LLM responses**: verify score extraction, threshold gate logic, and retry behavior in isolation
- **`@pytest.mark.vision` for tests requiring live model API keys**
- **No API calls in unmarked tests** (CI has no keys)
- **Existing test suite must pass**: `uv run pytest -x`
- **CLI tests for new subcommands** (`generate`, `review`)
- **Demo app tested with mock data**: verify table rendering, filter logic, and scoring logic without real eval results
- **Schema validation tests updated** for any backward-compatible changes

## Out of Scope

- Video temporal reasoning (questions remain single-frame only)
- Multilingual support (English only for v0.1)
- Multi-image questions (schema supports it, but pipeline produces single-image)
- Automated dataset balancing enforcement (soft warning only, not a hard gate)
- Frontier model evaluation (deferred until question quality validated)
- Source video downloading for the pipeline (Gemini processes YouTube URLs directly)
- Confident AI / deepeval platform integration (may be added later if pivot needed)
- No-image ablation (skipped for v0.1)
- Multi-model evaluation automation (manual process using existing pipeline)
- Release automation (manual checklist)
- Fixing pre-existing `ty check` CI failure on main (deferred)

## Further Notes

- The PR for HF Community Evals listing is already open (huggingface/community-evals#5)
- The adversarial loop is implemented as a full harness from day one (MVP approach), with OpenCode skill and GitHub Action wrapping incrementally
- The review model must be different from the generator to avoid shared blind spots
- All pipeline output follows the existing `SampleRecord` schema — `uv run bjj-vqa validate` must pass on any pipeline output
- Dataset limitations documented in README: source diversity (currently all Cobrinha), category imbalance, small sample sizes for some subjects
- Each slice is independently grabbable by an AI agent with no shared context between sessions — the issue body must contain all necessary context, API contracts, and test baselines
- Skills are `SKILL.md` files (reusable instruction bundles), not code deliverables — they ship alongside the CLI they wrap, not as separate PRs
