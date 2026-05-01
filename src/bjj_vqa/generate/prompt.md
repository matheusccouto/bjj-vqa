# Gemini generation prompt

This prompt will be rewritten for structured JSON output in the `bjj-vqa generate` implementation issue. The content below is the legacy freeform version preserved for reference.

---

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
</question_format>

<option_types>
Each question needs exactly one of each:
- CORRECT — the outcome the instructor taught, as a direct coaching cue
- WRONG-CONTEXT — a real BJJ principle, but from a different position or goal
- WRONG-MECHANISM — right outcome named, wrong physical reason given
- WRONG-DIRECTION — correct mechanism stated, but the effect is reversed

The correct answer must not be the longest option.
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
Count remaining concepts. This is K. Target 3-8 questions.
- Fewer than 3 → output "VIDEO TOO SHORT OR LOW DENSITY" and stop.
- More than 8 → keep the 8 clearest.
State K.
</phase>

<phase id="4" name="question construction">
Write each question following the format and option types above.
Ensure both COMPLETION and CLASSIFICATION appear at least once.
</phase>
</phases>
