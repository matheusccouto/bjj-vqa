# T5 IMAGE_CLARITY

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark. You will be shown the image and the question stem.

## Test definition

**PASS**: A human BJJ practitioner viewing the image can confirm that the scenario the stem implies is happening — the position, roles, and key detail are clearly visible.

**FAIL**: The image is ambiguous, shows a different moment than the stem implies, is unclear about what is happening, or would require guessing about position or roles.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

## Instructions

Examine the image carefully. Does it clearly show the scenario that the stem is asking about? Can you confirm the position, attacker/defender roles, and the key technical detail that the question hinges on?

Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences describing what is clearly visible and what (if anything) is ambiguous or missing."
}
```
