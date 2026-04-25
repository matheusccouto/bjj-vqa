"""Tests for the adversarial rubric."""

from unittest.mock import MagicMock, patch

from anthropic.types import TextBlock

from bjj_vqa.rubric import (
    RubricResult,
    RubricTestResult,
    _check_t7_format,
    _parse_llm_response,
)
from bjj_vqa.schema import SampleRecord


def _make_sample(**kwargs) -> SampleRecord:
    base = {
        "id": "00001",
        "image": "images/00001.jpg",
        "question": "When your opponent reacts by posting their hand, you finish by",
        "choices": [
            "driving your knee into their hip",
            "switching your angle to attack the omoplata",
            "pulling their sleeve across your body",
            "flattening them with your chest pressure",
        ],
        "answer": "A",
        "experience_level": "intermediate",
        "category": "gi",
        "subject": "submissions",
        "source": "https://youtube.com/watch?v=test&t=83s",
    }
    base.update(kwargs)
    return SampleRecord.model_validate(base)


class TestT7FormatCheck:
    """T7 is deterministic — no LLM call needed."""

    def test_passes_clean_question(self):
        sample = _make_sample()
        result = _check_t7_format(sample)
        assert result.test == "T7_FORMAT_COMPLIANCE"
        assert result.passed

    def test_fails_when_correct_is_longest(self):
        sample = _make_sample(
            choices=[
                "short",
                "this is the long correct answer with many extra words"
                " added to make it the longest option of all four",
                "medium length here",
                "also short",
            ],
            answer="B",
        )
        result = _check_t7_format(sample)
        assert not result.passed
        assert "longest" in result.rationale.lower()

    def test_fails_on_hedge_word_usually(self):
        sample = _make_sample(
            choices=[
                "driving your knee into their hip",
                "usually switching your angle works best",
                "pulling their sleeve across your body",
                "flattening them with your chest pressure",
            ],
            answer="A",
        )
        result = _check_t7_format(sample)
        assert not result.passed
        assert "usually" in result.rationale.lower()

    def test_fails_on_hedge_word_sometimes(self):
        sample = _make_sample(
            choices=[
                "sometimes works with pressure",
                "switching your angle",
                "pulling their sleeve",
                "flattening with chest",
            ],
            answer="B",
        )
        result = _check_t7_format(sample)
        assert not result.passed

    def test_fails_on_contrast_word_but(self):
        sample = _make_sample(
            choices=[
                "driving your knee into their hip",
                "switching angle but only from here",
                "pulling their sleeve across",
                "flattening with pressure",
            ],
            answer="A",
        )
        result = _check_t7_format(sample)
        assert not result.passed
        assert "but" in result.rationale.lower()

    def test_fails_on_contrast_word_although(self):
        sample = _make_sample(
            choices=[
                "driving your knee",
                "switching although risky",
                "pulling their sleeve",
                "flattening with chest",
            ],
            answer="A",
        )
        result = _check_t7_format(sample)
        assert not result.passed

    def test_fails_on_contrast_word_however(self):
        sample = _make_sample(
            choices=[
                "driving however carefully",
                "switching your angle",
                "pulling their sleeve",
                "flattening with chest",
            ],
            answer="B",
        )
        result = _check_t7_format(sample)
        assert not result.passed

    def test_fails_very_unequal_lengths(self):
        sample = _make_sample(
            choices=[
                "a",
                "switching your angle to attack the omoplata position"
                " effectively using hip rotation",
                "medium",
                "also short",
            ],
            answer="B",
        )
        result = _check_t7_format(sample)
        assert not result.passed

    def test_rationale_nonempty_on_pass(self):
        sample = _make_sample()
        result = _check_t7_format(sample)
        assert result.rationale


class TestParseLlmResponse:
    """Tests for parsing LLM JSON responses."""

    def test_parses_pass(self):
        text = '{"passed": true, "rationale": "No stem leak detected."}'
        result = _parse_llm_response("T1_STEM_LEAK", text)
        assert result.passed
        assert result.rationale == "No stem leak detected."

    def test_parses_fail(self):
        text = '{"passed": false, "rationale": "Option C eliminable from text."}'
        result = _parse_llm_response("T1_STEM_LEAK", text)
        assert not result.passed

    def test_parses_json_in_markdown_block(self):
        text = 'Some preamble.\n```json\n{"passed": true, "rationale": "OK"}\n```'
        result = _parse_llm_response("T1_STEM_LEAK", text)
        assert result.passed

    def test_falls_back_to_fail_on_unparseable(self):
        result = _parse_llm_response("T1_STEM_LEAK", "Sorry, I cannot evaluate this.")
        assert not result.passed
        assert "Could not parse" in result.rationale

    def test_test_id_set_correctly(self):
        text = '{"passed": true, "rationale": "Fine."}'
        result = _parse_llm_response("T4_IMAGE_DEPENDENCY", text)
        assert result.test == "T4_IMAGE_DEPENDENCY"


class TestRubricReview:
    """Tests for the review() function with mocked Anthropic responses."""

    def _mock_response(
        self,
        *,
        passed: bool,
        rationale: str = "Looks good.",
    ) -> MagicMock:
        content_block = MagicMock(spec=TextBlock)
        content_block.text = (
            f'{{"passed": {str(passed).lower()}, "rationale": "{rationale}"}}'
        )
        response = MagicMock()
        response.content = [content_block]
        return response

    @patch("bjj_vqa.rubric._get_client")
    def test_all_pass_returns_pass_verdict(self, mock_get_client, tmp_path):
        sample = _make_sample()
        image_path = tmp_path / "00001.jpg"
        image_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response(passed=True)

        from bjj_vqa.rubric import review

        result = review(sample, image_path)
        assert result.verdict == "PASS"
        assert all(t.passed for t in result.tests)

    @patch("bjj_vqa.rubric._get_client")
    def test_t1_fail_returns_reject(self, mock_get_client, tmp_path):
        sample = _make_sample()
        image_path = tmp_path / "00001.jpg"
        image_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        def side_effect(**kwargs):
            messages = kwargs.get("messages", [])
            if messages:
                content = messages[0].get("content", [])
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block["text"]
                        t1_cues = ("T1_STEM_LEAK", "STEM_LEAK", "stem leak")
                        if any(c in text or c.lower() in text.lower() for c in t1_cues):
                            return self._mock_response(
                                passed=False,
                                rationale="Stem leaks scenario.",
                            )
            return self._mock_response(passed=True)

        mock_client.messages.create.side_effect = side_effect

        from bjj_vqa.rubric import review

        result = review(sample, image_path)
        assert result.verdict in ("REJECT", "REWRITE")

    @patch("bjj_vqa.rubric._get_client")
    def test_result_has_seven_tests(self, mock_get_client, tmp_path):
        sample = _make_sample()
        image_path = tmp_path / "00001.jpg"
        image_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response(passed=True)

        from bjj_vqa.rubric import review

        result = review(sample, image_path)
        expected_test_count = 7
        assert len(result.tests) == expected_test_count

    @patch("bjj_vqa.rubric._get_client")
    def test_to_markdown_contains_verdict(self, mock_get_client, tmp_path):
        sample = _make_sample()
        image_path = tmp_path / "00001.jpg"
        image_path.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.messages.create.return_value = self._mock_response(passed=True)

        from bjj_vqa.rubric import review

        result = review(sample, image_path)
        md = result.to_markdown()
        assert result.verdict in md
        assert sample.id in md


class TestRubricResult:
    """Tests for RubricResult model."""

    def test_verdict_pass(self):
        result = RubricResult(
            question_id="00001",
            tests=[
                RubricTestResult(test=f"T{i}", passed=True, rationale="ok")
                for i in range(1, 8)
            ],
            verdict="PASS",
        )
        assert result.verdict == "PASS"

    def test_to_markdown_structure(self):
        result = RubricResult(
            question_id="00001",
            tests=[
                RubricTestResult(
                    test="T1_STEM_LEAK",
                    passed=True,
                    rationale="No leak.",
                ),
                RubricTestResult(
                    test="T7_FORMAT_COMPLIANCE",
                    passed=False,
                    rationale="Too long.",
                ),
            ],
            verdict="REWRITE",
        )
        md = result.to_markdown()
        assert "00001" in md
        assert "REWRITE" in md
        assert "PASS" in md
        assert "FAIL" in md
