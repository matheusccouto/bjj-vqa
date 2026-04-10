"""Tests for BJJ-VQA schema validation."""

import pytest
from pydantic import ValidationError

from bjj_vqa.schema import SampleRecord


class TestValidSample:
    """Tests for valid sample records."""

    def test_minimal_valid_sample(self):
        """Minimal valid sample with all required fields."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "What technique is this?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test&t=60s",
        }
        sample = SampleRecord.model_validate(record)
        assert sample.id == "00001"
        assert sample.answer == "A"

    def test_all_experience_levels(self):
        """All valid experience levels."""
        for level in ["beginner", "intermediate", "advanced"]:
            record = {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "Test?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": level,
                "category": "gi",
                "subject": "guard",
                "source": "https://youtube.com/watch?v=test",
            }
            sample = SampleRecord.model_validate(record)
            assert sample.experience_level == level

    def test_all_categories(self):
        """All valid categories."""
        for cat in ["gi", "no_gi"]:
            record = {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "Test?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": "beginner",
                "category": cat,
                "subject": "guard",
                "source": "https://youtube.com/watch?v=test",
            }
            sample = SampleRecord.model_validate(record)
            assert sample.category == cat

    def test_all_subjects(self):
        """All valid subjects."""
        for subj in ["guard", "passing", "submissions", "controls", "escapes", "takedowns"]:
            record = {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "Test?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": "beginner",
                "category": "gi",
                "subject": subj,
                "source": "https://youtube.com/watch?v=test",
            }
            sample = SampleRecord.model_validate(record)
            assert sample.subject == subj

    def test_all_answers(self):
        """All valid answer letters."""
        for ans in ["A", "B", "C", "D"]:
            record = {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "Test?",
                "choices": ["A", "B", "C", "D"],
                "answer": ans,
                "experience_level": "beginner",
                "category": "gi",
                "subject": "guard",
                "source": "https://youtube.com/watch?v=test",
            }
            sample = SampleRecord.model_validate(record)
            assert sample.answer == ans


class TestInvalidSample:
    """Tests for invalid sample records."""

    def test_missing_id(self):
        """Missing required id field."""
        record = {
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_missing_question(self):
        """Missing required question field."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_invalid_experience_level(self):
        """Invalid experience_level value."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "expert",  # Invalid
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_invalid_category(self):
        """Invalid category value."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "both",  # Invalid
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_invalid_subject(self):
        """Invalid subject value."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "sweeps",  # Invalid
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_invalid_answer(self):
        """Invalid answer letter."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "E",  # Invalid
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_wrong_choice_count_too_many(self):
        """More than 4 choices."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D", "E"],  # 5 choices
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_wrong_choice_count_too_few(self):
        """Less than 4 choices."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C"],  # 3 choices
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_empty_choices(self):
        """Empty choices list."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": [],  # Empty
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)