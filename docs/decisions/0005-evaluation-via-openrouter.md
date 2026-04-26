# 0005: CI inference backend — OpenRouter

**Status**: Accepted

## Context

CI runs a one-question smoke eval on every push to main (`eval-test.yml`) and a full eval on workflow_dispatch (`eval-model.yml`). Both need to call a model API. The CI environment only supports a small number of secrets, so using one API key for all models is strongly preferred.

Alternatives: individual provider keys (Anthropic, Google, OpenAI, etc.), a self-hosted model.

## Decision

Use OpenRouter as the primary inference backend for CI. Reasons:

- Single `OPENROUTER_API_KEY` secret covers hundreds of models from all major providers
- Compatible with inspect-ai's OpenAI-compatible provider interface
- Model IDs are namespaced (`openrouter/<provider>/<model>`), making it easy to swap models in the eval command
- The smoke eval uses `openrouter/google/gemma-4-31b-it` as a lightweight, low-cost default

## Consequences

- CI requires one secret: `OPENROUTER_API_KEY`
- Researchers who want to run evals against models not on OpenRouter can use their provider's API key directly with the appropriate inspect-ai provider
