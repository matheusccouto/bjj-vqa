"""Integration tests for the generate CLI.

These tests use the real OpenRouter API and are marked with
@pytest.mark.integration. They skip automatically when
OPENROUTER_API_KEY is not set.

Run explicitly: uv run pytest tests/test_generate.py -v -m integration
"""

import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory with empty samples.json."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    images_dir = data_dir / "images"
    images_dir.mkdir()
    (data_dir / "samples.json").write_text("[]")
    return data_dir


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="requires OPENROUTER_API_KEY",
)
def test_generate_appends_valid_records(temp_data_dir: Path) -> None:
    """Generate appends valid records to samples.json."""
    import os as _os

    _os.environ["BJJ_VQA_DATA_DIR"] = str(temp_data_dir)

    try:
        from bjj_vqa.generate import run

        # Use a short CC-licensed video
        url = "https://www.youtube.com/watch?v=SzL_uObk8fk"
        records = run(url)

        assert len(records) >= 1, "Expected at least 1 generated question"

        # Verify records were appended
        samples = json.loads((temp_data_dir / "samples.json").read_text())
        assert len(samples) >= 1

        # Verify each record is valid
        from bjj_vqa.schema import SampleRecord

        for s in samples:
            SampleRecord.model_validate(s)
    finally:
        _os.environ.pop("BJJ_VQA_DATA_DIR", None)


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="requires OPENROUTER_API_KEY",
)
def test_generate_creates_images(temp_data_dir: Path) -> None:
    """Generate creates image files in data/images/."""
    import os as _os

    _os.environ["BJJ_VQA_DATA_DIR"] = str(temp_data_dir)

    try:
        from bjj_vqa.generate import run

        url = "https://www.youtube.com/watch?v=SzL_uObk8fk"
        run(url)

        images_dir = temp_data_dir / "images"
        image_files = list(images_dir.glob("*.jpg"))
        assert len(image_files) >= 1, "Expected at least 1 image file"

        # Verify image names are short UUID hex
        for img in image_files:
            name = img.stem
            assert len(name) == 8, f"Expected 8-char hex name, got {name}"
            int(name, 16)  # verify it's valid hex
    finally:
        _os.environ.pop("BJJ_VQA_DATA_DIR", None)


@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="requires OPENROUTER_API_KEY",
)
def test_validate_passes_after_generate(temp_data_dir: Path) -> None:
    """bjj-vqa validate passes after generate."""
    import os as _os

    _os.environ["BJJ_VQA_DATA_DIR"] = str(temp_data_dir)

    try:
        from bjj_vqa.generate import run

        url = "https://www.youtube.com/watch?v=SzL_uObk8fk"
        run(url)

        from bjj_vqa.cli import validate

        validate()  # Should not raise
    finally:
        _os.environ.pop("BJJ_VQA_DATA_DIR", None)
