# BJJ-VQA TODO List

Generated from comprehensive project and web research on 2026-04-10.

---

## High Priority

### 1. ✅ Create eval.yaml for HuggingFace Community Eval Registration

**DONE** - Created `eval.yaml` in repo root.

---

### 2. ✅ License Consistency - Verified Correct

**Confirmed**: Dual licensing is intentional and correct:
- **Code (GPL-3.0-or-later)**: Software copyleft
- **Dataset (CC BY-SA 4.0)**: Data/content with attribution requirement

Both are share-alike for their respective domains. Common practice in ML/AI projects.

---

### 3. ✅ Dataset Split - Already Correct

**Confirmed**: Eval-only benchmarks use 100% `test` split (like GPQA, HLE, GSM8K).

`cli.py` already handles this:
```python
dataset_dict = DatasetDict({"test": dataset})
```

No `split` field needed in samples.json.

---

### 4. Add Per-Category Accuracy Reporting

**Why**: Standard VQA benchmarks report accuracy breakdowns. Similar datasets (PlantVillageVQA, ActionAtlas) report per-category performance. Current eval only shows overall accuracy.

**Implementation**:
- Modify `task.py` to collect metadata during evaluation
- Add post-eval analysis script for breakdowns by:
  - `experience_level` (beginner/intermediate/advanced)
  - `category` (gi/no_gi)
  - `subject` (guard/passing/submissions/controls/escapes/takedowns)

---

## Medium Priority

### 5. Expand Test Coverage

**Current**: 1 test file (`tests/test_task.py`) with 3 tests
**Needed**:
- Schema validation tests
- CLI command tests (validate, publish)
- Edge cases: missing fields, invalid values, missing images

---

### 6. Add Human Baseline Comparison

**Why**: ActionAtlas reports human accuracy (61.64%) vs GPT-4o (45.52%). Essential context for interpreting model performance.

**Action**: Have BJJ practitioners answer questions, report their accuracy distribution.

---

### 7. Implement Confusion Analysis

**What**: Which techniques/questions are hardest? Which choices are most confused?

**Implementation**:
- Track per-question results
- Generate confusion matrix by subject/category
- Identify systematic errors (e.g., gi vs no_gi confusion)

---

### 8. Register with HuggingFace Community Evals

**Status**: `eval.yaml` created. Need to contact HuggingFace to be added to supported benchmarks list.

**Docs**: https://huggingface.co/blog/community-evals

---

## Low Priority / Future Considerations

### 9. Add reasoning_type Metadata

**Why**: PlantVillageVQA has 3 cognitive levels. Sports-QA has multiple question types. Current BJJ-VQA only has "decision" questions.

**Proposed types**:
- `perception`: What is shown in this frame?
- `mechanics`: Why does this detail matter?
- `decision`: What should you do next?
- `counterfactual`: What if opponent reacts differently?

---

### 10. Video Extension

**Context**: Sports-QA, ActionAtlas use video (temporal information important for sports). BJJ techniques have temporal phases.

**Action**: Consider adding video clips instead of single frames for some questions.

---

### 11. Expand Question Diversity

**Current**: Focus on "decision" questions ("What should you do?")
**Could add**: 
- "Why" questions (mechanics explanation)
- "Identify" questions (technique recognition)
- Chronology questions (sequence understanding)
- Counterfactual questions (alternative scenarios)

---

### 12. Add Consistency Metrics

**Why**: Research shows accuracy alone insufficient. Models can give correct answers inconsistently.

**Metrics to consider**:
- CaCV (Consistency across Choice Variations)
- CaQV (Consistency across Question Variations)

---

### 13. Robustness Testing

**What**: Test model performance under:
- Image perturbations (noise, blur)
- Question paraphrasing
- Choice ordering variations

---

### 14. Multi-model Baseline

**Current**: Only tested with Gemini via OpenRouter
**Should test**: GPT-4o, Claude, Qwen-VL, LLaVA, open-source models

---

### 15. Create Detailed Dataset Card

**HuggingFace requirements**:
- Data Fields description (complete)
- Splits information
- Creation process (detailed)
- Limitations/Bias section
- Known issues
- Source provenance

---

## Code Quality Items

### 16. Type Annotations in CLI

**File**: `src/bjj_vqa/cli.py`
**Issue**: Some functions lack complete type annotations

---

### 17. Error Handling Improvements

**File**: `src/bjj_vqa/cli.py`
**Issue**: Could add more specific error messages for validation failures

---

### 18. Add pyproject.toml Metadata

**Missing**:
- `keywords`: ["bjj", "jiu-jitsu", "vqa", "benchmark", "multimodal"]
- `classifiers`: development status, intended audience
- `urls`: repository, documentation, HuggingFace

---

## Documentation Items

### 19. Add Limitations Section to README

**Should document**:
- Single-frame limitations (no temporal context)
- Language limitation (English only)
- Source limitation (Cobrinha videos only currently)
- Experience level assumptions

---

### 20. Add Evaluation Guide

**Should include**:
- How to run eval with different models
- How to interpret results
- How to submit results to HF leaderboard

---

## References

Research sources informing this TODO:

**Benchmark Structure**
- HuggingFace eval.yaml spec: https://huggingface.co/docs/hub/eval-results
- Community evals: https://huggingface.co/blog/community-evals

**Similar Datasets**
- PlantVillageVQA: https://huggingface.co/datasets/sohamjune/PlantVillageVQA
- Sports-QA: https://arxiv.org/abs/2401.01505
- ActionAtlas: https://arxiv.org/abs/2410.05774

**Evaluation Best Practices**
- VQA metrics analysis: https://openaccess.thecvf.com/content_ICCV_2017/papers/Kafle_An_Analysis_of_ICCV_2017_paper.pdf
- Consistency metrics: https://hal.science/hal-04860239v1/file/Khanh_An_Evaluating_VQA_Models__Consistency_in_the_Scientific_Domain.pdf
- VLM evaluation guide: https://learnopencv.com/vlm-evaluation-metrics/

**HuggingFace Publishing**
- Dataset cards: https://huggingface.co/docs/hub/datasets-cards
- Licenses: https://huggingface.co/docs/hub/repositories-licenses

---

## Next Action

**Per-Category Accuracy Reporting** - implement breakdowns by experience_level, category, subject.