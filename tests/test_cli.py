"""Tests for BJJ-VQA CLI: validate and validate-sources."""

import pytest

from bjj_vqa.cli import validate, validate_sources

from .helpers import (
    EMPTY_REGISTRY,
    VALID_SAMPLE,
    init_data_dir,
    write_registry,
    write_samples,
)


def test_validate_happy_path(env):
    """Valid fixture data passes validation end-to-end."""
    validate(data_dir=env)


def test_validate_rejects_bad_data(empty_env):
    """Invalid schema field causes validation failure."""
    write_samples(empty_env, [{**VALID_SAMPLE, "subject": "invalid_subject"}])
    write_registry(empty_env, EMPTY_REGISTRY)
    with pytest.raises(SystemExit):
        validate(data_dir=empty_env)


def test_validate_rejects_missing_image(empty_env):
    """Referencing a nonexistent image causes validation failure."""
    write_samples(empty_env, [{**VALID_SAMPLE, "image": "images/nonexistent.jpg"}])
    write_registry(empty_env, EMPTY_REGISTRY)
    with pytest.raises(SystemExit):
        validate(data_dir=empty_env)


def test_validate_rejects_answer_beyond_choices(empty_env):
    """Answer letter exceeding the number of choices causes failure."""
    write_samples(
        empty_env,
        [{**VALID_SAMPLE, "choices": ["Only two", "Another"], "answer": "C"}],
    )
    write_registry(empty_env, EMPTY_REGISTRY)
    with pytest.raises(SystemExit):
        validate(data_dir=empty_env)


def test_validate_rejects_missing_samples_json(tmp_path):
    """Missing samples.json causes validation failure."""
    data_dir = init_data_dir(tmp_path, with_fixtures=False)
    # Remove what init_data_dir created (empty samples.json placeholder not needed)
    (data_dir / "samples.json").unlink(missing_ok=True)
    with pytest.raises(SystemExit):
        validate(data_dir=data_dir)


def test_validate_sources_happy_path(env):
    """Valid registry cross-references pass validation."""
    validate_sources(data_dir=env)


def test_validate_sources_rejects_bad_crossrefs(empty_env):
    """Registry referencing nonexistent question IDs causes failure."""
    write_samples(empty_env, [VALID_SAMPLE])
    write_registry(
        empty_env,
        {
            "url": "https://youtube.com/watch?v=SzL_uObk8fk",
            "title": "Test",
            "creator": "Test",
            "license_type": "cc_by",
            "question_ids": ["00001", "99999"],
        },
    )
    with pytest.raises(SystemExit):
        validate_sources(data_dir=empty_env)
