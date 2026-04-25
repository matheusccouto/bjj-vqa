"""Seven-criterion adversarial rubric for BJJ-VQA question quality."""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal

import anthropic
from anthropic.types import TextBlock
from pydantic import BaseModel

from bjj_vqa.schema import SampleRecord

_PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "rubric"
_HEDGE_WORDS = re.compile(
    r"\b(usually|sometimes|often|occasionally|generally|typically|might|may)\b",
    re.IGNORECASE,
)
_CONTRAST_WORDS = re.compile(
    r"\b(but|although|however|though|yet|while|whereas)\b",
    re.IGNORECASE,
)

Verdict = Literal["PASS", "REWRITE", "REJECT"]


class RubricTestResult(BaseModel):
    """Result for a single rubric criterion."""

    test: str
    passed: bool
    rationale: str


class RubricResult(BaseModel):
    """Aggregated result of all seven rubric criteria."""

    question_id: str
    tests: list[RubricTestResult]
    verdict: Verdict

    def to_markdown(self) -> str:
        """Format result as a Markdown report."""
        lines = [f"### Rubric: {self.question_id} — {self.verdict}\n"]
        for t in self.tests:
            icon = "PASS" if t.passed else "FAIL"
            lines.append(f"**{t.test}**: {icon}")
            lines.append(f"  {t.rationale}\n")
        return "\n".join(lines)


def review(question: SampleRecord, image_path: Path) -> RubricResult:
    """Run all seven rubric criteria against a question and its image."""
    client = _get_client()
    image_b64 = _encode_image(image_path)

    options = question.choices
    option_map = {
        letter: options[i] if i < len(options) else ""
        for i, letter in enumerate("ABCD")
    }

    template_vars = {
        "stem": question.question,
        "option_a": option_map["A"],
        "option_b": option_map["B"],
        "option_c": option_map["C"],
        "option_d": option_map["D"],
        "answer": question.answer,
    }

    tests: list[RubricTestResult] = []

    # T1: stem leak (text-only, no image)
    t1 = _run_llm_test(
        "T1_STEM_LEAK",
        "test_T1_stem_leak.md",
        template_vars,
        client,
        image_b64=None,
    )
    tests.append(t1)

    # T2-T3, T5-T6: LLM-judged with image
    for test_id, filename in [
        ("T2_ROLE_COHERENCE", "test_T2_role_coherence.md"),
        ("T3_SINGLE_CORRECT", "test_T3_single_correct.md"),
        ("T5_IMAGE_CLARITY", "test_T5_image_clarity.md"),
        ("T6_BJJ_CORRECTNESS", "test_T6_bjj_correctness.md"),
    ]:
        result = _run_llm_test(
            test_id,
            filename,
            template_vars,
            client,
            image_b64=image_b64,
        )
        tests.append(result)

    # T4: image dependency (text-only reasoning about whether image is needed)
    t4 = _run_llm_test(
        "T4_IMAGE_DEPENDENCY",
        "test_T4_image_dependency.md",
        template_vars,
        client,
        image_b64=None,
    )
    tests.append(t4)

    # T7: pure Python format check
    t7 = _check_t7_format(question)
    tests.append(t7)

    # Reorder to T1-T7
    ordered = {t.test.split("_")[0]: t for t in tests}
    tests_ordered = [
        ordered.get("T1", tests[0]),
        ordered.get("T2", tests[1]),
        ordered.get("T3", tests[2]),
        ordered.get("T4", tests[5]),
        ordered.get("T5", tests[3]),
        ordered.get("T6", tests[4]),
        ordered.get("T7", tests[6]),
    ]

    all_pass = all(t.passed for t in tests_ordered)
    any_fail = any(not t.passed for t in tests_ordered)

    if all_pass:
        verdict: Verdict = "PASS"
    elif any_fail:
        # T1, T4 failures are REJECT; others are REWRITE
        reject_tests = {"T1_STEM_LEAK", "T4_IMAGE_DEPENDENCY"}
        hard_fail = any(not t.passed and t.test in reject_tests for t in tests_ordered)
        verdict = "REJECT" if hard_fail else "REWRITE"
    else:
        verdict = "PASS"

    return RubricResult(question_id=question.id, tests=tests_ordered, verdict=verdict)


def _get_client() -> anthropic.Anthropic:
    """Return an Anthropic client, exiting with a clear error if key is missing."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY is required for the rubric command")
        print("Hint: Set it in your shell or .env file")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def _encode_image(path: Path) -> str:
    """Return base64-encoded JPEG image."""
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def _load_prompt(filename: str, variables: dict[str, str]) -> str:
    """Load a rubric prompt template and substitute variables."""
    template = (_PROMPTS_DIR / filename).read_text()
    for key, value in variables.items():
        template = template.replace("{" + key + "}", value)
    return template


def _run_llm_test(
    test_id: str,
    prompt_filename: str,
    template_vars: dict[str, str],
    client: anthropic.Anthropic,
    *,
    image_b64: str | None,
) -> RubricTestResult:
    """Run a single LLM-based rubric test."""
    prompt = _load_prompt(prompt_filename, template_vars)

    content: list[Any] = []
    if image_b64 is not None:
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_b64,
                },
            },
        )
    content.append({"type": "text", "text": prompt})

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=512,
        messages=[{"role": "user", "content": content}],
    )

    first = response.content[0] if response.content else None
    text = first.text if isinstance(first, TextBlock) else ""
    return _parse_llm_response(test_id, text)


def _parse_llm_response(test_id: str, text: str) -> RubricTestResult:
    """Parse JSON from LLM response into a RubricTestResult."""
    # Extract JSON block from response
    json_match = re.search(r"\{[^{}]*\"passed\"[^{}]*\}", text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return RubricTestResult(
                test=test_id,
                passed=bool(data.get("passed", False)),
                rationale=str(data.get("rationale", "No rationale provided.")),
            )
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback: conservative fail if we cannot parse
    return RubricTestResult(
        test=test_id,
        passed=False,
        rationale=f"Could not parse LLM response. Raw: {text[:200]}",
    )


def _check_t7_format(question: SampleRecord) -> RubricTestResult:
    """T7 FORMAT_COMPLIANCE: pure Python string checks, no LLM call."""
    options = question.choices
    if len(options) != 4:  # noqa: PLR2004
        return RubricTestResult(
            test="T7_FORMAT_COMPLIANCE",
            passed=False,
            rationale=f"Expected 4 options, got {len(options)}.",
        )

    answer_index = ord(question.answer) - ord("A")
    correct_text = options[answer_index]
    max_len = max(len(o) for o in options)

    failures: list[str] = []

    if len(correct_text) == max_len and options.count(correct_text) == 1:
        failures.append("Correct answer is the longest option.")

    lengths = [len(o) for o in options]
    min_len = min(lengths)
    if max_len > min_len * 2:
        failures.append(
            f"Options have very unequal lengths (min={min_len}, max={max_len}).",
        )

    for i, opt in enumerate(options):
        letter = chr(ord("A") + i)
        if m := _HEDGE_WORDS.search(opt):
            failures.append(f"Option {letter} contains hedge word '{m.group()}'.")
        if m := _CONTRAST_WORDS.search(opt):
            failures.append(f"Option {letter} contains contrast word '{m.group()}'.")

    if failures:
        return RubricTestResult(
            test="T7_FORMAT_COMPLIANCE",
            passed=False,
            rationale=" ".join(failures),
        )

    return RubricTestResult(
        test="T7_FORMAT_COMPLIANCE",
        passed=True,
        rationale=(
            "Options have similar lengths, correct answer is not the longest,"
            " no hedge or contrast words."
        ),
    )
