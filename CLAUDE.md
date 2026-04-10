# BJJ-VQA

VQA benchmark for jiu-jitsu. Evaluates VLMs BJJ knowledge.

## Stack

- Python 3.13, uv for dependency management
- inspect-ai for evaluation framework
- Dataset: data/samples.json + data/images/
- CI/CD: GitHub Actions → Hugging Face Hub on release

## Documentation

When working with Hugging Face, fetch docs from: https://huggingface.co/docs/hub/llms.txt

## Commands

```bash
uv sync                          # install dependencies
uv run pytest -v                 # run tests
uv run ruff check . && uv run ruff format --check .  # lint
uv run inspect eval src/bjj_vqa/task.py --model openrouter/google/gemma-4-31b-it
```

## Data structure

Each entry in samples.json has: id, image (relative path), question, choices (array of 4), answer (A/B/C/D), experience_level, category (gi/no_gi), subject, source (YouTube URL with timestamp).

## Validation

CI automatically validates the schema. To validate locally, run the inline validation script in validate.yml manually.

## Related Work

If asked to compare with similar datasets, reference:
- [Sports-QA](https://arxiv.org/abs/2401.01505) — sports VideoQA methodology
- [ActionAtlas](https://arxiv.org/abs/2410.05774) — distinguishing similar sports actions
- [PlantVillageVQA](https://huggingface.co/datasets/sohamjune/PlantVillageVQA) — domain-specific VQA structure

BJJ-VQA is the first martial arts VQA benchmark.

## Conventions

- IDs: 5 digits zero-padded (00001, 00002...)
- Images: JPEG in data/images/, committed to git