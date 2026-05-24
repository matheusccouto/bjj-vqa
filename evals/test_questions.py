"""DeepEval quality gate for BJJ-VQA questions.

Each test evaluates one criterion against one question. Run the full
suite with:

    deepeval test run evals/ -m evals

Filter locally with pytest expressions:

    uv run pytest evals/ -m evals -k "STEM_LEAK"
    uv run pytest evals/ -m evals -k "00001"

Requires OPENROUTER_API_KEY to be set.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, MLLMImage, SingleTurnParams

from .multimodal_model import MultimodalOpenRouterModel

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SAMPLES_PATH = _PROJECT_ROOT / "data" / "samples.json"
_IMAGES_DIR = _PROJECT_ROOT / "data"

# ---------------------------------------------------------------------------
# Quality criteria — descriptions from CONTEXT.md "Quality evals" section
# ---------------------------------------------------------------------------

CRITERIA: dict[str, str] = {
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
        "Given the question stem, options, and image, there should be exactly one "
        "correct answer. Score 1 if only the marked answer is defensible. "
        "Score 0 if multiple answers could work."
    ),
    "IMAGE_DEPENDENCY": (
        "Evaluate whether answering requires the image. "
        "The question must require a specific visual fact from the image. "
        "If it can be answered from BJJ knowledge alone without the image, "
        "it FAILS. Score 1 if the image is required. Score 0 if the question "
        "is solvable from text alone."
    ),
    "IMAGE_CLARITY": (
        "Evaluate whether a human BJJ practitioner could confirm what "
        "the stem implies. Given the image, a practitioner should be able "
        "to confirm the situation. Score 1 if visually confirmable. Score 0 if not."
    ),
    "BJJ_CORRECTNESS": (
        "Evaluate whether the marked answer is BJJ-correct and distractors are "
        "based on real concepts. The correct answer must be technically accurate "
        "per Brazilian Jiu-Jitsu principles. Distractors must be plausible to "
        "someone who trains (WRONG-CONTEXT, WRONG-MECHANISM, or WRONG-DIRECTION "
        "types). Score 1 if BJJ-correct. Score 0 if technically wrong."
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
# Helpers
# ---------------------------------------------------------------------------


def _load_questions() -> list[dict]:
    """Load questions from the dataset."""
    with _SAMPLES_PATH.open() as f:
        return json.load(f)


def _format_question(q: dict) -> str:
    """Format a question for evaluation, including full answer text."""
    pairs = zip("ABCD", q["choices"], strict=False)
    choices = "\n".join(f"{ltr}) {ch}" for ltr, ch in pairs)
    answer_index = "ABCD".index(q["answer"])
    answer_text = q["choices"][answer_index]
    return f"Question: {q['question']}\nOptions:\n{choices}\nAnswer: {answer_text}"


def _image_for(q: dict) -> MLLMImage:
    """Resolve the image for a question as a local MLLMImage."""
    return MLLMImage(url=str(_IMAGES_DIR / q["image"]), local=True)


def _make_metric(criterion: str, model: MultimodalOpenRouterModel) -> GEval:
    """Create a GEval metric for the given criterion."""
    return GEval(
        name=criterion,
        criteria=CRITERIA[criterion],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        model=model,
        threshold=0.5,
    )


def _make_test_case(q: dict, criterion: str) -> LLMTestCase:
    """Create a multimodal LLMTestCase for a question and criterion."""
    text = _format_question(q)
    img = _image_for(q)
    return LLMTestCase(
        input=f"Criterion: {criterion}\n{text}\n{img}",
        actual_output=text,
        multimodal=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_QUESTIONS = _load_questions()
_QUESTION_IDS = [q["id"] for q in _QUESTIONS]


@pytest.fixture(scope="session")
def judge() -> MultimodalOpenRouterModel:
    """Create the multimodal OpenRouter judge model."""
    if "OPENROUTER_API_KEY" not in os.environ:
        pytest.fail("OPENROUTER_API_KEY is not set")
    return MultimodalOpenRouterModel(model="google/gemma-4-31b-it")


# ---------------------------------------------------------------------------
# Parametrized tests — one test per criterion x question
# ---------------------------------------------------------------------------


@pytest.mark.evals
@pytest.mark.parametrize("criterion", list(CRITERIA))
@pytest.mark.parametrize("question_id", _QUESTION_IDS)
def test_question_quality(
    criterion: str,
    question_id: str,
    judge: MultimodalOpenRouterModel,
) -> None:
    """Evaluate one criterion against one question."""
    q = next(q for q in _QUESTIONS if q["id"] == question_id)
    metric = _make_metric(criterion, judge)
    test_case = _make_test_case(q, criterion)
    assert_test(test_case, [metric])
