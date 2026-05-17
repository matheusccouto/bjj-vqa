# ADR-0007: timestamp field on SampleRecord

## Status

Accepted

## Context

Sample records are generated from video frames at specific timestamps. The original schema stored `timestamp_seconds` as an optional field with a fallback to `0`. This created ambiguity: a missing timestamp could mean "unknown" or "start of video", and the fallback masked data quality issues.

Additionally, the field was not enforced at the schema level, so generated questions could arrive without timestamps and silently default to `0`.

## Decision

- Renamed `timestamp_seconds` to `timestamp` for brevity
- Made `timestamp` a **required** field on `SampleRecord` (`int`, no default)
- Migrated all 57 existing records by extracting the `&t=` parameter from their `source` URL (e.g. `?t=70s` → `70`)
- Records without a `&t=` param in their source default to `timestamp: 0`
- For the generate module, Gemini output is validated via `instructor` with a required `timestamp` field — if Gemini fails to return one, the model retries automatically

## Consequences

- **Positive**: Every question is guaranteed to have an explicit timestamp, improving traceability and enabling timestamp-aware features (e.g. temporal reasoning, frame sequencing)
- **Positive**: `instructor` validation ensures Gemini always produces timestamps — no silent fallbacks
- **Neutral**: All 57 existing records were migrated; the migration is a one-time operation
- **Negative**: Schema is no longer backward-compatible with records missing the field
