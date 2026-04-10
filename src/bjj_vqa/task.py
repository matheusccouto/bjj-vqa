"""BJJ-VQA inspect-ai task definition."""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText, GenerateConfig
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice

from bjj_vqa.schema import DATA_DIR


def record_to_sample(record: dict) -> Sample:
    """Convert a JSON record to an inspect-ai Sample with multimodal input."""
    full_image_path = str(DATA_DIR / record["image"])

    input_content = [
        ContentImage(image=full_image_path),
        ContentText(text=record["question"]),
    ]

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


@task
def bjj_vqa() -> Task:
    """BJJ-VQA benchmark task for evaluating vision-language models."""
    dataset = json_dataset(
        json_file=str(DATA_DIR / "samples.json"),
        # RecordToSample required: FieldSpec can't combine image+question
        # into multimodal ChatMessageUser or resolve image paths
        sample_fields=record_to_sample,
    )

    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
        config=GenerateConfig(max_tokens=128),
    )
