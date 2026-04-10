"""Tests for BJJ-VQA CLI commands."""

import json
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image

from bjj_vqa.cli import validate


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory with test image."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        images_dir = data_dir / "images"
        images_dir.mkdir()

        # Create a test image
        img = Image.new("RGB", (100, 100), color="red")
        img.save(images_dir / "00001.jpg")

        yield data_dir


@pytest.fixture
def valid_samples():
    """Valid sample records for testing."""
    return [
        {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "What technique is this?",
            "choices": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test&t=60s",
        },
    ]


@pytest.fixture
def invalid_samples_wrong_subject():
    """Samples with invalid subject value."""
    return [
        {
            "id": "00001",
            "image": "images/00001.jpg",
            "question": "What technique is this?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "invalid_subject",  # Invalid
            "source": "https://youtube.com/watch?v=test",
        },
    ]


@pytest.fixture
def invalid_samples_missing_image():
    """Samples referencing non-existent image."""
    return [
        {
            "id": "00001",
            "image": "images/nonexistent.jpg",  # Doesn't exist
            "question": "What technique is this?",
            "choices": ["A", "B", "C", "D"],
            "answer": "A",
            "experience_level": "beginner",
            "category": "gi",
            "subject": "guard",
            "source": "https://youtube.com/watch?v=test",
        },
    ]


class TestValidate:
    """Tests for validate CLI command."""

    def test_validate_success(self, temp_data_dir, valid_samples, monkeypatch):
        """Validate succeeds with valid samples."""
        # Write valid samples
        samples_path = temp_data_dir / "samples.json"
        samples_path.write_text(json.dumps(valid_samples))

        # Patch DATA_DIR
        import bjj_vqa.cli
        monkeypatch.setattr(bjj_vqa.cli, "DATA_DIR", temp_data_dir)

        # Should not raise
        validate()

    def test_validate_invalid_schema(self, temp_data_dir, invalid_samples_wrong_subject, monkeypatch):
        """Validate fails with schema errors."""
        # Write invalid samples
        samples_path = temp_data_dir / "samples.json"
        samples_path.write_text(json.dumps(invalid_samples_wrong_subject))

        # Patch DATA_DIR
        import bjj_vqa.cli
        monkeypatch.setattr(bjj_vqa.cli, "DATA_DIR", temp_data_dir)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    def test_validate_missing_image(self, temp_data_dir, invalid_samples_missing_image, monkeypatch):
        """Validate fails when image file doesn't exist."""
        # Write samples with missing image reference
        samples_path = temp_data_dir / "samples.json"
        samples_path.write_text(json.dumps(invalid_samples_missing_image))

        # Patch DATA_DIR
        import bjj_vqa.cli
        monkeypatch.setattr(bjj_vqa.cli, "DATA_DIR", temp_data_dir)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    def test_validate_missing_samples_file(self, temp_data_dir, monkeypatch):
        """Validate fails when samples.json doesn't exist."""
        # No samples.json created
        import bjj_vqa.cli
        monkeypatch.setattr(bjj_vqa.cli, "DATA_DIR", temp_data_dir)

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    def test_validate_multiple_samples(self, temp_data_dir, monkeypatch):
        """Validate handles multiple samples."""
        # Create additional images
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(temp_data_dir / "images" / "00002.jpg")

        samples = [
            {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "Question 1?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": "beginner",
                "category": "gi",
                "subject": "guard",
                "source": "https://youtube.com/watch?v=test&t=60s",
            },
            {
                "id": "00002",
                "image": "images/00002.jpg",
                "question": "Question 2?",
                "choices": ["A", "B", "C", "D"],
                "answer": "B",
                "experience_level": "intermediate",
                "category": "no_gi",
                "subject": "submissions",
                "source": "https://youtube.com/watch?v=test&t=120s",
            },
        ]

        samples_path = temp_data_dir / "samples.json"
        samples_path.write_text(json.dumps(samples))

        import bjj_vqa.cli
        monkeypatch.setattr(bjj_vqa.cli, "DATA_DIR", temp_data_dir)

        # Should succeed
        validate()