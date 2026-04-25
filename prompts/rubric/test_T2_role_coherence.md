# T2 ROLE_COHERENCE

You are evaluating a multiple-choice question for a Brazilian Jiu-Jitsu visual benchmark. You will be shown the image and the question options.

## Test definition

**PASS**: Every option is internally consistent with the scenario visible in the image — correct attacker/defender roles, correct position, plausible within the context shown.

**FAIL**: At least one option is trivially wrong because it confuses attacker/defender roles, references a completely different position than what is shown, or is incoherent given what is visible in the image. A trivially wrong option is not a good distractor — it is detectable as wrong without domain knowledge, merely by matching roles or position.

## Question to evaluate

**Stem**: {stem}

**Options**:
A) {option_a}
B) {option_b}
C) {option_c}
D) {option_d}

**Marked answer**: {answer}

## Instructions

Examine the image carefully. For each option, assess whether it is internally consistent with the visible scenario (roles, position, context). A wrong answer is acceptable if it requires BJJ knowledge to reject. A wrong answer is NOT acceptable if it is trivially inconsistent with the image (e.g., describes the top player's action when the image shows the bottom player's perspective as the focus).

Respond with a JSON object:

```json
{
  "passed": true or false,
  "rationale": "One or two sentences identifying any role/position incoherence found, or confirming all options are consistent."
}
```
