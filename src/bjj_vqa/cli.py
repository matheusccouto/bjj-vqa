"""CLI for BJJ-VQA dataset operations."""

import argparse
import base64
import io
import json
import os
import sys

from datasets import Dataset, DatasetDict
from huggingface_hub.utils import HfHubHTTPError
from PIL import Image
from pydantic import ValidationError

from bjj_vqa.schema import SampleRecord, get_data_dir


def _image_to_data_uri(img: Image.Image) -> str:
    """Convert a PIL Image to a base64 data URI."""
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_base64}"


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
    data_dir = get_data_dir()
    data_path = data_dir / "samples.json"

    try:
        data: list[dict] = json.loads(data_path.read_text())
    except FileNotFoundError:
        print(f"ERROR: samples.json not found at {data_path}")
        print("Hint: Run from project root or set BJJ_VQA_DATA_DIR")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {data_path}")
        print(f"  Line {e.lineno}, column {e.colno}: {e.msg}")
        sys.exit(1)

    errors: list[str] = []
    valid_count = 0

    for record in data:
        rid = record.get("id", "UNKNOWN")
        schema_failed = False

        try:
            SampleRecord.model_validate(record)
        except ValidationError as e:
            schema_failed = True
            for err in e.errors():
                field = err["loc"][0]
                value = record.get(field, "missing")
                msg = err["msg"]
                errors.append(f"  {rid}: {field}='{value}' - {msg}")

        if not schema_failed:
            image_rel = record.get("image", "")
            image_path = data_dir / image_rel
            if not image_path.exists():
                errors.append(f"  {rid}: image '{image_rel}' not found at {image_path}")
            else:
                valid_count += 1

    if errors:
        print(f"Validation failed ({len(errors)} errors):")
        for e in errors:
            print(e)
        sys.exit(1)

    print(f"OK: {valid_count}/{len(data)} records valid")


def publish(repo: str, tag: str) -> None:
    """Publish dataset to Hugging Face Hub."""
    token = _require_env("HF_TOKEN")
    data_dir = get_data_dir()
    data_path = data_dir / "samples.json"

    try:
        data: list[dict] = json.loads(data_path.read_text())
    except FileNotFoundError:
        print(f"ERROR: samples.json not found at {data_path}")
        print("Hint: Run 'bjj-vqa validate' first to create dataset")
        sys.exit(1)

    try:
        records = [SampleRecord.model_validate(r) for r in data]
    except ValidationError:
        print("ERROR: Invalid records in samples.json")
        print("Hint: Run 'bjj-vqa validate' to see detailed errors")
        sys.exit(1)

    # Convert images to base64 data URIs
    images: list[str] = []
    for r in records:
        try:
            img = Image.open(data_dir / r.image)
            images.append(_image_to_data_uri(img))
        except FileNotFoundError:
            print(f"ERROR: Image not found: {r.image}")
            print("Hint: Run 'bjj-vqa validate' to check image paths")
            sys.exit(1)

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

    dataset_dict = DatasetDict({"test": dataset})

    try:
        dataset_dict.push_to_hub(
            repo_id=repo,
            token=token,
            commit_message=f"Release {tag}",
        )
    except HfHubHTTPError as e:
        print("ERROR: Failed to push to Hugging Face Hub")
        print(f"  {e}")
        print("Hint: Check HF_TOKEN has write access to repo")
        sys.exit(1)

    print(f"Published {len(records)} records to {repo}")
    print(f"https://huggingface.co/datasets/{repo}")


def _require_env(name: str) -> str:
    """Get required environment variable or exit with error."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: Environment variable {name} is required but not set")
        print("Hint: Set it in your shell or .env file")
        sys.exit(1)
    return val
