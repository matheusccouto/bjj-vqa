"""Tests for BJJ-VQA task module."""

import pytest

from bjj_vqa.task import record_to_sample


@pytest.fixture
def sample_record():
    """Minimal valid sample record for testing."""
    return {
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


def test_record_to_sample(sample_record):
    """Test basic conversion with all fields."""
    sample = record_to_sample(sample_record)

    assert sample.id == "00000"
    assert sample.target == "B"
    assert sample.choices == ["Option A", "Option B", "Option C", "Option D"]

    metadata = sample.metadata
    assert metadata is not None
    assert metadata["experience_level"] == "beginner"
    assert metadata["category"] == "gi"
    assert metadata["subject"] == "guard"
    assert metadata["source"] == "https://youtube.com/watch?v=test&t=60s"


def test_input_format(sample_record):
    """Test multimodal input has image and text."""
    sample = record_to_sample(sample_record)

    assert len(sample.input) == 1
    msg = sample.input[0]
    content = msg.content  # ty: ignore[unresolved-attribute]
    assert isinstance(content, list)
    assert content[0].type == "image"
    assert content[1].type == "text"
    assert content[1].text == "What technique is this?"  # ty: ignore[unresolved-attribute]


def test_missing_fields_raises_keyerror():
    """Test that missing required fields raise KeyError."""
    record = {
        "id": "00000",
        "image": "images/test.jpg",
        "question": "Minimal?",
        "answer": "A",
    }

    with pytest.raises(KeyError):
        record_to_sample(record)


def test_list_image_input_format():
    """Test that list-image records produce interleaved label+image content."""
    record = {
        "id": "00001",
        "image": ["images/00001_a.jpg", "images/00001_b.jpg"],
        "question": "Which position is correct?",
        "choices": ["Image A", "Image B"],
        "answer": "B",
        "experience_level": "advanced",
        "category": "no_gi",
        "subject": "controls",
        "source": "course/01",
    }
    sample = record_to_sample(record)

    content = sample.input[0].content  # ty: ignore[unresolved-attribute]
    assert isinstance(content, list)
    expected_len = len(record["image"]) * 2 + 1  # label+image per option, then question
    assert len(content) == expected_len
    assert content[0].type == "text"
    assert content[0].text == "Image A:"  # ty: ignore[unresolved-attribute]
    assert content[1].type == "image"
    assert content[2].type == "text"
    assert content[2].text == "Image B:"  # ty: ignore[unresolved-attribute]
    assert content[3].type == "image"
    assert content[4].type == "text"
    assert content[4].text == "Which position is correct?"  # ty: ignore[unresolved-attribute]
