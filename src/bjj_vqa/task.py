"""BJJ-VQA inspect-ai task definition."""

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import accuracy, choice, grouped
from inspect_ai.solver import multiple_choice

from bjj_vqa.schema import get_data_dir


def record_to_sample(
    record: dict,
    *,
    images: bool = True,
    data_dir: Path | None = None,
) -> Sample:
    """Convert a JSON record to an inspect-ai Sample with multimodal input."""
    if data_dir is None:
        data_dir = get_data_dir()
    image = record["image"]

    if isinstance(image, list):
        input_content: list[ContentImage | ContentText] = []
        for letter, path in zip("ABCD", image, strict=False):
            input_content.append(ContentText(text=f"Image {letter}:"))
            if images:
                assert isinstance(path, str)  # noqa: S101  # type narrowing for ty
                input_content.append(ContentImage(image=str(data_dir / path)))
        input_content.append(ContentText(text=record["question"]))
    else:
        input_content: list[ContentImage | ContentText] = []
        if images:
            assert isinstance(image, str)  # noqa: S101  # type narrowing for ty
            input_content.append(ContentImage(image=str(data_dir / image)))
        input_content.append(ContentText(text=record["question"]))

    return Sample(
        id=record["id"],
        input=[ChatMessageUser(content=input_content)],  # ty: ignore[invalid-argument-type]
        choices=record["choices"],
        target=record["answer"],
        metadata={
            "experience_level": record["experience_level"],
            "category": record["category"],
            "subject": record["subject"],
            "source": record["source"],
        },
    )


def _make_task(*, images: bool) -> Task:
    data_dir = get_data_dir()
    dataset = json_dataset(
        json_file=str(data_dir / "samples.json"),
        sample_fields=lambda r: record_to_sample(r, images=images, data_dir=data_dir),
    )
    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
        metrics=[
            accuracy(),
            grouped(accuracy(), "experience_level"),
            grouped(accuracy(), "category"),
            grouped(accuracy(), "subject"),
        ],
    )


@task
def bjj_vqa() -> Task:
    """BJJ-VQA benchmark task for evaluating vision-language models."""
    return _make_task(images=True)


@task
def bjj_vqa_no_images() -> Task:
    """Text-only baseline: same questions but no images.

    Run alongside bjj_vqa to verify models use visual input rather than guessing.
    """
    return _make_task(images=False)
