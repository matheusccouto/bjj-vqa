"""Schema and constants for BJJ-VQA dataset."""

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator


def get_data_dir() -> Path:
    """Get data directory from env var or default."""
    default_path = Path(__file__).parent.parent.parent / "data"
    return Path(os.environ.get("BJJ_VQA_DATA_DIR", default_path))


DATA_DIR = get_data_dir()


def as_image_list(image: str | list[str]) -> list[str]:
    """Normalize the image field to a list of paths."""
    return image if isinstance(image, list) else [image]


Answer = Literal["A", "B", "C", "D"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]
Category = Literal["gi", "no_gi"]
Subject = Literal["guard", "passing", "submissions", "controls", "escapes", "takedowns"]


class SampleRecord(BaseModel):
    """Schema for a BJJ-VQA sample with automatic validation."""

    id: str
    image: str | list[str]
    question: str
    choices: list[str] = Field(min_length=2, max_length=4)
    answer: Answer
    experience_level: ExperienceLevel
    category: Category
    subject: Subject
    source: str

    @model_validator(mode="after")
    def answer_within_choices(self) -> "SampleRecord":
        """Ensure the answer letter is within the number of choices."""
        index = ord(self.answer) - ord("A")
        if index >= len(self.choices):
            n = len(self.choices)
            msg = f"answer '{self.answer}' is out of range for {n} choices"
            raise ValueError(msg)
        return self
