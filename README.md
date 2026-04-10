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

This benchmark is registered as a [HuggingFace Community Eval](https://huggingface.co/blog/community-evals). To evaluate a model:

```bash
# From the HuggingFace dataset
inspect eval couto/bjj-vqa --model <model_id>

# Or from this repository
inspect eval src/bjj_vqa/task.py --model <model_id>
```

**eval.yaml configuration:**
- `evaluation_framework`: `inspect-ai`
- `field_spec.input`: `question`
- `field_spec.input_image`: `image`
- `field_spec.target`: `answer`
- `field_spec.choices`: `choices`
- `split`: `test`

## Contributing

Contributions are pairs of (image + question) submitted as a single PR.

**Image requirements**
- JPEG, extracted manually from a CC BY or CC BY-SA YouTube video
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
2. Open Gemini and paste the prompt below
3. Attach the video to Gemini and run the prompt
4. Review the output — verify timestamps, check validation passes, spot-check options
5. Paste the output to Claude Code with: "Implement these questions into `data/samples.json`"
6. Manually extract frames at the given timestamps and save to `data/images/`

<details>
<summary>Question generation prompt</summary>

```markdown
<role>
You are an expert Brazilian Jiu-Jitsu black belt building a VQA benchmark dataset
by watching instructional videos.
</role>

<task>
Watch the attached video in full. Extract the concepts the instructor teaches.
Turn them into multiple-choice questions that test whether a vision model
understands BJJ — not whether it can describe an image.

Reason through each step internally before writing output.
</task>

<validity_rule>
A question is valid only when BOTH inputs are required to answer it:
- knowing the concept the instructor taught
- reading the image to determine which option applies it correctly

If the image alone is enough → invalid.
If BJJ knowledge alone is enough → invalid.
</validity_rule>

<question_format>
Write each question as a cloze of the instructor's own words. Use both stem
formats at least once across your K questions.

COMPLETION — take a statement the instructor made, end the stem naturally,
and make the options the possible endings. Use when the instructor stated a
principle, preference, or sequence step directly.

CLASSIFICATION — present a technique or detail and ask what role or priority
it has. Use when the instructor categorized something (first resort, last
resort, only when X, never when Y, etc.).

Options must read like short, confident coaching cues. Keep all four similar
in length. No hedges. No "but", "although", or "however" inside options.

<example type="completion">
Q: When the forearm cuts across the front of the neck, the finish is mostly
   done by
A) rowing your elbow
B) squeezing your hands
C) driving your shoulder into their jaw
D) dropping your hip toward the mat
</example>

<example type="classification">
Q: Using your leg to bend their leg so you strip the grip is
A) the first thing to try
B) something to use when your arms alone cannot break it
C) a setup for the knee cut, not a grip strip
D) effective only after you have secured the underhook
</example>
</question_format>

<option_types>
Each question needs exactly one of each:
- CORRECT — the outcome the instructor taught, as a direct coaching cue
- WRONG-CONTEXT — a real BJJ principle, but from a different position or goal
- WRONG-MECHANISM — right outcome named, wrong physical reason given
- WRONG-DIRECTION — correct mechanism stated, but the effect is reversed

The correct answer must not be the longest option.
Distribute answers evenly across A/B/C/D — no letter repeats consecutively,
no letter appears more than ceil(K/2) times across all questions.
</option_types>

<phases>

<phase id="1" name="concept extraction">
List every distinct principle the instructor explicitly teaches.
For each:
  CONCEPT: [the teaching, close to verbatim]
  IMAGEABLE: YES / NO — can an image show which option applies it correctly?
Keep only YES concepts.
</phase>

<phase id="2" name="frame selection">
For each YES concept, find the best timestamp.
Valid frame: stable position, key detail clearly visible, not mid-transition.
  CONCEPT [N] → [HH:MM:SS]: [one sentence — what is visible]
Mark unframeable concepts and drop them.
</phase>

<phase id="3" name="question count">
Count remaining concepts. This is K.
- Fewer than 2 → output "VIDEO TOO SHORT OR LOW DENSITY" and stop.
- More than 8 → keep the 8 clearest. State drops in one word each.
State K.
</phase>

<phase id="4" name="question construction">
Write each question following the format and option types above.
Ensure both COMPLETION and CLASSIFICATION appear at least once.
</phase>

<phase id="5" name="validation">
For each question, check:
T1 — Can a practitioner answer without the image, from the concept alone? FAIL if yes.
T2 — Can someone answer by describing the image, without the concept? FAIL if yes.
T3 — Is the correct answer the longest or most technical option? FAIL if yes.
Rewrite any question that fails.
</phase>

</phases>

<output_format>
For each question:

QUESTION [N of K]
CONCEPT TESTED: [instructor's teaching in one line]
STEM TYPE: [COMPLETION / CLASSIFICATION]
TIMESTAMP: [HH:MM:SS]
EXPERIENCE_LEVEL: [beginner / intermediate / advanced]
CATEGORY: [gi / no_gi]
SUBJECT: [guard / passing / submissions / controls / escapes / takedowns]
SOURCE SECONDS: [integer]
SOURCE URL: https://youtu.be/<VIDEO_ID>?t=<SECONDS>

[question stem]

A) [option]   [CORRECT / WRONG-CONTEXT / WRONG-MECHANISM / WRONG-DIRECTION]
B) [option]   [type]
C) [option]   [type]
D) [option]   [type]

ANSWER: [letter]
VALIDATION: T1=[PASS/FAIL] T2=[PASS/FAIL] T3=[PASS/FAIL]

---

After all K questions:

CONCEPTS EXTRACTED: [N]
UNFRAMEABLE: [list]
K: [N]
STEM TYPE distribution: [COMPLETION: N, CLASSIFICATION: N]
SUBJECT distribution: [list]
EXPERIENCE_LEVEL distribution: [list]
Weakest question: [N — one sentence why]
Gap for next video: [one sentence]
</output_format>
```

</details>

## Sources

All frames are extracted from Creative Commons licensed YouTube videos. See [ATTRIBUTIONS.md](ATTRIBUTIONS.md) for full source attribution following the TASL framework.

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