"""DeepEval quality gate for BJJ-VQA questions.

Run with:  deepeval test run evals/

Requires OPENROUTER_API_KEY to be set.
"""

import json
import os
import sys
from pathlib import Path

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, SingleTurnParams
from openai import OpenAI

# ---------------------------------------------------------------------------
# Custom LLM: OpenRouter via OpenAI-compatible client
# ---------------------------------------------------------------------------


class OpenRouterModel(DeepEvalBaseLLM):
    """OpenRouter model wrapper for DeepEval evaluations."""

    def __init__(self, model_name: str = "google/gemma-4-31b-it"):
        self._model_name = model_name
        self._client: OpenAI | None = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENROUTER_API_KEY"],
            )
        return self._client

    def load_model(self):  # noqa: ANN201 — DeepEval expects this
        return self

    def generate(self, prompt: str) -> str:  # noqa: ANN201
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self._model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content or ""

    async def a_generate(self, prompt: str) -> str:  # noqa: ANN201
        return self.generate(prompt)

    def get_model_name(self) -> str:
        return f"openrouter/{self._model_name}"


def _make_judge() -> OpenRouterModel:
    """Create the judge model. Raises if OPENROUTER_API_KEY is not set."""
    if "OPENROUTER_API_KEY" not in os.environ:
        print(
            "ERROR: OPENROUTER_API_KEY is required for quality evals.",
            file=sys.stderr,
        )
        sys.exit(1)
    return OpenRouterModel()


_JUDGE: OpenRouterModel | None = None

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
# Load questions from data/samples.json
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parent.parent
_SAMPLES_PATH = _PROJECT_ROOT / "data" / "samples.json"


def _load_questions() -> list[dict]:
    """Load questions from the dataset."""
    with _SAMPLES_PATH.open() as f:
        return json.load(f)


def _format_question(q: dict) -> str:
    """Format a question for evaluation."""
    choices_str = "\n".join(
        f"{letter}) {choice}" for letter, choice in zip("ABCD", q["choices"])
    )
    return f"Question: {q['question']}\nOptions:\n{choices_str}\nAnswer: {q['answer']}"


# ---------------------------------------------------------------------------
# Test functions
# ---------------------------------------------------------------------------

_questions = _load_questions()


def _make_test_case(question: dict, criterion_name: str) -> LLMTestCase:
    """Create an LLMTestCase for a single question and criterion."""
    question_text = _format_question(question)

    return LLMTestCase(
        input=f"Criterion: {criterion_name}\n{question_text}",
        actual_output=question_text,
    )


def _make_metric(criterion_name: str) -> GEval:
    """Create a GEval metric for a given criterion."""
    global _JUDGE
    if _JUDGE is None:
        _JUDGE = _make_judge()
    return GEval(
        name=criterion_name,
        criteria=CRITERIA[criterion_name],
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
        ],
        model=_JUDGE,
        threshold=0.5,
    )


# Limit to first 3 questions to keep CI runs reasonable
_TEST_QUESTIONS = _questions[:3]


def test_stem_leak() -> None:
    """Evaluate STEM_LEAK criterion on sample questions."""
    metric = _make_metric("STEM_LEAK")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "STEM_LEAK"), [metric])


def test_role_coherence() -> None:
    """Evaluate ROLE_COHERENCE criterion on sample questions."""
    metric = _make_metric("ROLE_COHERENCE")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "ROLE_COHERENCE"), [metric])


def test_single_correct() -> None:
    """Evaluate SINGLE_CORRECT criterion on sample questions."""
    metric = _make_metric("SINGLE_CORRECT")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "SINGLE_CORRECT"), [metric])


def test_image_dependency() -> None:
    """Evaluate IMAGE_DEPENDENCY criterion on sample questions."""
    metric = _make_metric("IMAGE_DEPENDENCY")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "IMAGE_DEPENDENCY"), [metric])


def test_image_clarity() -> None:
    """Evaluate IMAGE_CLARITY criterion on sample questions."""
    metric = _make_metric("IMAGE_CLARITY")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "IMAGE_CLARITY"), [metric])


def test_bjj_correctness() -> None:
    """Evaluate BJJ_CORRECTNESS criterion on sample questions."""
    metric = _make_metric("BJJ_CORRECTNESS")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "BJJ_CORRECTNESS"), [metric])


def test_format_compliance() -> None:
    """Evaluate FORMAT_COMPLIANCE criterion on sample questions."""
    metric = _make_metric("FORMAT_COMPLIANCE")
    for q in _TEST_QUESTIONS:
        assert_test(_make_test_case(q, "FORMAT_COMPLIANCE"), [metric])
