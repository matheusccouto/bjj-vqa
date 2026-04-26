# 0004: Schema validation — Pydantic v2

**Status**: Accepted

## Context

`data/samples.json` is the source of truth for the dataset. All tooling (CLI, tests, eval pipeline) must be able to validate records against a schema. The validation must be strict enough to catch type errors, missing fields, and invalid enum values before they reach the eval pipeline.

## Decision

Use Pydantic v2 for schema definition and validation. Reasons:

- Fail-fast validation with structured error messages
- Native JSON Schema export (useful for CI and documentation)
- First-class Python type annotation integration
- Ecosystem fit: Pydantic is already a transitive dependency of inspect-ai
- v2 is significantly faster than v1 and is the current maintained version

## Consequences

- All record structure is defined in `src/bjj_vqa/schema.py` as Pydantic `BaseModel` subclasses
- `uv run bjj-vqa validate` uses Pydantic validation as the source of truth
- Adding new fields requires updating the schema and ensuring backward-compatible defaults for existing records
- Tests use `SampleRecord.model_validate()` directly
