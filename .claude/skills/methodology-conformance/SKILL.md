---
name: methodology-conformance
description: Verify a question conforms to the BJJ-VQA construction methodology before adding it to the dataset. Make sure to use this skill whenever the user is adding a new question, modifying an existing question, or asks whether a question is valid. Also use it when reviewing PRs that touch data/samples.json.
---

# Methodology conformance check

When the user is adding or reviewing a question in BJJ-VQA, follow this process:

1. Read `docs/methodology.md` for the canonical methodology
2. Read the question being added/modified from `data/samples.json` or the PR diff
3. Verify each of these:
   - Source URL is in `sources/registry.jsonl` with a valid license_type
   - Frame at the question's source timestamp shows a stable position
   - Stem does not name the scenario (no "in this back-take transition" leaks)
   - All four options are similar in length
   - The correct answer is not the longest option
   - No hedge or contrast words appear inside options
4. Run the seven-criterion rubric:
   ```
   uv run bjj-vqa rubric <question-id>
   ```
5. If the rubric returns PASS, suggest the question is ready
6. If the rubric returns REWRITE or REJECT, present the specific failures to the user and propose revisions

If multiple questions need checking, run the rubric on all of them and present a summary table.
