# ADR-0008: DeepEval v4 quality eval framework

## Status

Accepted

## Context

BJJ-VQA questions need automated quality evaluation that sends the question image to the judge model. The initial PR used DeepEval v2.6 with a 160-line `MultimodalOpenRouterModel` that overrode four generate methods and manually assembled OpenAI-compatible content blocks from `[DEEPEVAL:IMAGE:...]` marker strings in `LLMTestCase` inputs.

DeepEval v4 (`>=4.0.3`) provides `MLLMImage` objects that embed directly into `LLMTestCase` f-strings, and `GEval` gains a `multimodal` flag that appends grounding rules to the evaluation prompt. The image slugs are still resolved inside the model wrapper, but the code is now much simpler.

The eval tests were also parametrized by criterion only, iterating questions inside each test. This made failures hard to locate in CI output.

## Decision

1. **Upgrade to `deepeval>=4.0.3`**.
2. **Use `GEval` + `LLMTestCase` + `MLLMImage`**: all 7 criteria send the image via `MLLMImage(url=..., local=True)` embedded in the test case input. No split between text-only and multimodal criteria.
3. **Thin `MultimodalOpenRouterModel`**: subclass overrides `supports_multimodal()`, `_generate_with_client()`, `generate_raw_response()`, and `a_generate_raw_response()`. A shared `_to_content_blocks()` helper converts `[DEEPEVAL:IMAGE:...]` slugs to OpenAI content blocks. ~70 lines vs the previous 160.
4. **Parametrize by criterion x question**: each test = 1 criterion x 1 question. Failures show `test_question_quality[STEM_LEAK-00001]` style names.
5. **`@pytest.mark.evals` marker**: registered in `pyproject.toml`. CI runs all questions. Local dev filters with `-k` or `-m evals`.
6. **Drop `EVAL_SAMPLE_SIZE` env var**: no sampling fixture. Full dataset in CI, `pytest -k` for local.
7. **No ruff per-file-ignores for `evals/`**: eval files follow the same rules as the rest of the codebase.
8. **Threshold**: 0.5 for all criteria. Will calibrate after first full run.

## Consequences

- **Positive**: Simpler model wrapper (~70 lines vs 160). Test names pinpoint exact criterion x question failures.
- **Positive**: All criteria receive the image, matching the image-dependent nature of BJJ-VQA questions.
- **Neutral**: Coupling to DeepEval v4 API. `MLLMImage` slug format may change across major versions.
- **Neutral**: 7 criteria x 57 questions = 399 test cases per run. Each costs an API call. CI runtime is O(minutes) but costs tokens.