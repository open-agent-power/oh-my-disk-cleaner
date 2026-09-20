"""
Regression tests for DiskAnalyzer._get_dir_size_fast directory sizing.

Guards against the depth-cap defect where the fast size walk stopped after a
couple of directory levels and reported deeply nested content (Wine prefixes,
node_modules, game data) as near-zero, so the tool's "Largest Directories"
ranking silently pointed away from what actually filled the disk.
"""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1] / "skills" / "disk-cleaner" / "scripts" / "analyze_disk.py"
)


@pytest.fixture(scope="module")
def analyze_disk():
    spec = importlib.util.spec_from_file_location("analyze_disk_dir_size", str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def analyzer(analyze_disk):
    return analyze_disk.DiskAnalyzer(show_progress=False)


def _write(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(b"\0" * size)


def test_counts_content_nested_below_the_old_depth_cap(analyzer, tmp_path):
    """The bulk of a Wine-prefix-style tree lives 4 levels deep; count all of it."""
    deep = tmp_path / "game" / "drive_c" / "Games" / "Title" / "data.bin"
    _write(deep, 5 * 1024 * 1024)

    size = analyzer._get_dir_size_fast(tmp_path)

    assert size == 5 * 1024 * 1024


def test_matches_total_across_many_depths(analyzer, tmp_path):
    """Sum every file regardless of how deep it sits."""
    _write(tmp_path / "top.bin", 1024)
    _write(tmp_path / "a" / "mid.bin", 2048)
    _write(tmp_path / "a" / "b" / "c" / "deep.bin", 4096)

    size = analyzer._get_dir_size_fast(tmp_path)

    assert size == 1024 + 2048 + 4096


def test_explicit_depth_limit_still_truncates(analyzer, tmp_path):
    """A caller that opts into a shallow estimate keeps the bounded behaviour."""
    _write(tmp_path / "top.bin", 1024)
    _write(tmp_path / "a" / "b" / "deep.bin", 4096)

    # depth 0: only files directly under tmp_path.
    assert analyzer._get_dir_size_fast(tmp_path, max_depth=0) == 1024
    # depth 1: adds the immediate subdirectory's own files, not its grandchildren.
    assert analyzer._get_dir_size_fast(tmp_path, max_depth=1) == 1024
    # depth 2: reaches the file two levels down.
    assert analyzer._get_dir_size_fast(tmp_path, max_depth=2) == 1024 + 4096
