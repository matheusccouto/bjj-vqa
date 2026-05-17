"""Shared test fixtures."""

from pathlib import Path

import pytest

from .helpers import init_data_dir, write_samples


@pytest.fixture
def env(tmp_path: Path):
    """Data dir with valid fixture data (samples.json, images, registry)."""
    return init_data_dir(tmp_path, with_fixtures=True)


@pytest.fixture
def empty_env(tmp_path: Path):
    """Data dir with images but no samples.json or registry.jsonl."""
    return init_data_dir(tmp_path, with_fixtures=False)


@pytest.fixture
def gen_env(tmp_path: Path):
    """Data dir with empty samples.json and registry.jsonl for generate tests."""
    data_dir = init_data_dir(tmp_path, with_fixtures=False)
    write_samples(data_dir, [])
    (data_dir.parent / "sources" / "registry.jsonl").write_text("")
    return data_dir
