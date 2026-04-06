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
---

# BJJ-VQA

A Visual Question Answering benchmark that tests whether Vision-Language
Models can reason about Brazilian Jiu-Jitsu mechanics — not just recognize
technique names.

Each question presents a still frame from a CC-licensed instructional video
and asks *why* a specific visible detail matters. The correct answer cannot
be identified from text alone.

## Setup

```bash
uv sync
```

## Run an evaluation

```bash
export ANTHROPIC_AUTH_TOKEN=your-token
uv run inspect eval src/bjj_vqa/task.py --model anthropic/claude-opus-4-5
uv run inspect view
```

Any model supported by [inspect-ai](https://inspect.aisi.org.uk/providers.html)
works. Results go in `.eval_results/` in the model's repo.

## Dataset

1 question · gi only · single video source · intermediate

Images live in `data/images/` and are committed to this repo. The packaged
dataset (images + metadata) is published to Hugging Face Hub on each GitHub
release.

→ [huggingface.co/datasets/couto/bjj-vqa](https://huggingface.co/datasets/couto/bjj-vqa)

## Contributing

Contributions are pairs of (image + question) submitted as a single PR.

**Image requirements**
- JPEG, extracted manually from a CC BY or CC BY-SA YouTube video
- Filename: next sequential 5-digit ID (e.g. `00006.jpg`)
- Commit the frame directly

**Question requirements**
- Question text must establish full situational context (position, what both
  athletes are doing) so no prior frame is needed
- Ask *why* a visible detail matters — never ask *what* technique is shown
- All 4 choices must be plausible to someone who trains
- Correct answer must not be identifiable from text alone
- Answers distributed across A/B/C/D (no letter more than twice, no repeats
  in consecutive questions)

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

Allowed values: `experience_level` → `beginner /
intermediate / advanced` · `category` → `gi / no_gi` · `subject` → `guard / passing /
submissions / controls / escapes / takedowns`

**Attribution** — add a line to the Sources section below for any new video.

**Generating candidates** — paste the prompt below into Gemini with a CC
video attached. Output requires your review before submission.

<details>
<summary>Question generation prompt (Gemini)</summary>

```
You are a BJJ black belt with competition experience in gi and no-gi.

Watch the attached video. Generate exactly 5 questions. Be concise.

---

## Context

These questions are for BJJ-VQA, a Visual Question Answering benchmark that
tests whether AI vision models can reason about what is happening on the mat,
not just recognize techniques by name.

A VQA benchmark presents a model with an image and a multiple-choice
question. The model must choose the correct answer by reasoning about what
it sees. This creates a specific failure mode called a language shortcut: if
a model can identify the correct answer by reading the question and options
alone, without processing the image, the question is invalid.

A question is free of language shortcuts when:
- The correct answer cannot be guessed from BJJ knowledge alone
- The correct answer is not identifiable as the longest, most complete, or
  most technically worded option
- All 4 options are plausible to someone who trains but has not seen this frame
- The image is the deciding factor

---

## Question Construction

Every question must be self-contained. Write the question so it establishes
full situational context so no prior frame is needed. The image reveals only
the specific visible detail being asked about.

Ask WHY a visible detail matters mechanically. Never ask WHAT technique is
shown. Plain mat language only, no anatomy terms.

If SHORTCUT_RISK is MEDIUM or HIGH, rewrite before submitting.

---

## Answer Distribution

Spread correct answers across A, B, C, D. No letter appears more than twice.
No letter repeats in two consecutive questions. Vary grammatical structure
across options.

---

## Format

TIMESTAMP: [MM:SS]
QUESTION: [self-contained context + specific visible detail]
A) ...
B) ...
C) ...
D) ...
ANSWER: [A / B / C / D]
CONCEPT: [2-5 words, plain mat language]
EXPERIENCE_LEVEL: [beginner / intermediate / advanced]
CATEGORY: [gi / no_gi]
SUBJECT: [guard / passing / submissions / controls / escapes / takedowns]
RATIONALE: [Coach talking to a student. Why correct? Why each wrong option fails?]
SHORTCUT_RISK: [LOW / MEDIUM / HIGH]

---

## Distractor Rules

For each question, the four options must collectively include:
- One option applying a real BJJ principle to the wrong situation
- One option partially correct but wrong about the mechanism
- One option describing the opposite of what is happening
- The correct answer — not the longest or most complete-sounding option

---

## Coverage

After the 5 questions:
- SUBJECT distribution:
- EXPERIENCE_LEVEL distribution:
- Highest SHORTCUT_RISK and why:
- Frame with most occlusion risk:
- What is missing that the next video should cover:
```

</details>

## Sources

All frames extracted from Creative Commons licensed videos.

| Video | Author | License | Used at |
|-------|--------|---------|---------|
| [Armlock X Triangulo Partindo da Guarda Fechada](https://youtube.com/watch?v=SzL_uObk8fk) | Cobrinha BJJ & Fitness | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 00001 |

When using this dataset, please attribute:
> Frames from "Armlock X Triangulo Partindo da Guarda Fechada" by Cobrinha
> Brazilian Jiu-Jitsu & Fitness, CC BY 4.0.

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