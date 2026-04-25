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
StemType = Literal["COMPLETION", "CLASSIFICATION"]
OptionType = Literal["CORRECT", "WRONG_CONTEXT", "WRONG_MECHANISM", "WRONG_DIRECTION"]
SourceLicense = Literal[
    "cc_by",
    "cc_by_sa",
    "permissioned",
    "owned",
    "synthetic",
    "fair_use",
]
Language = Literal["en", "pt-br"]


class SampleRecord(BaseModel):
    """Schema for a BJJ-VQA sample with automatic validation.

    Required fields match the original 57-question dataset.
    Optional fields capture methodology metadata added in v0.3+; existing
    records without these fields remain valid (all default to None/False/en).

    When is_unanswerable=True, the choices list must include a
    "cannot be determined" (or equivalent) option as the correct answer.
    """

    id: str
    image: str | list[str]
    question: str
    choices: list[str] = Field(min_length=2, max_length=4)
    answer: Answer
    experience_level: ExperienceLevel
    category: Category
    subject: Subject
    source: str

    # Methodology metadata — optional, defaults preserve backward compatibility
    stem_type: StemType | None = None
    option_types: dict[str, OptionType] | None = None
    concept: str | None = None
    source_license: SourceLicense | None = None
    is_unanswerable: bool = False
    language: Language = "en"

    @model_validator(mode="after")
    def answer_within_choices(self) -> "SampleRecord":
        """Ensure the answer letter is within the number of choices."""
        index = ord(self.answer) - ord("A")
        if index >= len(self.choices):
            n = len(self.choices)
            msg = f"answer '{self.answer}' is out of range for {n} choices"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def option_types_has_one_correct(self) -> "SampleRecord":
        """When option_types is provided, the answer key must map to CORRECT."""
        if self.option_types is None:
            return self
        correct_keys = [k for k, v in self.option_types.items() if v == "CORRECT"]
        if len(correct_keys) != 1:
            msg = (
                f"option_types must have exactly one CORRECT entry, got {correct_keys}"
            )
            raise ValueError(msg)
        if self.option_types.get(self.answer) != "CORRECT":
            msg = (
                f"answer '{self.answer}' must map to CORRECT in option_types, "
                f"but maps to '{self.option_types.get(self.answer)}'"
            )
            raise ValueError(msg)
        return self


class Source(BaseModel):
    """Schema for a source registry entry in sources/registry.jsonl."""

    url: str
    title: str
    creator: str
    license_type: SourceLicense
    permission_reference: str | None = None
    question_ids: list[str]
    notes: str = ""
