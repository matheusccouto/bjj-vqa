# T1 STEM_LEAK

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark. Your task is to determine whether the question stem leaks enough information to eliminate answer options without looking at the image.

## Test definition

**PASS**: A practitioner reading only the stem and four options cannot eliminate more than one option without the image. The image is necessary to narrow down to the correct answer.

**FAIL**: The stem text alone (position description, named technique, described scenario) allows a practitioner to eliminate more than one wrong option without looking at the image.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

**Marked answer**: {answer}

## Instructions

1. Cover the image mentally — evaluate ONLY the stem and options as text.
2. List which options, if any, can be eliminated from text reasoning alone, and why.
3. If more than one option can be eliminated from text alone, the test FAILS.
4. Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences explaining which options (if any) are eliminable from text alone and why."
}
```
