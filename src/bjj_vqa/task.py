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

    return Sample(
        id=record["id"],
        input=[
            ChatMessageUser(
                content=[
                    ContentImage(image=full_image_path),
                    ContentText(text=record["question"]),
                ],
            ),
        ],
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
