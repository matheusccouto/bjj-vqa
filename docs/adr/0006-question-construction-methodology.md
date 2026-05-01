# 0006: Question construction methodology

**Status**: Accepted

## Context

Early questions in the dataset were constructed informally, without a documented process. As the benchmark grows and contributions from others are accepted, there needs to be a shared, reproducible standard for what makes a question valid. Without one, question quality is inconsistent and the benchmark is not defensible as a rigorous evaluation.

## Decision

Formalize the construction process as a written methodology document: `docs/methodology.md`. The methodology specifies:

- Source selection and licensing requirements
- Concept extraction and the "imageable" test
- Frame selection criteria
- Two stem formats (COMPLETION, CLASSIFICATION)
- Four option types (CORRECT, WRONG-CONTEXT, WRONG-MECHANISM, WRONG-DIRECTION)
- Seven quality criteria (T1-T7) for manual review before acceptance
- Metadata requirements
- Dataset-level balance targets

This document is the canonical reference for all question contribution decisions.

## Consequences

- New questions must satisfy all seven criteria (manual curator review) before being accepted
- The generation prompt in `prompts/generate.md` is part of the methodology; changes to it should accompany updates to `docs/methodology.md`
