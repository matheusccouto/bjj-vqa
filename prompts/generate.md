# Question generation prompt

This is the canonical prompt for generating candidate questions from CC-licensed BJJ instructional videos. It is used with a frontier vision-language model (e.g., Gemini) that can read video. Changes to this prompt should accompany updates to `docs/methodology.md`.

---

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
