# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the bjj-vqa project. An ADR documents a significant decision, its context, and its consequences.

## Format

Each ADR is a Markdown file named `NNNN-short-title.md` with the following structure:

```markdown
# NNNN: Short title

**Status**: Accepted | Deprecated | Superseded by NNNN

## Context

Why this decision needed to be made. The forces at play, constraints, and alternatives considered.

## Decision

What was decided and why.

## Consequences

What becomes easier, harder, or different as a result.
```

## When to write an ADR

- Introducing or removing a dependency
- Choosing a license
- Selecting an evaluation framework or dataset format
- Changing the schema in a way that affects existing records
- Any decision that a future contributor would wonder "why did they do it this way?"

See the `NNNN-*.md` files in this directory; each ADR title is its filename.
