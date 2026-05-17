"""Tests for BJJ-VQA task module."""

import pytest

from bjj_vqa.task import record_to_sample

RECORD = {
    "id": "00000",
    "image": "images/test.jpg",
    "question": "What technique is this?",
    "choices": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "B",
    "experience_level": "beginner",
    "category": "gi",
    "subject": "guard",
    "source": "https://youtube.com/watch?v=test&t=60s",
}


def test_record_to_sample():
    """record_to_sample preserves id, target, choices, and metadata."""
    sample = record_to_sample(RECORD)
    assert sample.id == "00000"
    assert sample.target == "B"
    assert sample.choices == ["Option A", "Option B", "Option C", "Option D"]
    metadata = sample.metadata
    assert metadata["experience_level"] == "beginner"
    assert metadata["category"] == "gi"
    assert metadata["subject"] == "guard"


def test_input_format():
    """Output contains interleaved image and text content."""
    sample = record_to_sample(RECORD)
    content = sample.input[0].content  # ty: ignore[unresolved-attribute]
    assert isinstance(content, list)
    assert content[0].type == "image"
    assert content[1].type == "text"
    assert content[1].text == "What technique is this?"  # ty: ignore[unresolved-attribute]


def test_missing_fields_raises_keyerror():
    """Missing required fields cause KeyError, not silent corruption."""
    with pytest.raises(KeyError):
        record_to_sample(
            {"id": "00000", "image": "images/test.jpg", "question": "?", "answer": "A"},
        )


def test_list_image_input_format():
    """Multi-image records produce interleaved label+image content."""
    record = {
        "id": "00001",
        "image": ["images/a.jpg", "images/b.jpg"],
        "question": "Which position?",
        "choices": ["Image A", "Image B"],
        "answer": "B",
        "experience_level": "advanced",
        "category": "no_gi",
        "subject": "controls",
        "source": "course/01",
    }
    sample = record_to_sample(record)
    content = sample.input[0].content  # ty: ignore[unresolved-attribute]
    assert len(content) == 5  # label+image per option, then question text
