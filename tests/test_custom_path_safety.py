"""Safety-gate tests for clean_disk.py --path hardening (issue #9).

The skill script lives under skills/disk-cleaner/scripts/ and is not an
importable package, so these tests load it directly via importlib and exercise
the new ``validate_custom_path`` gate plus the recursive dry-run sizing.
"""

import importlib.util
import os
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1] / "skills" / "disk-cleaner" / "scripts" / "clean_disk.py"
)


@pytest.fixture(scope="module")
def clean_disk():
    spec = importlib.util.spec_from_file_location("clean_disk_mod", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def cleaner(clean_disk):
    return clean_disk.DiskCleaner(dry_run=True, show_progress=False)


@pytest.fixture
def err(clean_disk):
    """The UnsafePathError class (module-level, not on the instance)."""
    return clean_disk.UnsafePathError


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Redirect os.path.expanduser('~') at a temp dir so the home/profile root
    protection is testable without touching the real home directory."""
    home = tmp_path / "myhome"
    home.mkdir()
    original_expanduser = os.path.expanduser

    def patched(p):
        return str(home) if p == "~" else original_expanduser(p)

    monkeypatch.setattr(os.path, "expanduser", patched)
    return home


# --- Filesystem / home root rejection ---------------------------------------


def test_filesystem_root_rejected(cleaner, err):
    with pytest.raises(err):
        cleaner.validate_custom_path("/")


def test_is_filesystem_root_handles_posix_and_drive_roots(cleaner):
    # POSIX root is always recognised.
    assert cleaner._is_filesystem_root(Path("/"))
    assert not cleaner._is_filesystem_root(Path("/Users"))
    assert not cleaner._is_filesystem_root(Path("/tmp"))
    # Drive roots are recognised on Windows. On POSIX os.path.splitdrive does
    # not parse "C:", so only assert the Windows behaviour there.
    if os.name == "nt":
        assert cleaner._is_filesystem_root(Path("C:\\"))
        assert cleaner._is_filesystem_root(Path("D:\\"))


def test_home_root_rejected(cleaner, fake_home, err):
    with pytest.raises(err):
        cleaner.validate_custom_path(str(fake_home))


def test_home_subdirectory_still_allowed(cleaner, fake_home):
    cache = fake_home / ".cache"
    cache.mkdir()
    # A junk-looking subdir of home must pass: the root rule only blocks the
    # exact home directory, not its children.
    assert cleaner.validate_custom_path(str(cache)) == str(cache.resolve())


# --- Non-junk opt-in --------------------------------------------------------


def test_non_junk_path_requires_opt_in(cleaner, tmp_path, err):
    target = tmp_path / "projects" / "myapp"
    target.mkdir(parents=True)
    with pytest.raises(err):
        cleaner.validate_custom_path(str(target))


def test_non_junk_path_allowed_with_unsafe_opt_in(cleaner, tmp_path):
    target = tmp_path / "projects" / "myapp"
    target.mkdir(parents=True)
    resolved = str(target.resolve())
    assert (
        cleaner.validate_custom_path(resolved, force=True, allow_unsafe=True, confirm_path=resolved)
        == resolved
    )


# --- force requires exact --confirm-path ------------------------------------


def test_force_without_confirm_rejected(cleaner, tmp_path, err):
    target = tmp_path / "projects"
    target.mkdir()
    with pytest.raises(err):
        cleaner.validate_custom_path(str(target), force=True, allow_unsafe=True)


def test_confirm_path_mismatch_rejected(cleaner, tmp_path, err):
    target = tmp_path / "projects"
    target.mkdir()
    with pytest.raises(err):
        cleaner.validate_custom_path(
            str(target), force=True, allow_unsafe=True, confirm_path=str(tmp_path)
        )


def test_confirm_path_match_accepted(cleaner, tmp_path):
    target = tmp_path / "projects"
    target.mkdir()
    resolved = str(target.resolve())
    assert (
        cleaner.validate_custom_path(resolved, force=True, allow_unsafe=True, confirm_path=resolved)
        == resolved
    )


# --- Recursive dry-run sizing ----------------------------------------------


def test_dry_run_recursive_size(cleaner, tmp_path):
    cache = tmp_path / "cache"
    nested = cache / "deep" / "deeper"
    nested.mkdir(parents=True)
    # 5 MiB nested inside subdirectories; a non-recursive stat of the parent
    # directory entry would be ~0 bytes.
    (nested / "blob.bin").write_bytes(b"x" * (5 * 1024 * 1024))

    result = cleaner.clean_directory(str(cache), show_progress=False)
    assert result["space_freed_mb"] > 4.0


def test_hidden_junk_dirs_match(cleaner, tmp_path):
    """Hidden junk dirs (~/.cache, ~/.Trash) must be recognised after the
    leading dot is stripped from each path segment."""
    for name in (".cache", ".Trash", ".tmp"):
        d = tmp_path / name
        d.mkdir()
        assert cleaner.validate_custom_path(str(d)) == str(d.resolve())
