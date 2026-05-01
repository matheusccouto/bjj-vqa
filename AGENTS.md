BJJ Visual Question Answering benchmark. HuggingFace datasets, inspect-ai eval harness, DeepEval question quality evals.

## Stack
Python 3.13+, uv, HuggingFace datasets, inspect-ai, DeepEval, yt-dlp, ffmpeg, Gradio.
Tests: `uv run pytest -x`. Lint: `uv run ruff check .`. Format: `uv run ruff format --check .`. Type: `uv run ty check src`.
Validate: `uv run bjj-vqa validate`.

## Hard rules
1. Never modify gold answers without documenting in `CONTEXT.md`.
2. Schema changes must be backward-compatible. New required fields need migration of all existing records.
3. Never delete a failing test.
4. `uv run bjj-vqa validate` must pass on every commit that touches `data/`.

<important if="you are adding or modifying a question">
Read `CONTEXT.md`. Update `sources/registry.jsonl`. Run `uv run bjj-vqa validate`.
</important>

<important if="you are modifying the schema">
Backward-compatible only. New required fields need migration of all existing records. Update `tests/test_schema.py`. Add an ADR in `docs/adr/`.
</important>

<important if="you are writing tests">
Tests in `tests/`. API-key tests marked `@pytest.mark.vision`. No API calls in unmarked tests (CI has no keys). Use TDD: write failing tests first.
</important>

<important if="you are touching HuggingFace integration">
`eval.yaml` must stay valid. README frontmatter must stay conformant. Do not modify without checking HF Community Evals spec.
</important>

## Agent skills

### Issue tracker
GitHub Issues on matheusccouto/bjj-vqa (via `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels
Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs
Single-context layout. `CONTEXT.md` at root, ADRs in `docs/adr/`. See `docs/agents/domain.md`.

## References
- uv: https://docs.astral.sh/uv/llms.txt
- ruff: https://docs.astral.sh/ruff/llms.txt
- ty: https://docs.astral.sh/ty/llms.txt
- Pydantic: https://docs.pydantic.dev/latest/llms.txt
- inspect-ai: https://inspect.aisi.org.uk/llms.txt
- DeepEval: https://docs.confident-ai.com/llms.txt
- HuggingFace: https://huggingface.co/docs/hub/llms.txt
