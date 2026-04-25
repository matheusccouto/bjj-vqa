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
        subjects = [
            "guard",
            "passing",
            "submissions",
            "controls",
            "escapes",
            "takedowns",
        ]
        for subj in subjects:
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
        """Less than 2 choices."""
        record = {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A"],  # 1 choice
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

    def test_answer_out_of_range(self):
        """Answer letter beyond the number of choices."""
        record = {
            "id": "00001",
            "image": ["images/00001_a.jpg", "images/00001_b.jpg"],
            "question": "Which image?",
            "choices": ["Image A", "Image B"],
            "answer": "C",  # Only A and B are valid
            "experience_level": "advanced",
            "category": "no_gi",
            "subject": "controls",
            "source": "course/01",
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)


class TestNewOptionalFields:
    """Tests for optional methodology metadata fields added in v0.3+."""

    def _base(self) -> dict:
        return {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "Test?",
            "choices": ["A", "B", "C", "D"],
            "answer": "B",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        }

    def test_existing_record_still_valid_without_new_fields(self):
        """Existing records without new fields remain valid."""
        sample = SampleRecord.model_validate(self._base())
        assert sample.stem_type is None
        assert sample.option_types is None
        assert sample.concept is None
        assert sample.source_license is None
        assert sample.is_unanswerable is False
        assert sample.language == "en"

    def test_stem_type_completion(self):
        """COMPLETION stem type accepted."""
        record = {**self._base(), "stem_type": "COMPLETION"}
        sample = SampleRecord.model_validate(record)
        assert sample.stem_type == "COMPLETION"

    def test_stem_type_classification(self):
        """CLASSIFICATION stem type accepted."""
        record = {**self._base(), "stem_type": "CLASSIFICATION"}
        sample = SampleRecord.model_validate(record)
        assert sample.stem_type == "CLASSIFICATION"

    def test_stem_type_invalid(self):
        """Invalid stem type rejected."""
        record = {**self._base(), "stem_type": "FILL_IN_THE_BLANK"}
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_option_types_valid(self):
        """Valid option_types with one CORRECT at answer key."""
        record = {
            **self._base(),
            "option_types": {
                "A": "WRONG_CONTEXT",
                "B": "CORRECT",
                "C": "WRONG_MECHANISM",
                "D": "WRONG_DIRECTION",
            },
        }
        sample = SampleRecord.model_validate(record)
        assert sample.option_types is not None
        assert sample.option_types["B"] == "CORRECT"

    def test_option_types_wrong_answer_key(self):
        """option_types with CORRECT at wrong key fails validation."""
        record = {
            **self._base(),
            "answer": "B",
            "option_types": {
                "A": "CORRECT",  # should be B
                "B": "WRONG_CONTEXT",
                "C": "WRONG_MECHANISM",
                "D": "WRONG_DIRECTION",
            },
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_option_types_two_correct_fails(self):
        """option_types with two CORRECT values fails validation."""
        record = {
            **self._base(),
            "option_types": {
                "A": "CORRECT",
                "B": "CORRECT",
                "C": "WRONG_MECHANISM",
                "D": "WRONG_DIRECTION",
            },
        }
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_concept_field(self):
        """Concept field accepted as free text."""
        concept = "When opponent posts hand, switch to omoplata."
        record = {**self._base(), "concept": concept}
        sample = SampleRecord.model_validate(record)
        assert sample.concept == concept

    def test_source_license_cc_by(self):
        """cc_by source license accepted."""
        record = {**self._base(), "source_license": "cc_by"}
        sample = SampleRecord.model_validate(record)
        assert sample.source_license == "cc_by"

    def test_source_license_invalid(self):
        """Invalid source license rejected."""
        record = {**self._base(), "source_license": "mit"}
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)

    def test_is_unanswerable_default_false(self):
        """is_unanswerable defaults to False."""
        sample = SampleRecord.model_validate(self._base())
        assert sample.is_unanswerable is False

    def test_is_unanswerable_true(self):
        """is_unanswerable=True accepted."""
        record = {**self._base(), "is_unanswerable": True}
        sample = SampleRecord.model_validate(record)
        assert sample.is_unanswerable is True

    def test_language_default_en(self):
        """Language defaults to 'en'."""
        sample = SampleRecord.model_validate(self._base())
        assert sample.language == "en"

    def test_language_pt_br(self):
        """pt-br language accepted."""
        record = {**self._base(), "language": "pt-br"}
        sample = SampleRecord.model_validate(record)
        assert sample.language == "pt-br"

    def test_language_invalid(self):
        """Invalid language code rejected."""
        record = {**self._base(), "language": "es"}
        with pytest.raises(ValidationError):
            SampleRecord.model_validate(record)


class TestSourceModel:
    """Tests for the Source model used in sources/registry.jsonl."""

    def test_valid_source(self):
        """Valid source entry passes validation."""
        from bjj_vqa.schema import Source

        raw = {
            "url": "https://youtube.com/watch?v=test123",
            "title": "Test Video",
            "creator": "Test Channel",
            "license_type": "cc_by",
            "permission_reference": None,
            "question_ids": ["00001", "00002"],
            "notes": "CC BY 4.0 verified",
        }
        source = Source.model_validate(raw)
        assert source.license_type == "cc_by"
        assert source.question_ids == ["00001", "00002"]

    def test_source_invalid_license(self):
        """Invalid license_type rejected."""
        from bjj_vqa.schema import Source

        raw = {
            "url": "https://youtube.com/watch?v=test",
            "title": "Test",
            "creator": "Test",
            "license_type": "cc_zero",
            "permission_reference": None,
            "question_ids": [],
            "notes": "",
        }
        with pytest.raises(ValidationError):
            Source.model_validate(raw)


class TestImageChoiceSample:
    """Tests for multi-image choice records (private benchmark format)."""

    def test_two_image_choices(self):
        """Valid record with two image options."""
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
        sample = SampleRecord.model_validate(record)
        assert sample.answer == "B"
        assert len(sample.choices) == len(record["choices"])
        assert isinstance(sample.image, list)

    def test_three_image_choices(self):
        """Valid record with three image options."""
        record = {
            "id": "00002",
            "image": ["images/00002_a.jpg", "images/00002_b.jpg", "images/00002_c.jpg"],
            "question": "Which is the correct escape?",
            "choices": ["Image A", "Image B", "Image C"],
            "answer": "C",
            "experience_level": "advanced",
            "category": "no_gi",
            "subject": "escapes",
            "source": "course/02",
        }
        sample = SampleRecord.model_validate(record)
        assert sample.answer == "C"
        assert len(sample.choices) == len(record["choices"])
