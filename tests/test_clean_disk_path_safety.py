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
    validated, _ = cleaner.validate_custom_path(str(cache))
    assert validated == str(cache.resolve())


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
    validated, _ = cleaner.validate_custom_path(str(cache))
    assert validated == str(cache.resolve())


def test_project_marker_keeps_a_junk_named_project_gated(clean_disk, cleaner, tmp_path):
    project = tmp_path / "cache"
    (project / ".git").mkdir(parents=True)

    with pytest.raises(clean_disk.UnsafePathError):
        cleaner.validate_custom_path(str(project))
    validated, _ = cleaner.validate_custom_path(str(project), allow_unsafe=True)
    assert validated == str(project.resolve())


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
    validated, _ = cleaner.validate_custom_path(resolved, force=True, confirm_path=resolved)
    assert validated == resolved


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


def test_recursive_size_does_not_follow_a_directory_symlink(clean_disk, tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    local_file = root / "local.bin"
    local_file.write_bytes(b"local")
    target = tmp_path / "target"
    target.mkdir()
    (target / "external.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    link = root / "linked"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Cannot create a test directory symlink: {error}")

    measured = clean_disk.DiskCleaner(show_progress=False)._item_size(root)

    assert measured == local_file.stat().st_size + link.lstat().st_size


@pytest.mark.skipif(os.name != "nt", reason="Windows junction semantics")
def test_recursive_size_treats_a_windows_junction_as_a_leaf(clean_disk, tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    target = tmp_path / "target"
    target.mkdir()
    (target / "external.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    junction = root / "junction"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        pytest.skip(f"Cannot create a test junction: {created.stderr.strip()}")

    measured = clean_disk.DiskCleaner(show_progress=False)._item_size(root)

    assert measured == junction.lstat().st_size


def test_custom_path_identity_is_rechecked_during_validation(clean_disk, tmp_path, monkeypatch):
    cache = tmp_path / "cache"
    cache.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    cleaner = clean_disk.DiskCleaner(show_progress=False)
    replaced = False

    def replace_after_initial_stat(path):
        nonlocal replaced
        if not replaced:
            replaced = True
            cache.rmdir()
            cache.symlink_to(project, target_is_directory=True)
        return False

    monkeypatch.setattr(cleaner, "_is_protected_root", replace_after_initial_stat)

    with pytest.raises(clean_disk.UnsafePathError, match="changed during validation"):
        cleaner.validate_custom_path(str(cache))


def test_custom_path_identity_is_checked_between_stat_and_resolve(
    clean_disk, tmp_path, monkeypatch
):
    cache = tmp_path / "cache"
    cache.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    original_resolve = Path.resolve
    replaced = False

    def replace_before_resolve(path, *args, **kwargs):
        nonlocal replaced
        if path == cache and not replaced:
            replaced = True
            cache.rmdir()
            cache.symlink_to(project, target_is_directory=True)
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", replace_before_resolve)
    cleaner = clean_disk.DiskCleaner(show_progress=False)

    with pytest.raises(clean_disk.UnsafePathError, match="changed during validation"):
        cleaner.validate_custom_path(str(cache))


def test_clean_directory_rejects_a_replaced_custom_root(clean_disk, tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    project = tmp_path / "project"
    project.mkdir()
    source = project / "source.py"
    source.write_text("preserve", encoding="utf-8")
    cleaner = clean_disk.DiskCleaner(dry_run=False, show_progress=False)
    validated_path, identity = cleaner.validate_custom_path(str(cache))

    cache.rmdir()
    try:
        cache.symlink_to(project, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Cannot create a test directory symlink: {error}")
    result = cleaner.clean_directory(validated_path, expected_identity=identity)

    assert result["files_deleted"] == 0
    assert len(result["errors"]) == 1
    assert "changed after validation" in result["errors"][0]
    assert source.read_text(encoding="utf-8") == "preserve"


def test_cli_exits_nonzero_after_writing_an_error_report(clean_disk, tmp_path, monkeypatch, capsys):
    cache = tmp_path / "cache"
    cache.mkdir()
    report = tmp_path / "report.json"

    def fail_clean_directory(self, path, **kwargs):
        return {
            "path": path,
            "files_deleted": 0,
            "space_freed_mb": 0,
            "errors": ["delete failed"],
        }

    monkeypatch.setattr(clean_disk.DiskCleaner, "clean_directory", fail_clean_directory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--path",
            str(cache),
            "--force",
            "--confirm-path",
            str(cache.resolve()),
            "--json",
            "--no-progress",
            "--output",
            str(report),
        ],
    )

    with pytest.raises(SystemExit) as exit_info:
        clean_disk.main()

    assert exit_info.value.code == 1
    assert json.loads(report.read_text(encoding="utf-8"))["summary"]["total_errors"] == 1
    assert '"total_errors": 1' in capsys.readouterr().out


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
