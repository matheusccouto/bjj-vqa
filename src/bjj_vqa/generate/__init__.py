"""Generate BJJ-VQA questions from a YouTube URL using Gemini via OpenRouter."""

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from openai import OpenAI

from bjj_vqa.schema import SampleRecord, get_data_dir

_MODEL = "google/gemini-flash-latest"


def _get_client() -> OpenAI:
    """Create an OpenAI-compatible client for OpenRouter."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=_require_env("OPENROUTER_API_KEY"),
    )


def _require_env(name: str) -> str:
    """Get required environment variable or exit with error."""
    val = os.environ.get(name)
    if not val:
        print(f"ERROR: Environment variable {name} is required but not set")
        sys.exit(1)
    return val


def _load_prompt() -> str:
    """Load the generation prompt from prompt.md."""
    prompt_path = Path(__file__).parent / "prompt.md"
    return prompt_path.read_text()


def generate_questions(youtube_url: str) -> list[dict]:
    """Call Gemini via OpenRouter to generate questions from a YouTube URL.

    Returns a list of dicts matching the SampleRecord schema.
    """
    client = _get_client()
    prompt = _load_prompt()

    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "video_url", "video_url": {"url": youtube_url}},
                ],
            },
        ],
        temperature=0.3,
        max_tokens=8000,
    )

    text = resp.choices[0].message.content or ""
    # Extract JSON array from response (may have markdown code fences)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    if text.startswith("json"):
        text = text[4:].strip()

    return json.loads(text)


def _extract_frame(youtube_url: str, timestamp: int, output_path: Path) -> None:
    """Extract a single frame at the given timestamp using yt-dlp + ffmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get direct stream URL via yt-dlp
    result = subprocess.run(
        ["yt-dlp", "-g", "-f", "best[height<=720]", youtube_url],
        capture_output=True,
        text=True,
        check=True,
    )
    stream_url = result.stdout.strip()

    # Extract frame via ffmpeg
    subprocess.run(
        [
            "ffmpeg",
            "-ss",
            str(timestamp),
            "-i",
            stream_url,
            "-vframes",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ],
        capture_output=True,
        check=True,
    )


def run(youtube_url: str) -> list[SampleRecord]:
    """Full generate pipeline: call Gemini, extract frames, append to samples.json.

    Returns the list of newly generated SampleRecord objects.
    """
    questions = generate_questions(youtube_url)
    data_dir = get_data_dir()
    images_dir = data_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    records: list[SampleRecord] = []
    for q in questions:
        image_name = f"{uuid.uuid4().hex[:8]}.jpg"
        image_path = images_dir / image_name
        timestamp = q.get("timestamp_seconds", 0)

        _extract_frame(youtube_url, timestamp, image_path)

        record = SampleRecord(
            id=uuid.uuid4().hex[:5],
            image=f"images/{image_name}",
            question=q["question"],
            choices=q["choices"],
            answer=q["answer"],
            experience_level=q["experience_level"],
            category=q["category"],
            subject=q["subject"],
            source=q["source"],
        )
        records.append(record)

    # Append to samples.json
    samples_path = data_dir / "samples.json"
    existing: list[dict] = []
    if samples_path.exists():
        existing = json.loads(samples_path.read_text())
    existing.extend([r.model_dump() for r in records])
    samples_path.write_text(json.dumps(existing, indent=2))

    return records
