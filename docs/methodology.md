# BJJ-VQA Question Construction Methodology

This document describes the structured, rubric-driven process used to construct questions in BJJ-VQA. The methodology is fully reproducible by any researcher with access to source materials, a screenshot tool, and access to a frontier vision-language model and a frontier reasoning model.

## Core principle

Every question must satisfy this validity criterion: **both the image and BJJ domain knowledge are required to answer correctly**. If either alone suffices, the question is invalid.

## Process

### Step 1: Source selection

Each question is derived from an instructional video with documented licensing. Acceptable source types:

- Creative Commons YouTube content (verified per video via the YouTube CC license filter)
- YouTube content from creators who have granted explicit email permission
- The dataset author's own filmed content
- Synthetically generated content

Individual frames from non-Creative-Commons YouTube videos may be used sparingly under fair use, with explicit attribution. These should not be the majority of the benchmark.

The source must be documented in `sources/registry.jsonl` with: url, title, creator, license_type, permission_reference (if applicable), notes.

### Step 2: Concept extraction

Watch the source video. For each discrete concept the instructor teaches:

- Record the concept close to the instructor's own words
- Determine whether the concept is imageable: can a still frame show which option applies it correctly?
- Identify a candidate timestamp where the concept is clearly demonstrated

Drop concepts that fail the imageable test. Aim for 4-8 concepts per 20-minute video.

### Step 3: Frame selection

For each concept, choose the best timestamp. Criteria:

- Stable position (not mid-transition)
- Key detail clearly visible (not occluded, not motion-blurred)
- Minimal ambiguity about what is happening
- No text overlays that give away the answer

Capture the frame as a JPEG screenshot using any screenshot tool you prefer. Save with the next sequential 5-digit ID.

### Step 4: Question construction

Use the structured generation prompt (see `prompts/generate.md`) with a frontier vision-language model that can read source video. The model proposes candidate questions; the human curator (the dataset author, a BJJ practitioner) reviews each one.

**Stem format** — one of two types:

- **COMPLETION**: end an instructor statement naturally; options are possible endings
- **CLASSIFICATION**: ask what role or priority a technique/detail has

Both stem types must appear in the dataset.

**Option types** — exactly one of each per question:

- **CORRECT**: the outcome the instructor taught
- **WRONG-CONTEXT**: a real BJJ principle, but from a different position or goal
- **WRONG-MECHANISM**: right outcome named, wrong physical reason given
- **WRONG-DIRECTION**: correct mechanism stated, but the effect is reversed

**Format rules**:

- Four options labeled A through D
- All options similar in length
- Correct answer must not be the longest option
- No hedge words ("usually", "sometimes")
- No contrast words ("but", "although", "however") inside options
- Options read like short, confident coaching cues

**Critical rule**: do not name the scenario in the stem. The image must carry the work of identifying position, attacker/defender roles, and technique. A stem that says "in this back-take transition" leaks the scenario; the model can eliminate options without looking. Instead, write stems that assume the reader has seen the image and ask about a specific detail.

### Step 5: Adversarial rubric validation

Before accepting a question, run the seven-criterion rubric. Default to rejection. Each test is binary; stop at the first failure.

- **T1 STEM_LEAK**: cover the image. Read only the stem and four options. If more than one option can be eliminated from stem text alone, fail.
- **T2 ROLE_COHERENCE**: is every option internally consistent with the scenario in the image? Options that mix attacker/defender roles or wrong positions are weak distractors. Fail if any option is trivially wrong due to role/position confusion.
- **T3 SINGLE_CORRECT**: given the scenario, is the marked answer the only defensible answer? Fail if another option is also plausibly correct, even if the marked answer is "more correct."
- **T4 IMAGE_DEPENDENCY**: does answering require the image? Identify what visual information is necessary. Fail if the question can be answered from stem + BJJ knowledge alone.
- **T5 IMAGE_CLARITY**: can a human BJJ practitioner confirm what the stem implies is happening? Fail if the image is ambiguous or shows a different moment.
- **T6 BJJ_CORRECTNESS**: is the marked answer actually correct? Is the stated mechanism accurate? Are distractors based on real BJJ concepts? Fail if the correct answer is BJJ-wrong or if a distractor is BJJ-nonsensical.
- **T7 FORMAT_COMPLIANCE**: options similar length, correct answer not longest, no hedge or contrast words. Fail if format violated.

The rubric is implemented as `uv run bjj-vqa rubric <question-id>` (see Phase 5 below). T1, T4 require an LLM call (we use the Anthropic API). T2, T3, T5, T6 are LLM-judged. T7 is pure string check.

### Step 6: Metadata

Every question records the fields documented in `src/bjj_vqa/schema.py`. The schema is enforced by `uv run bjj-vqa validate`.

### Step 7: Dataset-level balance

Across the full benchmark:
- Both stem types represented (at least 30% of each)
- Option letter distribution: no letter dominates (max 30%)
- Category and subject distributed (no single bucket above 40% unless intentional)
- A subset of questions tagged is_unanswerable=true (correct answer is "cannot be determined" or equivalent), to test model abstention

## No-image ablation

After adding a batch of questions, run the no-image ablation to check for stem leak at scale:

```bash
uv run inspect eval src/bjj_vqa/task.py@bjj_vqa_no_images --model <model_id> --log-dir logs/no_image/
uv run python scripts/no_image_report.py logs/no_image/
```

The report lists individual questions answered correctly without images — these are candidates for rewriting or removal. Do not add `bjj-vqa rubric --all` to CI; run it manually with your `ANTHROPIC_API_KEY` when you want a diagnostic.

## What this methodology does not cover

- Frame extraction from video. Contributors use whatever screenshot tool they prefer.
- Source-video discovery. Contributors find sources via the YouTube CC filter or by direct creator outreach.
- Translation. The dataset is currently English-only; bilingual support is future work.
- Video-temporal questions. The current benchmark is single-frame only.

## Reproducibility

A researcher with the same source videos, a screenshot tool, access to Gemini (or any frontier video VLM), and access to Claude (or any frontier reasoning model) can reproduce the construction process by following Steps 1-7 of this document.
