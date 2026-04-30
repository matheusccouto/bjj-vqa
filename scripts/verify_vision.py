"""Verify that the VLM vision pipeline is correctly processing images.

Creates 4 synthetic images with unambiguous visual content and runs a short
eval through the exact same inspect-ai pipeline used by the real benchmark.
Any model that can truly see images should score 100%.
A failure means images are not being sent or processed correctly.

Usage:
    uv run python scripts/verify_vision.py --model openrouter/google/gemma-4-31b-it
    uv run python scripts/verify_vision.py --model anthropic/claude-3-5-sonnet-latest
"""

import argparse
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

from inspect_ai import Task
from inspect_ai import eval as inspect_eval
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice
from PIL import Image, ImageDraw, ImageFont

# Each entry: (question, image_A_key, image_B_key, correct_answer)
QUESTIONS = [
    ("Which image shows the letter X?", "letter_x", "letter_o", "A"),
    ("Which image shows the number 7?", "digit_3", "digit_7", "B"),
    ("Which image has a red background?", "red", "blue", "A"),
    ("Which image shows a circle?", "square", "circle", "B"),
]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _text_image(text: str, size: int = 256) -> Image.Image:
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    font = _font(size // 2)
    draw.text((size // 2, size // 2), text, fill="black", anchor="mm", font=font)
    return img


def _color_image(color: str, size: int = 256) -> Image.Image:
    return Image.new("RGB", (size, size), color=color)


def _shape_image(shape: str, size: int = 256) -> Image.Image:
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    m = size // 5
    box = [m, m, size - m, size - m]
    if shape == "circle":
        draw.ellipse(box, fill="black")
    else:
        draw.rectangle(box, fill="black")
    return img


IMAGE_FACTORIES: dict[str, Callable] = {
    "letter_x": lambda: _text_image("X"),
    "letter_o": lambda: _text_image("O"),
    "digit_3": lambda: _text_image("3"),
    "digit_7": lambda: _text_image("7"),
    "red": lambda: _color_image("red"),
    "blue": lambda: _color_image("blue"),
    "circle": lambda: _shape_image("circle"),
    "square": lambda: _shape_image("square"),
}


def _save_images(tmp_dir: Path) -> dict[str, str]:
    paths: dict[str, str] = {}
    for name, factory in IMAGE_FACTORIES.items():
        path = tmp_dir / f"{name}.jpg"
        factory().save(path, "JPEG")
        paths[name] = str(path)
    return paths


def _build_sample(
    sid: str,
    question: str,
    img_a: str,
    img_b: str,
    target: str,
) -> Sample:
    return Sample(
        id=sid,
        input=[
            ChatMessageUser(
                content=[
                    ContentText(text="Image A:"),
                    ContentImage(image=img_a),
                    ContentText(text="Image B:"),
                    ContentImage(image=img_b),
                    ContentText(text=question),
                ],
            ),
        ],
        choices=["Image A", "Image B"],
        target=target,
    )


def build_task(tmp_dir: Path) -> Task:
    """Build a task with synthetic unambiguous visual questions."""
    paths = _save_images(tmp_dir)
    samples = [
        _build_sample(f"q{i + 1}", question, paths[a], paths[b], answer)
        for i, (question, a, b, answer) in enumerate(QUESTIONS)
    ]
    return Task(dataset=samples, solver=multiple_choice(), scorer=choice())


def main() -> None:
    """Run the vision pipeline verification."""
    parser = argparse.ArgumentParser(
        description="Verify the VLM vision pipeline processes images correctly.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model to test (e.g. openrouter/google/gemma-4-31b-it)",
    )
    args = parser.parse_args()

    print(f"Vision pipeline check: {args.model}")
    print(f"Questions: {len(QUESTIONS)}")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        task = build_task(Path(tmp))
        logs = inspect_eval(task, model=args.model)

    if not logs or logs[0].status == "error":
        print("ERROR: eval did not complete successfully.")
        sys.exit(1)

    results = logs[0].results
    assert results is not None, "Eval returned no results"
    accuracy = results.scores[0].metrics["accuracy"].value
    n = len(QUESTIONS)
    n_correct = round(accuracy * n)

    print(f"Score: {n_correct}/{n} ({accuracy:.0%})")

    if n_correct == n:
        print("PASS: model is correctly reading image content.")
        sys.exit(0)
    else:
        wrong = n - n_correct
        print(f"FAIL: {wrong} question(s) answered incorrectly.")
        print("Images may not be reaching the model or are not being processed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
