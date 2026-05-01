# 0006: Question construction methodology

**Status**: Accepted

## Context

Early questions in the dataset were constructed informally, without a documented process. As the benchmark grows and contributions from others are accepted, there needs to be a shared, reproducible standard for what makes a question valid. Without one, question quality is inconsistent and the benchmark is not defensible as a rigorous evaluation.

## Decision

Formalize the construction process in `CONTEXT.md` (at the repo root). The methodology specifies:

- Source selection and licensing requirements
- Concept extraction and the "imageable" test
- Frame selection criteria
- Two stem formats (COMPLETION, CLASSIFICATION)
- Four option types (CORRECT, WRONG-CONTEXT, WRONG-MECHANISM, WRONG-DIRECTION)
- Quality evals (STEM_LEAK, ROLE_COHERENCE, SINGLE_CORRECT, IMAGE_DEPENDENCY, IMAGE_CLARITY, BJJ_CORRECTNESS, FORMAT_COMPLIANCE)
- Metadata requirements
- Dataset-level balance targets

`CONTEXT.md` is the canonical reference for all question contribution decisions. The Gemini generation prompt in `src/bjj_vqa/generate/prompt.md` implements this methodology.

## Consequences

- New questions must pass all quality evals before being accepted
- Changes to the generation prompt should accompany updates to `CONTEXT.md`
