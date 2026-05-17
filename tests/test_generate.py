"""Integration tests for the generate pipeline.

Requires OPENROUTER_API_KEY. Calls real external services.
Run: uv run pytest tests/test_generate.py -v -m integration
"""

import json
import os

import pytest

from bjj_vqa.cli import validate
from bjj_vqa.generate import GeneratedQuestion, generate_questions, run

from .helpers import VALID_SAMPLE, YOUTUBE_URL

pytestmark = pytest.mark.integration

skip_no_key = pytest.mark.skipif(
    os.environ.get("OPENROUTER_API_KEY") is None,
    reason="OPENROUTER_API_KEY not set",
)


@skip_no_key
def test_generate_questions_returns_valid_output():
    """Gemini returns valid GeneratedQuestion objects from a YouTube URL."""
    questions = generate_questions(YOUTUBE_URL)

    assert 3 <= len(questions) <= 8
    for q in questions:
        assert isinstance(q, GeneratedQuestion)
        assert len(q.question) > 10
        assert len(q.choices) == 4
        assert q.answer in ("A", "B", "C", "D")
        assert q.experience_level in ("beginner", "intermediate", "advanced")
        assert q.category in ("gi", "no_gi")
        assert q.subject in (
            "guard",
            "passing",
            "submissions",
            "controls",
            "escapes",
            "takedowns",
        )
        assert q.timestamp > 0


@skip_no_key
def test_run_creates_records_and_images(gen_env):
    """The full pipeline creates records, images, samples.json, and registry."""
    records = run(YOUTUBE_URL, data_dir=gen_env)

    assert len(records) >= 3
    for r in records:
        assert (gen_env / r.image).exists()
        assert (gen_env / r.image).stat().st_size > 0

    samples = json.loads((gen_env / "samples.json").read_text())
    assert len(samples) == len(records)

    source_entry = json.loads(
        (gen_env.parent / "sources" / "registry.jsonl").read_text().strip(),
    )
    assert source_entry["url"] == YOUTUBE_URL
    assert source_entry["license_type"] in ("cc_by", "cc_by_sa", "permissioned")
    assert len(source_entry["question_ids"]) == len(records)


@skip_no_key
def test_run_appends_to_existing_samples(gen_env):
    """run() appends to existing samples.json without overwriting."""
    existing = [
        {
            **VALID_SAMPLE,
            "source": "https://youtube.com/watch?v=existing",
            "timestamp": 10,
        },
    ]
    (gen_env / "samples.json").write_text(json.dumps(existing, indent=2))

    records = run(YOUTUBE_URL, data_dir=gen_env)

    samples = json.loads((gen_env / "samples.json").read_text())
    assert len(samples) == 1 + len(records)
    assert samples[0]["id"] == "00001"


@skip_no_key
def test_run_output_passes_validate(gen_env):
    """Generated data passes bjj-vqa validate end-to-end."""
    run(YOUTUBE_URL, data_dir=gen_env)
    validate(data_dir=gen_env)
