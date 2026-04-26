# 0001: Evaluation framework — inspect-ai

**Status**: Accepted

## Context

The benchmark needs a framework to run evaluations: load the dataset, send prompts to models, score responses, and log results. The framework must support multimodal inputs (image + text) and integrate with the Hugging Face Community Evals system.

Alternatives considered: lm-evaluation-harness (EleutherAI), custom eval scripts, Eleuther's lighteval.

## Decision

Use inspect-ai (from the UK AI Safety Institute). It provides:

- Native multimodal support for image + text inputs
- First-class HF Community Evals integration via `eval.yaml`
- Support for all major model providers through a uniform API
- Built-in multiple-choice scoring, grouped metrics, and structured logging
- Active maintenance and a growing ecosystem

## Consequences

- `eval.yaml` must follow inspect-ai's Community Evals format
- All task definitions live in `src/bjj_vqa/task.py` as `@task` decorated functions
- Eval results are stored in inspect-ai's JSON log format
- Contributors running evaluations need `inspect-ai` installed (included in dependencies)
