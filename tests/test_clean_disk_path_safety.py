import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1] / "skills" / "disk-cleaner" / "scripts" / "clean_disk.py"
)


@pytest.fixture(scope="module")
def clean_disk():
    spec = importlib.util.spec_from_file_location("clean_disk_path_safety", str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cleaner(clean_disk):
    return clean_disk.DiskCleaner(dry_run=True, show_progress=False)


def make_tree(root):
    nested = root / "objects" / "nested"
    nested.mkdir(parents=True)
    (nested / "payload.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    (root / "small.txt").write_text("small", encoding="utf-8")
    (root / "keep.sh").write_text("echo keep", encoding="utf-8")


def test_filesystem_and_home_roots_are_refused(clean_disk, cleaner, tmp_path, monkeypatch):
    filesystem_root = Path(Path.cwd().anchor)
    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(str(filesystem_root), allow_unsafe=True)

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(os.path, "expanduser", lambda path: str(home) if path == "~" else path)
    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(str(home), allow_unsafe=True)

    cache = home / ".cache"
    cache.mkdir()
    assert cleaner.validate_custom_path(str(cache)) == str(cache.resolve())


def test_clean_directory_refuses_a_protected_root(clean_disk, tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    child = home / "keep.txt"
    child.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(os.path, "expanduser", lambda path: str(home) if path == "~" else path)

    result = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(str(home))

    assert result["files_deleted"] == 0
    assert len(result["errors"]) == 1
    assert child.exists()


def test_protected_path_comparison_respects_component_boundaries(cleaner, tmp_path):
    protected = tmp_path / "usr"
    protected.mkdir()
    child = protected / "cache"
    child.mkdir()
    sibling = tmp_path / "usr-local"
    sibling.mkdir()
    cleaner.protected_paths = {str(protected)}

    assert cleaner._is_safe_to_delete(child) is False
    assert cleaner._is_safe_to_delete(sibling) is True


def test_custom_path_uses_the_target_name(clean_disk, cleaner, tmp_path):
    project = tmp_path / "projects" / "app"
    project.mkdir(parents=True)

    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(str(project))

    cache = tmp_path / "cache"
    cache.mkdir()
    assert cleaner.validate_custom_path(str(cache)) == str(cache.resolve())


def test_project_marker_keeps_a_junk_named_project_gated(clean_disk, cleaner, tmp_path):
    project = tmp_path / "cache"
    (project / ".git").mkdir(parents=True)

    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(str(project))
    assert cleaner.validate_custom_path(str(project), allow_unsafe=True) == str(project.resolve())


def test_force_requires_the_resolved_absolute_path(clean_disk, cleaner, tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    resolved = str(cache.resolve())

    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(resolved, force=True)
    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(resolved, force=True, confirm_path="cache")
    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(resolved, force=True, confirm_path=str(tmp_path))
    assert cleaner.validate_custom_path(resolved, force=True, confirm_path=resolved) == resolved


def test_preview_and_execution_share_selection_and_size(clean_disk, tmp_path):
    preview_root = tmp_path / "preview"
    execute_root = tmp_path / "execute"
    make_tree(preview_root)
    make_tree(execute_root)

    preview = clean_disk.DiskCleaner(dry_run=True, show_progress=False).clean_directory(
        str(preview_root)
    )
    execution = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(
        str(execute_root)
    )

    assert preview["files_deleted"] == execution["files_deleted"] == 2
    assert preview["space_freed_mb"] == execution["space_freed_mb"] == 2.0
    assert (preview_root / "objects" / "nested" / "payload.bin").exists()
    assert (execute_root / "keep.sh").exists()
    assert sorted(path.name for path in execute_root.iterdir()) == ["keep.sh"]


def test_recursive_size_drives_max_size_filter(clean_disk, tmp_path):
    root = tmp_path / "cache"
    make_tree(root)

    result = clean_disk.DiskCleaner(dry_run=True, show_progress=False).clean_directory(
        str(root), max_size_mb=1
    )

    assert result["files_deleted"] == 1
    assert result["space_freed_mb"] == 0.0


def test_recursive_delete_failure_is_reported(clean_disk, tmp_path, monkeypatch):
    root = tmp_path / "cache"
    nested = root / "nested"
    nested.mkdir(parents=True)

    def fail_delete(path):
        raise OSError("delete failed")

    monkeypatch.setattr(clean_disk.shutil, "rmtree", fail_delete)
    result = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(str(root))

    assert result["files_deleted"] == 0
    assert result["errors"] == ["delete failed"]
    assert nested.exists()


def test_cli_requires_opt_in_and_exact_confirmation(tmp_path):
    project = tmp_path / "project"
    make_tree(project)
    command = [sys.executable, str(SCRIPT), "--path", str(project), "--json", "--no-progress"]

    refused = subprocess.run(command, capture_output=True, text=True)
    assert refused.returncode == 2
    assert "--allow-unsafe-path" in refused.stderr

    preview = subprocess.run(command + ["--allow-unsafe-path"], capture_output=True, text=True)
    assert preview.returncode == 0
    assert json.loads(preview.stdout)["summary"]["total_space_freed_mb"] == 2.0
    assert (project / "objects").exists()

    unconfirmed = subprocess.run(
        command + ["--allow-unsafe-path", "--force"], capture_output=True, text=True
    )
    assert unconfirmed.returncode == 2
    assert "--confirm-path" in unconfirmed.stderr
    assert (project / "objects").exists()

    confirmed = subprocess.run(
        command + ["--allow-unsafe-path", "--force", "--confirm-path", str(project.resolve())],
        capture_output=True,
        text=True,
    )
    assert confirmed.returncode == 0
    assert json.loads(confirmed.stdout)["summary"]["total_space_freed_mb"] == 2.0
    assert sorted(path.name for path in project.iterdir()) == ["keep.sh"]
