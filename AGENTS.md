# BJJ-VQA — Agent Context

BJJ-VQA is a Visual Question Answering benchmark for Brazilian Jiu-Jitsu, intended for Hugging Face Community Evals via inspect-ai. Questions are multiple-choice, each paired with a still frame from a CC-licensed instructional video. The dataset author is a BJJ practitioner; questions are constructed using a hybrid AI-assisted methodology documented in `docs/methodology.md`. The benchmark evaluates whether vision-language models can reason about BJJ mechanics, not just recognize technique names.

## Project map

```
src/bjj_vqa/
  schema.py       — Pydantic models: SampleRecord, Source, and type aliases
  task.py         — inspect-ai task definitions (bjj_vqa, bjj_vqa_no_images)
  cli.py          — CLI entry point: validate, validate-sources, rubric, publish
  rubric.py       — Seven-criterion adversarial rubric (Anthropic API)

tests/
  test_schema.py  — Schema validation unit tests
  test_task.py    — inspect-ai task construction tests
  test_cli.py     — CLI integration tests
  test_rubric.py  — Rubric tests (T7 deterministic, T1-T6 mocked)
  test_vision_pipeline.py — Vision pipeline smoke tests (marked "vision")

data/
  samples.json    — 57 VQA questions (source of truth)
  images/         — JPEG frames committed to git (5-digit IDs)

sources/
  registry.jsonl  — Machine-readable source registry (one JSON object per line)

docs/
  methodology.md  — Canonical question construction methodology
  architecture.md — Eval flow, HF integration, data structure
  glossary.md     — VQA and BJJ terminology
  decisions/      — Architecture Decision Records (ADRs)
  research/       — Investigation notes (YYYY-MM-DD_<topic>.md)
  rubric-report.md — Generated artifact (gitignored); run `bjj-vqa rubric --all`

prompts/
  generate.md     — Canonical question generation prompt (used with Gemini)
  rubric/         — Per-criterion LLM prompts for the adversarial rubric

scripts/
  no_image_report.py  — Aggregate no-images eval log into stem-leak report
  extract_metrics.py  — Extract accuracy metrics from eval log
  submit_hf.py        — Submit eval results to HuggingFace
  verify_vision.py    — Verify vision pipeline end-to-end

.github/
  workflows/      — CI: validate.yml, eval-test.yml, eval-model.yml, publish.yml
  ISSUE_TEMPLATE/ — Bug, feature, and question-addition templates
  pull_request_template.md
  CODEOWNERS

eval.yaml         — HuggingFace Community Evals configuration (do not modify)
ATTRIBUTIONS.md   — Human-readable attribution table (TASL framework)
```

## Commands

```bash
uv sync                          # install all dependencies
uv run pytest -v                 # run all tests (except vision-marked)
uv run pytest -v -m vision       # run vision pipeline tests (needs API key)
uv run ruff check .              # lint
uv run ruff format --check .     # check formatting
uv run ty check                  # static type check
uv run bjj-vqa validate          # validate samples.json schema + image paths + sources
uv run bjj-vqa validate-sources  # validate sources/registry.jsonl cross-references
uv run bjj-vqa rubric <id>       # run seven-criterion rubric on one question
uv run bjj-vqa rubric --all      # run rubric on all questions → docs/rubric-report.md
uv run inspect eval src/bjj_vqa/task.py --model <model_id>  # run full eval
uv run inspect eval src/bjj_vqa/task.py@bjj_vqa_no_images --model <model_id>
```

## Workflow

Non-trivial work follows this pattern:

1. Read the relevant files (issue, methodology, existing code)
2. Produce a written plan in chat with: files to create, files to modify, ambiguities, estimated size
3. Wait for user approval before creating a branch or changing any file
4. Implement on a feature branch; open a PR using the template
5. Ensure all CI checks pass: ruff, ty, pytest, bjj-vqa validate

Use plan mode in Claude Code for any task that touches multiple files or is tied to a GitHub issue.

---

<important if="you are adding or modifying a question">
Frames must come from CC-licensed sources or sources with explicit creator permission.
Update `sources/registry.jsonl` with the source's licensing before adding questions.
Run `uv run bjj-vqa validate` to check schema and image paths.
Run `uv run bjj-vqa rubric <id>` and confirm all seven criteria pass before submitting.
Read `docs/methodology.md` to understand what makes a question valid.
</important>

<important if="you are modifying the schema (src/bjj_vqa/schema.py)">
Schema changes require backward-compatible defaults so existing 57 questions remain valid.
Update `tests/test_schema.py` to cover new fields.
If adding a new required field, migrate all existing records in `data/samples.json` first.
Document the decision in a new ADR under `docs/decisions/`.
</important>

<important if="you are introducing a new dependency">
Add it to `pyproject.toml` under the appropriate group (main or dev/test).
Record the rationale in a new ADR under `docs/decisions/`.
Run `uv sync --locked` after adding; update `uv.lock` by running `uv sync`.
</important>

<important if="you are writing or modifying tests">
Unit tests live in `tests/`. Tests requiring live API keys must be marked `@pytest.mark.vision`.
The `eval-test.yml` CI workflow runs a one-question smoke eval on every push to main.
Do not add API calls to unmarked tests — CI has no ANTHROPIC_API_KEY by default.
Mock Anthropic responses using `pytest-mock` (already in dev deps).
</important>

<important if="you are touching anything that affects HuggingFace Community Evals integration">
`eval.yaml` at the repo root must remain valid — do not modify it without checking the HF Community Evals spec.
The dataset card frontmatter in `README.md` must remain conformant with HF dataset card format.
Eval results belong in `.eval_results/` inside the model's own HF repo, not this dataset repo.
Verify with the HF docs links in the References section below.
</important>

<important if="you are implementing a GitHub issue">
Read the issue body and locate the files declared in scope.
Only touch files within that declared scope.
If a necessary change is outside scope, stop and ask the user before expanding.
Cross-check your file list before opening a PR.
</important>

## References

- uv: https://docs.astral.sh/uv/llms.txt
- ruff: https://docs.astral.sh/ruff/llms.txt
- ty: https://docs.astral.sh/ty/llms.txt
- Pydantic: https://docs.pydantic.dev/latest/llms.txt
- inspect-ai: https://inspect.aisi.org.uk/
- HuggingFace Community Evals: https://huggingface.co/blog/community-evals
- HuggingFace eval-results spec: https://huggingface.co/docs/hub/eval-results
- HuggingFace Hub docs: https://huggingface.co/docs/hub/llms.txt
