"""Shared test constants and helper functions."""

import json
import shutil
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"

YOUTUBE_URL = "https://www.youtube.com/watch?v=SzL_uObk8fk"

VALID_SAMPLE = {
    "id": "00001",
    "image": "images/00001.jpg",
    "question": "What technique is shown?",
    "choices": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "A",
    "experience_level": "beginner",
    "category": "gi",
    "subject": "guard",
    "source": "https://youtube.com/watch?v=SzL_uObk8fk&t=70s",
    "timestamp": 70,
}

EMPTY_REGISTRY = {
    "url": "",
    "title": "",
    "creator": "",
    "license_type": "cc_by",
    "question_ids": [],
}


def init_data_dir(tmp_path: Path, *, with_fixtures: bool = False) -> Path:
    """Create data/images + sources dirs. Copy fixtures if requested."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "images").mkdir()
    sources_dir = tmp_path / "sources"
    sources_dir.mkdir()
    if with_fixtures:
        shutil.copy2(FIXTURES_DIR / "samples.json", data_dir / "samples.json")
        shutil.copy2(FIXTURES_DIR / "registry.jsonl", sources_dir / "registry.jsonl")
    for img in (FIXTURES_DIR / "images").glob("*.jpg"):
        shutil.copy2(img, data_dir / "images" / img.name)
    return data_dir


def write_samples(data_dir: Path, samples: list[dict]):
    """Write samples.json to data_dir."""
    (data_dir / "samples.json").write_text(json.dumps(samples, indent=2))


def write_registry(data_dir: Path, entry: dict):
    """Write registry.jsonl to the sources dir next to data_dir."""
    (data_dir.parent / "sources" / "registry.jsonl").write_text(
        json.dumps(entry) + "\n",
    )
