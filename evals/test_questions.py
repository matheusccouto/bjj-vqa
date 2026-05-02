"""DeepEval quality gate for BJJ-VQA questions.

Run with:  deepeval test run evals/

Requires OPENROUTER_API_KEY to be set.
"""

import json
import os
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import OpenRouterModel
from deepeval.test_case import LLMTestCase, SingleTurnParams

# ---------------------------------------------------------------------------
# Quality criteria from CONTEXT.md
# ---------------------------------------------------------------------------

CRITERIA = {
    "STEM_LEAK": (
        "Evaluate whether the question stem leaks the answer. "
        "The stem must NOT name the scenario, position, or technique. "
        "A practitioner reading only the stem and options (without seeing the image) "
        "should be able to eliminate at most ONE option from stem text alone. "
        "If they can eliminate two or more, the question FAILS. "
        "Score 1 if the stem does not reveal the scenario. Score 0 if it does."
    ),
    "ROLE_COHERENCE": (
        "Evaluate whether every option is internally consistent with the scenario. "
        "Each of the four choices must be a plausible BJJ concept — not nonsense. "
        "Score 1 if all options are coherent BJJ concepts. Score 0 if any are not."
    ),
    "SINGLE_CORRECT": (
        "Evaluate whether the marked answer is the only defensible answer. "
        "Given the question stem and options, there should be exactly one correct answer. "
        "Score 1 if only the marked answer is defensible. Score 0 if multiple answers could work."
    ),
    "IMAGE_DEPENDENCY": (
        "Evaluate whether answering requires the image. "
        "The question must require a specific visual fact from the image to answer. "
        "If the question can be answered from BJJ knowledge alone without the image, it FAILS. "
        "Score 1 if the image is required. Score 0 if the question is solvable from text alone."
    ),
    "IMAGE_CLARITY": (
        "Evaluate whether a human BJJ practitioner could confirm what the stem implies. "
        "Given the image, a practitioner should be able to confirm the situation described "
        "in the question stem. Score 1 if the scenario is visually confirmable. Score 0 if not."
    ),
    "BJJ_CORRECTNESS": (
        "Evaluate whether the marked answer is BJJ-correct and distractors are based on real concepts. "
        "The correct answer must be technically accurate per Brazilian Jiu-Jitsu principles. "
        "Distractors must be plausible to someone who trains (WRONG-CONTEXT, WRONG-MECHANISM, "
        "or WRONG-DIRECTION types). Score 1 if BJJ-correct. Score 0 if technically wrong."
    ),
    "FORMAT_COMPLIANCE": (
        "Evaluate format compliance: options must be similar in length, "
        "the correct answer must not be the longest option, "
        "and options must not contain hedge words (usually, sometimes) "
        "or contrast words (but, although, however). "
        "Score 1 if all format rules are met. Score 0 if any are violated."
    ),
}

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parent.parent
_SAMPLES_PATH = _PROJECT_ROOT / "data" / "samples.json"


@pytest.fixture(scope="module")
def questions() -> list[dict]:
    """Load questions from the dataset."""
    with _SAMPLES_PATH.open() as f:
        return json.load(f)


@pytest.fixture(scope="module")
def sample_questions(questions: list[dict]) -> list[dict]:
    """Limit to first 3 questions to keep CI runs reasonable."""
    return questions[:3]


@pytest.fixture(scope="module")
def judge() -> OpenRouterModel:
    """Create the OpenRouter judge model."""
    if "OPENROUTER_API_KEY" not in os.environ:
        pytest.skip("OPENROUTER_API_KEY is not set")
    return OpenRouterModel(model="google/gemma-4-31b-it")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_question(q: dict) -> str:
    """Format a question for evaluation."""
    choices = "\n".join(
        f"{letter}) {choice}" for letter, choice in zip("ABCD", q["choices"], strict=False)
    )
    return f"Question: {q['question']}\nOptions:\n{choices}\nAnswer: {q['answer']}"


def _make_metric(criterion: str, judge: OpenRouterModel) -> GEval:
    """Create a GEval metric for a criterion."""
    return GEval(
        name=criterion,
        criteria=CRITERIA[criterion],
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        model=judge,
        threshold=0.5,
    )


def _make_test_case(q: dict, criterion: str) -> LLMTestCase:
    """Create an LLMTestCase for a question and criterion."""
    text = _format_question(q)
    return LLMTestCase(
        input=f"Criterion: {criterion}\n{text}",
        actual_output=text,
    )


# ---------------------------------------------------------------------------
# Parametrized tests — each question evaluated against all criteria
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("criterion", list(CRITERIA))
def test_question_quality(criterion: str, sample_questions: list[dict], judge: OpenRouterModel) -> None:
    """Evaluate each sample question against all quality criteria."""
    metric = _make_metric(criterion, judge)
    for q in sample_questions:
        assert_test(_make_test_case(q, criterion), [metric])
