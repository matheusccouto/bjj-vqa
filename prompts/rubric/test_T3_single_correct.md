# T3 SINGLE_CORRECT

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark. You will be shown the image and the question.

## Test definition

**PASS**: Given the image and BJJ domain knowledge, the marked answer is the only defensible correct answer. No other option is plausibly correct.

**FAIL**: Another option is also plausibly correct given the image and BJJ knowledge, even if the marked answer is "more correct" or "most commonly taught." If a knowledgeable practitioner could reasonably defend a different answer, the test fails.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

**Marked answer**: {answer}

## Instructions

Consider the image carefully. Apply BJJ domain knowledge. Assess whether any option other than the marked answer could be defended as correct by a knowledgeable practitioner viewing this image.

Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences. If failed, identify which option(s) are also plausibly correct and why."
}
```
