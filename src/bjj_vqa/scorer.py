"""Custom scorer for models that return structured responses."""

import re

from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState


@scorer(metrics=[accuracy(), stderr()])
def choice_robust() -> scorer:
    """Robust choice scorer that handles various response formats.

    Handles:
    - Plain text: "B" or "ANSWER: B"
    - List format: [{'type': 'text', 'text': 'B'}] (Gemini via OpenRouter)
    - With reasoning: [{'type': 'reasoning'}, {'type': 'text', 'text': 'B'}]
    """

    async def score(state: TaskState, target: Target) -> Score:
        # Get output content
        output = state.output

        # Handle different content formats
        response = ""

        if hasattr(output, "completion"):
            content = output.completion
        elif hasattr(output, "choices") and output.choices:
            # Get first choice's message content
            msg = output.choices[0].message
            content = msg.content if hasattr(msg, "content") else ""
        else:
            content = str(output)

        # Handle list format (Gemini via OpenRouter)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    response = item.get("text", "")
                    break
        elif isinstance(content, str):
            response = content

        # Extract letter from response
        # Patterns: "B", "ANSWER: B", "The answer is B", "**B**", etc.
        response = response.strip()

        # Try direct match first (single letter)
        if response in ["A", "B", "C", "D"]:
            answer = response
        else:
            # Extract letter from text
            match = re.search(r"\b([A-D])\b", response)
            answer = match.group(1) if match else ""

        # Compare with target
        target_text = (
            target.text.strip() if hasattr(target, "text") else str(target).strip()
        )
        correct = answer == target_text

        return Score(
            value=1.0 if correct else 0.0,
            answer=answer,
            explanation=response,
        )

    return score
