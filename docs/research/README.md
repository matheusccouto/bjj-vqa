# Research notes

This directory contains investigation notes written during issue work. Write a research note when you spend non-trivial time investigating something that is not obvious from the code — a surprising behavior, a rejected approach, a comparison of options, or findings that informed a significant decision.

## When to write a research note

- You investigated why something behaves unexpectedly and the answer is not in the code
- You compared two or more approaches and chose one; the reasoning would help a future contributor
- You ran experiments or benchmarks that informed a decision
- You found information in an external source that is not linked anywhere in the repo

## Naming convention

Files are named `YYYY-MM-DD_<short-topic>.md`. The date is when the investigation was done.

Example: `2026-04-15_stem-leak-analysis.md`

## Format

No fixed template — write enough to be useful to a future reader who just hit the same question. Include the question you were investigating, what you found, and what you decided or recommended.

Research notes are not ADRs. An ADR records a decision and its consequences. A research note records an investigation that may or may not have led to a decision.
