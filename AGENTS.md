BJJ Visual Question Answering benchmark. HuggingFace datasets, inspect-ai eval harness, methodology checklist.

## Stack
Python 3.13+, uv, HuggingFace datasets, inspect-ai, OpenCV, Pillow.
Tests: `uv run pytest -x`. Lint: `uv run ruff check .`. Format: `uv run ruff format --check .`. Type: `uv run ty check src`.
Validate: `uv run bjj-vqa validate`.

## Hard rules
1. Never modify gold answers without documenting in `docs/methodology.md`.
2. Never commit `data/` contents -- use DVC.
3. Every new task family gets a methodology checklist entry FIRST.
4. Schema changes must be backward-compatible.
5. Never delete a failing test.

<important if="you are adding or modifying a question">
Read `docs/methodology.md`. Update `sources/registry.jsonl`. Run `uv run bjj-vqa validate`.
</important>

<important if="you are modifying the schema">
Backward-compatible only. New required fields need migration of all existing records. Update `tests/test_schema.py`. ADR in `docs/decisions/`.
</important>

<important if="you are writing tests">
Tests in `tests/`. API-key tests marked `@pytest.mark.vision`. No API calls in unmarked tests (CI has no keys).
</important>

<important if="you are touching HuggingFace integration">
`eval.yaml` must stay valid. README frontmatter must stay conformant. Do not modify without checking HF Community Evals spec.
</important>

## References
- uv: https://docs.astral.sh/uv/llms.txt
- ruff: https://docs.astral.sh/ruff/llms.txt
- ty: https://docs.astral.sh/ty/llms.txt
- Pydantic: https://docs.pydantic.dev/latest/llms.txt
- inspect-ai: https://inspect.aisi.org.uk/llms.txt
- HuggingFace: https://huggingface.co/docs/hub/llms.txt