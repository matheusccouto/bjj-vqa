"""Tests for BJJ-VQA schema validation."""

import pytest
from pydantic import ValidationError

from bjj_vqa.generate import GeneratedQuestion
from bjj_vqa.schema import SampleRecord


def _sample(**overrides):
    """Build a valid SampleRecord dict, overriding any fields."""
    base = {
        "id": "00001",
        "image": "images/00001.jpg",
        "question": "What technique is this?",
        "choices": ["A", "B", "C", "D"],
        "answer": "A",
        "experience_level": "beginner",
        "category": "gi",
        "subject": "guard",
        "source": "https://youtube.com/watch?v=test",
        "timestamp": 0,
    }
    base.update(overrides)
    return base


def test_valid_sample():
    """A minimal valid record parses successfully."""
    assert SampleRecord.model_validate(_sample()).id == "00001"


@pytest.mark.parametrize(
    ("field", "bad_val"),
    [("experience_level", "expert"), ("category", "both"), ("subject", "sweeps")],
)
def test_rejects_invalid_enum(field, bad_val):
    """Invalid enum values are rejected by the schema."""
    with pytest.raises(ValidationError):
        SampleRecord.model_validate(_sample(**{field: bad_val}))


def test_rejects_bad_choice_counts():
    """Too few, too many, or empty choices are rejected."""
    for choices in [["A"], ["A", "B", "C", "D", "E"], []]:
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(_sample(choices=choices))


def test_rejects_answer_beyond_choices():
    """Answer letter beyond the number of choices is rejected."""
    with pytest.raises(ValidationError):
        SampleRecord.model_validate(_sample(choices=["A", "B"], answer="C"))


def test_image_as_list():
    """A record with a list of image paths parses correctly."""
    record = _sample(
        image=["images/a.jpg", "images/b.jpg"],
        choices=["Image A", "Image B"],
        answer="B",
    )
    sample = SampleRecord.model_validate(record)
    assert isinstance(sample.image, list)


def test_generated_question_requires_4_choices():
    """GeneratedQuestion rejects fewer than 4 choices."""
    with pytest.raises(ValidationError):
        GeneratedQuestion(
            question="Test?",
            choices=["A", "B"],
            answer="A",
            experience_level="beginner",
            category="gi",
            subject="guard",
            source="https://youtube.com/watch?v=test&t=42s",
            timestamp=42,
        )
