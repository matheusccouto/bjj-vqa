# 0005: OpenRouter as primary inference provider

**Status**: Accepted

## Context

All model calls in this project — benchmark evaluation in CI, question quality review in DeepEval evals, and question generation via Gemini Flash — need a model API. Using a single provider simplifies secrets management and keeps the codebase consistent.

Alternatives considered: individual provider keys (Anthropic, Google, OpenAI), Google AI Studio SDK directly for Gemini.

## Decision

Use OpenRouter for all inference, including Gemini Flash question generation. Reasons:

- Single `OPENROUTER_API_KEY` secret covers all models including Gemini Flash
- OpenRouter supports YouTube URL passthrough for Gemini models natively via the `file_data` parameter — no Google AI Studio SDK required
- Compatible with inspect-ai's OpenAI-compatible provider interface
- Model IDs are namespaced (`openrouter/<provider>/<model>`), making model swaps trivial

## Consequences

- The entire project requires one secret: `OPENROUTER_API_KEY`
- No Google AI Studio SDK dependency
- Researchers running their own evals can use their provider's API key directly with the appropriate inspect-ai provider
