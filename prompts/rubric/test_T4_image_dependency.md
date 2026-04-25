# T4 IMAGE_DEPENDENCY

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark. Your task is to determine whether the image is necessary to answer the question correctly.

## Test definition

**PASS**: A practitioner with strong BJJ knowledge cannot reliably identify the correct answer from the stem and options alone — they must see the image to determine which option applies.

**FAIL**: The question can be answered correctly from the stem text and BJJ domain knowledge alone, without the image. The image adds no information that changes the answer.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

**Marked answer**: {answer}

## Instructions

Reason about what visual information is necessary to answer correctly. Ask: "If I could not see the image but I had strong BJJ knowledge, would I be able to identify the correct answer?" If yes, the test fails.

Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences explaining what visual information is (or is not) required to select the correct answer."
}
```
