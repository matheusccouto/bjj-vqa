# T6 BJJ_CORRECTNESS

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark.

## Test definition

**PASS**: The marked answer is factually correct BJJ. The mechanism described is accurate. The distractors are based on real BJJ concepts (even if wrong in this context).

**FAIL**: The marked answer is BJJ-incorrect or mechanically inaccurate, OR at least one distractor describes something nonsensical that no trained practitioner would recognize as a real BJJ concept.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

**Marked answer**: {answer}

## Instructions

Apply BJJ domain knowledge. Assess: (1) Is the marked answer factually correct? Is the physical mechanism accurate? (2) Are the distractors based on real BJJ concepts, even if they are wrong in this context?

Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences. If failed, identify what is BJJ-incorrect or nonsensical."
}
```
