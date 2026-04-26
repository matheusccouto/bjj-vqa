# BJJ-VQA Architecture

## What it is

BJJ-VQA is a multiple-choice Visual Question Answering benchmark. Each question pairs a still frame from a CC-licensed BJJ instructional video with four answer choices. The correct answer requires both the image (to identify position, roles, and technique detail) and BJJ domain knowledge (to reason about why that detail matters). Models that can answer from text alone, or that merely describe what they see, will not score well.

## Eval flow

```
samples.json + images/
       |
       v
  inspect-ai task (src/bjj_vqa/task.py)
       |  record_to_sample(): builds ChatMessageUser with image + question text
       v
  Model (any inspect-ai provider: OpenRouter, Anthropic, Google, etc.)
       |  Returns answer letter A/B/C/D
       v
  Scorer: choice() — exact match against target
  Metrics: accuracy(), grouped by experience_level / category / subject
       |
       v
  .eval_results/ log (JSON)
```

The `bjj_vqa_no_images` task variant strips images from the input. Running it alongside the main task reveals stem leak: questions the model answers correctly without seeing the image.

## HuggingFace Community Evals integration

The benchmark is registered as a HuggingFace Community Eval. The integration works as follows:

1. `eval.yaml` at the repo root defines the task spec in inspect-ai format. HF reads this file to know how to run the benchmark.
2. The packaged dataset (images + metadata) is published to `couto/bjj-vqa` on HF Hub on each GitHub release.
3. When a researcher evaluates a model, inspect-ai writes results to `.eval_results/` inside the model's own HF repository — not this dataset repo.
4. HF leaderboards aggregate `.eval_results/` from model repos to display benchmark rankings.

The `eval.yaml` must not be modified without verifying conformance with the HF Community Evals spec.

## Dataset structure

```
data/
  samples.json          — array of SampleRecord objects (source of truth)
  images/               — JPEG frames, named <id>.jpg (5-digit zero-padded)

sources/
  registry.jsonl        — one Source object per line; machine-readable attribution
```

See `src/bjj_vqa/schema.py` for the full `SampleRecord` and `Source` field specs.

## Out of scope

The following are explicitly not part of this benchmark in its current form:

- **Video temporal reasoning**: questions are single-frame only; transitions and sequences are not tested
- **Multilingual**: questions and answers are English-only; PT-BR support is future work
- **Beyond-image inputs**: no audio, no video clips, no multi-frame sequences
- **Non-instructional content**: competition footage is not used as a source
