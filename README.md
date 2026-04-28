---
pretty_name: BJJ-VQA
license: cc-by-sa-4.0
tags:
  - vision-language-models
  - visual-question-answering
  - benchmark
  - inspect-ai
  - bjj
  - brazilian-jiu-jitsu
task_categories:
  - visual-question-answering
language:
  - en
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: test
        path: data/test-*
---

# BJJ-VQA

A Visual Question Answering benchmark that tests whether Vision-Language Models can reason about Brazilian Jiu-Jitsu mechanics, not just recognize technique names.

Each question presents a still frame from a CC-licensed instructional video and asks *why* a specific visible detail matters. The correct answer cannot be identified from text alone.

## Methodology

Questions are constructed using a structured methodology: source selection (CC-licensed videos), concept extraction, frame selection, question construction (two stem formats, four option types), and validation against seven quality criteria. The correct answer to every question requires both the image and BJJ domain knowledge.

See [docs/methodology.md](docs/methodology.md) for the full construction methodology.

## For agents

AI coding agents should read [AGENTS.md](AGENTS.md) before starting work.

## Setup

```bash
uv sync
```

## Run an evaluation

```bash
export OPENROUTER_API_KEY=your-key
uv run inspect eval src/bjj_vqa/task.py --model openrouter/anthropic/claude-opus-4-5
uv run inspect view
```

Any model supported by [inspect-ai](https://inspect.aisi.org.uk/providers.html)
works. Evaluation results are stored in `.eval_results/` in the **model's** repository (not this dataset repo). See the [HuggingFace eval-results docs](https://huggingface.co/docs/hub/eval-results) for how to submit results.

## Dataset

Questions from CC-licensed BJJ instructional videos. Gi and no-gi positions across all experience levels.

Images live in `data/images/` and are committed to this repo. The packaged dataset (images + metadata) is published to Hugging Face Hub on each GitHub release.

→ [huggingface.co/datasets/couto/bjj-vqa](https://huggingface.co/datasets/couto/bjj-vqa)

### HuggingFace Community Eval

BJJ-VQA is being registered as a [HuggingFace Community Eval](https://huggingface.co/blog/community-evals). See [`eval.yaml`](eval.yaml) for the benchmark spec (format: [inspect-ai](https://inspect.aisi.org.uk/)) and the [HF Eval Results docs](https://huggingface.co/docs/hub/eval-results) for submission details.

## Contributing

Contributions are pairs of (image + question) submitted as a single PR.

**Image requirements**
- JPEG, extracted manually from a CC BY or CC BY-SA YouTube video
- Max resolution: 720p (1280px width) - higher resolutions will be resized
- Filename: next sequential 5-digit ID (e.g. `00006.jpg`)
- Commit the frame directly

**Question requirements**
- Question text must establish full situational context (position, what both athletes are doing) so no prior frame is needed
- Ask *why* a visible detail matters, never ask *what* technique is shown
- All 4 choices must be plausible to someone who trains
- Correct answer must not be identifiable from text alone
- Answers distributed across A/B/C/D (no letter more than twice, no repeats in consecutive questions)

**JSON fields** (add to `data/samples.json`):

```json
{
  "id": "00006",
  "image": "images/00006.jpg",
  "question": "...",
  "choices": ["...", "...", "...", "..."],
  "answer": "B",
  "experience_level": "beginner",
  "category": "gi",
  "subject": "submissions",
  "source": "https://www.youtube.com/watch?v=EXAMPLE&t=83s"
}
```

Allowed values: `experience_level` → `beginner / intermediate / advanced` · `category` → `gi / no_gi` · `subject` → `guard / passing / submissions / controls / escapes / takedowns`

**Attribution** - add a line to the Sources section below for any new video.

**Generating candidates**

1. Find a CC BY or CC BY-SA licensed BJJ instructional video on YouTube
2. Open Gemini and paste the prompt from [prompts/generate.md](prompts/generate.md)
3. Attach the video to Gemini and run the prompt
4. Review the output — verify timestamps, check validation passes, spot-check options
5. Paste the output to Claude Code with: "Implement these questions into `data/samples.json`"
6. Manually extract frames at the given timestamps using a screenshot tool and save to `data/images/`

Review your draft against the criteria in `docs/methodology.md` before opening a PR.

## Sources

All frames are extracted from Creative Commons licensed YouTube videos. See [ATTRIBUTIONS.md](ATTRIBUTIONS.md) for full source attribution following the TASL framework.

## Limitations

**Single-frame only**: Questions are based on still frames, not video. Temporal context (motion, transitions, sequence) is not captured.

**English only**: Questions and answers are in English. Non-English speakers or multilingual evaluation not supported.

**Source diversity**: All questions currently come from Cobrinha BJJ videos. Other instructors/styles may have different technique preferences.

**Dataset imbalance**:
- 67% intermediate, 21% beginner, 12% advanced
- 84% gi, 16% no_gi
- Some subjects have few questions (escapes: 1, passing: 3)

**Interpret accuracy carefully**: Categories with <5 questions are not statistically significant. Per-category accuracy should be interpreted with sample size in mind.

**Methodology conformance**: Questions added before the methodology was formalized have not been audited against all criteria. Some may be revised or replaced as a result of future review.

## Citation

```bibtex
@dataset{bjj_vqa_2026,
  author  = {Matheus Couto},
  title   = {BJJ-VQA: Brazilian Jiu-Jitsu Visual Question Answering Benchmark},
  year    = {2026},
  url     = {https://huggingface.co/datasets/couto/bjj-vqa},
  license = {CC BY-SA 4.0}
}
```

**Code**: GPL-3.0 · **Dataset**: CC BY-SA 4.0