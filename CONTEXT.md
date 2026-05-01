# BJJ-VQA Context

## What it is

BJJ-VQA is a multiple-choice Visual Question Answering benchmark. Each question pairs a still frame from a CC-licensed BJJ instructional video with four answer choices. The correct answer requires both the image (to identify position, roles, and technique detail) and BJJ domain knowledge (to reason about why that detail matters). Models that answer from text alone, or that merely describe what they see, will not score well.

## Eval flow

```
data/samples.json + data/images/
       |
       v
  inspect-ai task (src/bjj_vqa/task.py)
       |  record_to_sample(): builds ChatMessageUser with image + question text
       v
  Model via OpenRouter (any inspect-ai provider)
       |  Returns answer letter A/B/C/D
       v
  Scorer: choice() — exact match against target
  Metrics: accuracy(), grouped by experience_level / category / subject
       |
       v
  logs/ (.eval log files)
```

## HuggingFace Community Evals

`eval.yaml` at the repo root defines the task spec. The dataset is published to `couto/bjj-vqa` on HF Hub on each GitHub release. Researchers run evals against their own models; results go into `.eval_results/` inside the model's HF repo.

## Dataset structure

```
data/
  samples.json       — array of SampleRecord objects (source of truth)
  images/            — JPEG frames, named with short UUID hex (e.g. a3f7b9c1.jpg)

sources/
  registry.jsonl     — one Source object per line; machine-readable attribution
```

See `src/bjj_vqa/schema.py` for the full `SampleRecord` and `Source` field specs.

## Question validity

Every question must satisfy this core criterion: **both the image and BJJ domain knowledge are required to answer correctly**. If either alone suffices, the question is invalid.

## Question structure

**Stem formats** — one of two types per question:

- **COMPLETION**: end an instructor statement naturally; options are possible endings
- **CLASSIFICATION**: ask what role or priority a technique/detail has

Both types must appear in the dataset (at least 30% each).

**Option types** — exactly one of each per question:

- **CORRECT**: the outcome the instructor taught
- **WRONG-CONTEXT**: a real BJJ principle, but from a different position or goal
- **WRONG-MECHANISM**: right outcome named, wrong physical reason given
- **WRONG-DIRECTION**: correct mechanism stated, but the effect is reversed

**Format rules**:

- Four options labeled A through D, similar in length
- Correct answer must not be the longest option
- No hedge words ("usually", "sometimes") or contrast words ("but", "although") inside options
- Options read like short, confident coaching cues
- Do not name the scenario in the stem — the image carries that work

## Quality evals

Questions are validated against these criteria (defined in `evals/`):

- **STEM_LEAK**: cover the image; if more than one option can be eliminated from text alone, fail
- **ROLE_COHERENCE**: every option must be internally consistent with the scenario in the image
- **SINGLE_CORRECT**: the marked answer must be the only defensible answer given the image
- **IMAGE_DEPENDENCY**: answering must require the image; fail if solvable from text + BJJ knowledge alone
- **IMAGE_CLARITY**: a human BJJ practitioner must be able to confirm what the stem implies is happening
- **BJJ_CORRECTNESS**: marked answer must be BJJ-correct; distractors must be based on real concepts
- **FORMAT_COMPLIANCE**: options similar length, correct answer not longest, no hedge or contrast words

## Dataset balance targets

- Both stem types: at least 30% each
- Answer letter distribution: no single letter above 30%
- Category/subject buckets: soft warning if any bucket exceeds 40%

## Generation pipeline

Gemini Flash via OpenRouter processes a YouTube URL and returns structured questions + suggested timestamps. Frames are extracted via yt-dlp + ffmpeg. See `src/bjj_vqa/generate/prompt.md` for the Gemini system prompt.

Two parallel approaches exist (see PRD):
- **Track A**: `bjj-vqa generate <url>` writes directly to `data/` and opens a PR via GitHub Actions
- **Track B**: agentic loop where OpenCode iterates with Gemini using `bjj-vqa generate --instructions`, reviews with `deepeval test run evals/`, then commits via `bjj-vqa add`

## CLI

```
bjj-vqa validate          — validate samples.json schema and image paths
bjj-vqa validate-sources  — validate sources/registry.jsonl cross-references
bjj-vqa publish           — publish dataset to HuggingFace Hub
bjj-vqa generate <url>    — generate questions from YouTube URL (Track A: writes to data/)
bjj-vqa add <dir>         — merge tmp dir output into data/ (Track B only)
```

## Versioning

- **v0.1**: existing 57 questions — development fixture set
- **v1**: mass-produced, fully validated questions from the generation pipeline
