"""Schema and constants for BJJ-VQA dataset."""

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


def get_data_dir() -> Path:
    """Get data directory from env var or default."""
    default_path = Path(__file__).parent.parent.parent / "data"
    return Path(os.environ.get("BJJ_VQA_DATA_DIR", default_path))


DATA_DIR = get_data_dir()

Answer = Literal["A", "B", "C", "D"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
Category = Literal["gi", "no_gi"]
Subject = Literal["guard", "passing", "submissions", "controls", "escapes", "takedowns"]


class SampleRecord(BaseModel):
    """Schema for a BJJ-VQA sample with automatic validation."""

    id: str
    image: str
    question: str
    choices: list[str] = Field(min_length=4, max_length=4)
    answer: Answer
    experience_level: ExperienceLevel
    category: Category
    subject: Subject
    source: str
