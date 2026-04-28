# Question generation prompt

This is the canonical prompt for generating candidate questions from CC-licensed BJJ instructional videos. It is used with a frontier vision-language model that can read video. Changes to this prompt should accompany updates to `docs/methodology.md`.

## Model recommendation

**Primary model: Gemini 2.5 Flash** via Google AI Studio (free tier, ~1500 req/day).

Rationale:
- Native video understanding (reads full video, no frame extraction needed for input)
- 1M token context window — handles long instructional videos
- Free tier sufficient for dataset construction volumes
- Competitive quality on visual reasoning benchmarks

Alternatives considered:
- **Gemini 2.5 Pro**: Higher quality but no free video tier; costs ~$1.25/video. Not justified for generation that will be manually reviewed anyway.
- **GPT-4o**: Good image reasoning but requires manual frame extraction for video (no native video API at free tier). Adds pipeline complexity without quality upside for this task.
- **Claude Sonnet 4**: Excellent reasoning but no video input; would require frame-level prompting only. Loses temporal context.

Stick with Gemini 2.5 Flash until a model with demonstrably better video-BJJ reasoning becomes available at comparable cost.

---

```markdown
<role>
You are an expert Brazilian Jiu-Jitsu black belt building a VQA benchmark dataset
by watching instructional videos. Your questions must require BOTH the image and
BJJ domain knowledge to answer — neither alone can suffice.
</role>

<task>
Watch the attached video in full. Extract the concepts the instructor teaches.
Turn them into multiple-choice questions that test whether a vision model
understands BJJ — not whether it can describe an image.
</task>

<validity_rule>
A question is valid ONLY when BOTH inputs are REQUIRED to answer it:
- BJJ domain knowledge tells you what the instructor taught
- The image tells you WHICH option applies that teaching correctly

If the image alone is enough → invalid (tests OCR, not understanding).
If BJJ knowledge alone is enough → invalid (tests trivia, not vision).
</validity_rule>

<anti_pattern_rules>
These are the most common failures in generated questions. Every rule below exists
because real generated questions have failed these checks.

STEM LEAK — the most common and most damaging failure:
NEVER name the position, technique, or scenario in the stem. The image must carry
the burden of identifying what is happening.

BAD (leaks the scenario):
  "In this back-take transition, the first grip to establish is"
  → A reader who knows BJJ can eliminate options without seeing the image.

GOOD (image carries the load):
  "The first grip to establish here is"
  → You must see the image to know what position and options are relevant.

BAD (leaks the technique):
  "When performing the gi choke from mount, the primary pressure comes from"
  → The stem names the technique and position.

GOOD (image identifies the technique):
  "The primary pressure for the finish here comes from"
  → You must see the image to know which finish is being applied.

BAD (leaks through option filtering):
  "The escape being shown works best against"
  A) a tight guillotine     B) a loose guillotine
  C) a darce choke          D) an anaconda choke
  → BJJ knowledge alone eliminates C and D (different choke family).

GOOD (all options plausible for the same position):
  "The detail that makes this escape work is"
  A) framing with the forearm       B) shrimping to create angle
  C) underhooking the far arm       D) posting on the mat
  → You must see the image to know which detail the instructor emphasized.

OPTION LENGTH SIGNAL — the correct answer must not be the longest option.
Longer correct answers act as a signal. Keep all four options within ~30%
character count of each other.

REPEATED DISTRUCTOR PATTERNS — vary your distractor strategies across questions.
Do not use the same WRONG-CONTEXT pattern (e.g., "from a different guard type")
for more than half the questions in a set.
</anti_pattern_rules>

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
  VISUAL_ANCHOR: [if YES, what specific visible detail would a viewer need to see?]
Keep only YES concepts where the visual anchor is concrete (a grip, an angle, a
body part placement), not abstract ("good posture" or "proper timing").

Drop concepts where the visual anchor is vague or could apply to any position.
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
- 2 → proceed (minimum for a useful session)
- 3 to 6 → ideal range, proceed with all
- More than 6 → keep the 6 clearest. State drops in one word each.
State K.

Target: 3-6 questions per video. Fewer questions with higher quality beats
more questions with lower quality. If you are unsure about a concept, drop it
rather than produce a marginal question.
</phase>

<phase id="4" name="question construction">
Write each question following the format and option types above.
Ensure both COMPLETION and CLASSIFICATION appear at least once.

For EACH question, you must identify a REQUIRED VISUAL FACT:
the specific thing a viewer must see in the image to determine the correct
answer. If you cannot name one, the question fails T4 and must be redesigned.

Common visual facts:
- which grip is being used (collar vs lapel vs sleeve)
- which limb is applying pressure (elbow vs shoulder vs hip)
- body orientation relative to opponent (angle, direction of pressure)
- sequence position (first vs second vs third step visible in frame)
</phase>

<phase id="5" name="validation">
For EACH question, run these checks. Rewrite any question that fails.

T1 STEM LEAK — Cover the image. Read only the stem and four options.
Can more than one option be eliminated from stem text alone?
If YES → FAIL. Rewrite the stem to remove scenario/position/technique names.

T2 ROLE COHERENCE — Look at the image. Is every option internally consistent
with the visible scenario? If any option mixes roles or references a different
position → FAIL. Rewrite the options.

T3 SINGLE CORRECT — Given the image scenario, is the marked answer the only
defensible answer? If another option is also plausible → FAIL.

T4 IMAGE DEPENDENCY — Can this question be answered from stem + BJJ knowledge
alone, without the image? What SPECIFIC visual fact is required?
If you cannot name one → FAIL. Rewrite to remove text-only paths.

T5 OPTION LENGTH — Is the correct answer the longest option? If yes → FAIL.
Reorder or reword options so the correct one is not longest.

After rewriting, re-check ALL criteria for the rewritten question.
Do not proceed until every question passes T1, T2, T3, T4, and T5.
</phase>

</phases>

<output_format>
For each question:

QUESTION [N of K]
CONCEPT TESTED: [instructor's teaching in one line]
VISUAL FACT: [the specific visible detail required to answer — must be concrete]
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
VALIDATION: T1=[PASS/FAIL] T2=[PASS/FAIL] T3=[PASS/FAIL] T4=[PASS/FAIL] T5=[PASS/FAIL]
T4_VISUAL_FACT: [one sentence naming the specific visual information required]

---

After all K questions:

CONCEPTS EXTRACTED: [N]
DROPPED (not imageable): [list with one-line reason each]
K: [N]
STEM TYPE distribution: [COMPLETION: N, CLASSIFICATION: N]
SUBJECT distribution: [list]
EXPERIENCE_LEVEL distribution: [list]
Weakest question: [N — one sentence why]
Gap for next video: [one sentence]
</output_format>
```