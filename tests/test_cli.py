"""Tests for BJJ-VQA CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image


@pytest.fixture
def temp_data_env():
    """Create temporary data directory and set BJJ_VQA_DATA_DIR env var."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        images_dir = data_dir / "images"
        images_dir.mkdir()

        # Create test image
        img = Image.new("RGB", (100, 100), color="red")
        img.save(images_dir / "00001.jpg")

        # Set env var and yield path
        os.environ["BJJ_VQA_DATA_DIR"] = str(data_dir)
        yield data_dir

        # Cleanup
        os.environ.pop("BJJ_VQA_DATA_DIR", None)


def write_samples(data_dir: Path, samples: list[dict]) -> Path:
    """Write samples.json to data directory."""
    samples_path = data_dir / "samples.json"
    samples_path.write_text(json.dumps(samples))
    return samples_path


class TestValidate:
    """Tests for validate CLI command."""

    @patch("bjj_vqa.cli.validate_sources")
    def test_validate_success(self, mock_validate_sources, temp_data_env):
        """Validate succeeds with valid samples."""
        valid_samples = [
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
        write_samples(temp_data_env, valid_samples)

        # Import after env var is set
        from bjj_vqa.cli import validate

        validate()

    def test_validate_invalid_schema(self, temp_data_env):
        """Validate fails with schema errors."""
        invalid_samples = [
            {
                "id": "00001",
                "image": "images/00001.jpg",
                "question": "What technique is this?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": "beginner",
                "category": "gi",
                "subject": "invalid_subject",
                "source": "https://youtube.com/watch?v=test",
            },
        ]
        write_samples(temp_data_env, invalid_samples)

        from bjj_vqa.cli import validate

        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    def test_validate_missing_image(self, temp_data_env):
        """Validate fails when image file doesn't exist."""
        samples = [
            {
                "id": "00001",
                "image": "images/nonexistent.jpg",
                "question": "What technique is this?",
                "choices": ["A", "B", "C", "D"],
                "answer": "A",
                "experience_level": "beginner",
                "category": "gi",
                "subject": "guard",
                "source": "https://youtube.com/watch?v=test",
            },
        ]
        write_samples(temp_data_env, samples)

        from bjj_vqa.cli import validate

        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    def test_validate_missing_samples_file(self, temp_data_env):
        """Validate fails when samples.json doesn't exist."""
        from bjj_vqa.cli import validate

        with pytest.raises(SystemExit) as exc_info:
            validate()
        assert exc_info.value.code == 1

    @patch("bjj_vqa.cli.validate_sources")
    def test_validate_multiple_samples(self, mock_validate_sources, temp_data_env):
        """Validate handles multiple samples."""
        # Create additional image
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(temp_data_env / "images" / "00002.jpg")

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
        write_samples(temp_data_env, samples)

        from bjj_vqa.cli import validate

        validate()
