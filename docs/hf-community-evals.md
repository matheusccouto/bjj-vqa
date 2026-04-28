# HuggingFace Community Evals Registration

## Status

- [x] `eval.yaml` validated in dataset repo
- [x] PR submitted to [huggingface/community-evals](https://github.com/huggingface/community-evals/pull/5) to add BJJ-VQA as a supported benchmark
- [ ] Allow-list activation by HuggingFace team (beta — requires human outreach)
- [ ] First evaluation results submitted from a model run

## What was done

### 1. Enhanced `eval.yaml`

Added required `inspect-ai` fields (`solvers` and `scorers`) and expanded `description` per the [Eval Results spec](https://huggingface.co/docs/hub/en/eval-results). The file is validated at push time on the Hub.

### 2. Updated `scripts/submit_hf.py`

Changed `task_id` from `default` to `bjj_vqa` to match the `eval.yaml` task ID.

### 3. PR to `huggingface/community-evals`

Submitted [PR #5](https://github.com/huggingface/community-evals/pull/5) adding BJJ-VQA to:
- README supported benchmarks table
- `BENCHMARK_TRACKER.md` prospective benchmarks
- `evaluation_manager.py` built-in benchmark mapping

## Registration Process

Per the [HF documentation](https://huggingface.co/docs/hub/en/eval-results):

1. **Create a dataset repo** with evaluation data — ✅ [couto/bjj-vqa](https://huggingface.co/datasets/couto/bjj-vqa)
2. **Add `eval.yaml`** to repo root — ✅ Done, with `inspect-ai` framework config
3. **File is validated at push time** — Will validate on next push to the HF dataset repo
4. **Get added to the allow-list** — ⏳ Beta step; requires contacting the HF team. The community-evals PR serves as this outreach.

## How to submit evaluation results

Once the benchmark is allow-listed, anyone can submit evaluation results to model repos via PR:

```yaml
# .eval_results/bjj-vqa.yaml
- dataset:
    id: couto/bjj-vqa
    task_id: bjj_vqa
  value: 0.72
  date: "2026-04-27"
  source:
    url: https://github.com/matheusccouto/bjj-vqa/actions/runs/...
    name: GitHub Actions Eval
```