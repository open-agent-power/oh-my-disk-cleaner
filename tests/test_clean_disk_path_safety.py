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


def test_recursive_selection_preserves_protected_extensions(clean_disk, tmp_path):
    preview_root = tmp_path / "preview"
    execute_root = tmp_path / "execute"
    for root in (preview_root, execute_root):
        payload = root / "payload"
        payload.mkdir(parents=True)
        (payload / "data.bin").write_bytes(b"x" * (2 * 1024 * 1024))
        (payload / "keep.sh").write_text("echo keep", encoding="utf-8")

    preview = clean_disk.DiskCleaner(dry_run=True, show_progress=False).clean_directory(
        str(preview_root)
    )
    execution = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(
        str(execute_root)
    )

    assert preview["files_deleted"] == execution["files_deleted"] == 0
    assert preview["space_freed_mb"] == execution["space_freed_mb"] == 0.0
    assert (preview_root / "payload" / "data.bin").exists()
    assert (preview_root / "payload" / "keep.sh").exists()
    assert (execute_root / "payload" / "data.bin").exists()
    assert (execute_root / "payload" / "keep.sh").exists()


def test_recursive_selection_preserves_directories_containing_links(clean_disk, tmp_path):
    root = tmp_path / "cache"
    payload = root / "payload"
    payload.mkdir(parents=True)
    (payload / "data.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    target = tmp_path / "target"
    target.mkdir()
    linked = payload / "linked"
    try:
        linked.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Cannot create a test directory symlink: {error}")

    result = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(str(root))

    assert result["files_deleted"] == 0
    assert result["space_freed_mb"] == 0.0
    assert result["errors"] == []
    assert (payload / "data.bin").exists()
    assert linked.is_symlink()


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
    assert len(result["errors"]) == 1
    assert result["errors"][0].endswith("nested: delete failed")
    assert nested.exists()


def test_partial_plan_failure_reports_success_and_continues(clean_disk, tmp_path, monkeypatch):
    root = tmp_path / "cache"
    blocked = root / "blocked"
    blocked.mkdir(parents=True)
    (blocked / "payload.bin").write_bytes(b"b" * (2 * 1024 * 1024))
    removed = root / "removed.bin"
    removed.write_bytes(b"r" * (1 * 1024 * 1024))
    original_rmtree = clean_disk.shutil.rmtree

    def fail_one_tree(path):
        if path == blocked:
            raise OSError("delete failed")
        original_rmtree(path)

    monkeypatch.setattr(clean_disk.shutil, "rmtree", fail_one_tree)
    result = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(str(root))

    assert result["files_deleted"] == 1
    assert result["space_freed_mb"] == 1.0
    assert len(result["errors"]) == 1
    assert any(error.startswith(str(blocked)) for error in result["errors"])
    assert blocked.exists()
    assert not removed.exists()


def test_plan_execution_treats_missing_entries_as_idempotent_success(clean_disk, tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    removed_elsewhere = cache / "removed-elsewhere.bin"
    removed_elsewhere.write_bytes(b"x" * (2 * 1024 * 1024))
    remaining = cache / "remaining.bin"
    remaining.write_bytes(b"r" * (1 * 1024 * 1024))
    cleaner = clean_disk.DiskCleaner(dry_run=False, show_progress=False)
    removed_operations, removed_selected = cleaner._build_deletion_plan(removed_elsewhere)
    remaining_operations, remaining_selected = cleaner._build_deletion_plan(remaining)

    removed_elsewhere.unlink()
    freed_bytes, removed_any, errors = cleaner._execute_deletion_plan(
        removed_operations + remaining_operations
    )

    assert removed_selected is True
    assert remaining_selected is True
    assert freed_bytes == 1 * 1024 * 1024
    assert removed_any is True
    assert errors == []
    assert not remaining.exists()


def test_plan_build_treats_a_missing_leaf_as_idempotent_success(clean_disk, tmp_path, monkeypatch):
    payload = tmp_path / "cache" / "payload.bin"
    payload.parent.mkdir()
    payload.write_bytes(b"x")
    original_lstat = Path.lstat

    def remove_before_lstat(path):
        if path == payload:
            path.unlink()
            raise FileNotFoundError(path)
        return original_lstat(path)

    monkeypatch.setattr(Path, "lstat", remove_before_lstat)
    operations, fully_selected = clean_disk.DiskCleaner(
        dry_run=True, show_progress=False
    )._build_deletion_plan(payload)

    assert operations == []
    assert fully_selected is True


def test_plan_build_treats_a_missing_directory_as_idempotent_success(
    clean_disk, tmp_path, monkeypatch
):
    payload = tmp_path / "cache" / "payload"
    payload.mkdir(parents=True)
    original_scandir = os.scandir

    def remove_before_scandir(path):
        if Path(path) == payload:
            payload.rmdir()
            raise FileNotFoundError(path)
        return original_scandir(path)

    monkeypatch.setattr(os, "scandir", remove_before_scandir)
    operations, fully_selected = clean_disk.DiskCleaner(
        dry_run=True, show_progress=False
    )._build_deletion_plan(payload)

    assert operations == []
    assert fully_selected is True


def test_directory_replaced_by_symlink_never_deletes_the_link_target(
    clean_disk, tmp_path, monkeypatch
):
    root = tmp_path / "cache"
    payload = root / "payload"
    payload.mkdir(parents=True)
    local_file = payload / "local.bin"
    local_file.write_bytes(b"local")
    target = tmp_path / "target"
    target.mkdir()
    external_file = target / "external.bin"
    external_file.write_bytes(b"external")
    probe = root / "symlink-probe"
    try:
        probe.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Cannot create a test directory symlink: {error}")
    probe.unlink()

    original_scandir = os.scandir
    replaced = False

    def replace_before_traversal(path):
        nonlocal replaced
        if not replaced and isinstance(path, (str, bytes, os.PathLike)) and Path(path) == payload:
            replaced = True
            local_file.unlink()
            payload.rmdir()
            payload.symlink_to(target, target_is_directory=True)
        return original_scandir(path)

    monkeypatch.setattr(os, "scandir", replace_before_traversal)
    cleaner = clean_disk.DiskCleaner(dry_run=False, show_progress=False)
    operations, fully_selected = cleaner._build_deletion_plan(payload)
    freed_bytes, removed_any, errors = cleaner._execute_deletion_plan(operations)

    assert fully_selected is True
    assert operations[0][1] == "rmtree"
    assert freed_bytes == 0
    assert removed_any is False
    assert len(errors) == 1
    assert payload.is_symlink()
    assert external_file.read_bytes() == b"external"


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


def test_directory_symlink_is_removed_as_a_leaf(clean_disk, tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    target = tmp_path / "target"
    nested = target / "nested"
    nested.mkdir(parents=True)
    payload = nested / "payload.bin"
    payload.write_bytes(b"x" * (2 * 1024 * 1024))
    link = root / "linked-cache"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"Cannot create a test directory symlink: {error}")

    cleaner = clean_disk.DiskCleaner(dry_run=True, show_progress=False)
    operations, fully_selected = cleaner._build_deletion_plan(link)

    assert fully_selected is True
    assert operations == [(link, "unlink", link.lstat().st_size)]

    execution = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(
        str(root)
    )
    assert execution["errors"] == []
    assert not link.exists()
    assert payload.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows junction semantics")
def test_windows_junction_is_removed_as_a_leaf(clean_disk, tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    target = tmp_path / "target"
    nested = target / "nested"
    nested.mkdir(parents=True)
    payload = nested / "payload.bin"
    payload.write_bytes(b"x" * (2 * 1024 * 1024))
    junction = root / "junction"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        pytest.skip(f"Cannot create a test junction: {created.stderr.strip()}")

    cleaner = clean_disk.DiskCleaner(dry_run=True, show_progress=False)
    operations, fully_selected = cleaner._build_deletion_plan(junction)
    preview = cleaner.clean_directory(str(root))

    assert fully_selected is True
    assert operations == [(junction, "rmdir", junction.lstat().st_size)]
    assert preview["space_freed_mb"] == round(junction.lstat().st_size / (1024 * 1024), 2)

    execution = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(
        str(root)
    )
    assert execution["errors"] == []
    assert not junction.exists()
    assert payload.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows junction semantics")
def test_directory_containing_a_windows_junction_is_retained(clean_disk, tmp_path):
    root = tmp_path / "cache"
    candidate = root / "candidate"
    candidate.mkdir(parents=True)
    local_file = candidate / "local.bin"
    local_file.write_bytes(b"local")
    target = tmp_path / "target"
    target.mkdir()
    external_file = target / "external.bin"
    external_file.write_bytes(b"external")
    junction = candidate / "junction"
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
    )
    if created.returncode != 0:
        pytest.skip(f"Cannot create a test junction: {created.stderr.strip()}")

    result = clean_disk.DiskCleaner(dry_run=False, show_progress=False).clean_directory(str(root))

    assert result["files_deleted"] == 0
    assert result["space_freed_mb"] == 0.0
    assert result["errors"] == []
    assert local_file.exists()
    assert junction.exists()
    assert external_file.read_bytes() == b"external"


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
