"""CLI for BJJ-VQA dataset operations."""

import argparse
import json
import os
import sys

from datasets import Dataset, DatasetDict
from PIL import Image
from pydantic import ValidationError

from bjj_vqa.schema import DATA_DIR, SampleRecord


def main() -> None:
    """CLI entry point for BJJ-VQA dataset operations."""
    parser = argparse.ArgumentParser(description="BJJ-VQA CLI")
    subparsers = parser.add_subparsers(required=True)

    validate_cmd = subparsers.add_parser("validate", help="Validate dataset schema")
    validate_cmd.set_defaults(func=lambda _: validate())

    publish_cmd = subparsers.add_parser("publish", help="Publish to HuggingFace Hub")
    publish_cmd.add_argument("--repo", required=True, help="Target repo")
    publish_cmd.add_argument("--tag", required=True, help="Release tag")
    publish_cmd.set_defaults(func=lambda a: publish(a.repo, a.tag))

    args = parser.parse_args()
    args.func(args)


def validate() -> None:
    """Validate samples.json schema and image paths."""
    data_path = DATA_DIR / "samples.json"
    try:
        data = json.loads(data_path.read_text())
    except FileNotFoundError:
        print(f"ERROR: {data_path} not found")
        sys.exit(1)

    errors = []

    for record in data:
        rid = record.get("id", "UNKNOWN")
        schema_failed = False

        try:
            SampleRecord.model_validate(record)
        except ValidationError as e:
            schema_failed = True
            for err in e.errors():
                field = err["loc"][0]
                msg = err["msg"]
                errors.append(f"{rid}: {field} - {msg}")

        # Only check image if schema passed
        if not schema_failed:
            image_path = DATA_DIR / record.get("image", "")
            if not image_path.exists():
                errors.append(f"{rid}: image '{image_path}' not found")

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"OK: {len(data)} records valid")


def publish(repo: str, tag: str) -> None:
    """Publish dataset to Hugging Face Hub."""
    token = _env_or_exit("HF_TOKEN")
    data_path = DATA_DIR / "samples.json"
    data = json.loads(data_path.read_text())

    records = [SampleRecord.model_validate(r) for r in data]

    images = [Image.open(DATA_DIR / r.image) for r in records]

    dataset = Dataset.from_dict(
        {
            "id": [r.id for r in records],
            "image": images,
            "question": [r.question for r in records],
            "choices": [r.choices for r in records],
            "answer": [r.answer for r in records],
            "experience_level": [r.experience_level for r in records],
            "category": [r.category for r in records],
            "subject": [r.subject for r in records],
            "source": [r.source for r in records],
        },
    )

    # Create DatasetDict with 'test' split for benchmark compatibility
    dataset_dict = DatasetDict({"test": dataset})

    dataset_dict.push_to_hub(repo_id=repo, token=token, commit_message=f"Release {tag}")

    print(f"Published to {repo} with tag {tag}")
    print(f"https://huggingface.co/datasets/{repo}")


def _env_or_exit(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: {name} not set")
        sys.exit(1)
    return val
