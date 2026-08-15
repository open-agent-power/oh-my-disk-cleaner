"""Behavior tests for the macOS QQ media cleanup helper."""

import os
import platform
import subprocess
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "skills" / "disk-cleaner" / "scripts" / "qq_cleanup_macos.zsh"


def _qq_fixture(tmp_path: Path):
    qq_root = (
        tmp_path
        / "Library"
        / "Containers"
        / "com.tencent.qq"
        / "Data"
        / "Library"
        / "Application Support"
        / "QQ"
    )
    data_root = qq_root / "nt_qq_123" / "nt_data"
    pic_dir = data_root / "Pic"
    emoji_dir = data_root / "Emoji"
    db_dir = qq_root / "nt_qq_123" / "nt_db"

    for directory in (pic_dir, emoji_dir, db_dir):
        directory.mkdir(parents=True)

    old_pic = pic_dir / "old picture.jpg"
    new_pic = pic_dir / "new-picture.jpg"
    old_emoji = emoji_dir / "old-emoji.gif"
    new_emoji = emoji_dir / "new-emoji.gif"
    database = db_dir / "msg.db"

    for path in (old_pic, new_pic, old_emoji, new_emoji, database):
        path.write_bytes(b"fixture")

    old_timestamp = time.time() - 100 * 24 * 60 * 60
    os.utime(old_pic, (old_timestamp, old_timestamp))
    os.utime(old_emoji, (old_timestamp, old_timestamp))

    return old_pic, new_pic, old_emoji, new_emoji, database


def _run_script(tmp_path: Path, *arguments: str):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(exist_ok=True)
    fake_pgrep = fake_bin / "pgrep"
    fake_pgrep.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    fake_pgrep.chmod(0o755)

    env = os.environ.copy()
    env["QQ_CLEANUP_HOME"] = str(tmp_path)
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    return subprocess.run(
        ["/bin/zsh", str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_preview_lists_old_media_without_changing_files(tmp_path):
    old_pic, new_pic, old_emoji, new_emoji, database = _qq_fixture(tmp_path)

    result = _run_script(
        tmp_path,
        "clean",
        "--older-than-days",
        "90",
        "--categories",
        "Pic,Emoji",
    )

    assert result.returncode == 0, result.stderr
    assert "mode=preview" in result.stdout
    assert "files=2" in result.stdout
    assert all(path.exists() for path in (old_pic, new_pic, old_emoji, new_emoji, database))


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_execute_deletes_only_old_pictures_and_emojis(tmp_path):
    old_pic, new_pic, old_emoji, new_emoji, database = _qq_fixture(tmp_path)

    result = _run_script(
        tmp_path,
        "clean",
        "--older-than-days",
        "90",
        "--categories",
        "Pic,Emoji",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    assert "deleted_files=2" in result.stdout
    assert "residual_files=0" in result.stdout
    assert not old_pic.exists()
    assert not old_emoji.exists()
    assert new_pic.exists()
    assert new_emoji.exists()
    assert database.exists()


@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
def test_cleanup_rejects_chat_database_category(tmp_path):
    _qq_fixture(tmp_path)

    result = _run_script(
        tmp_path,
        "clean",
        "--older-than-days",
        "90",
        "--categories",
        "nt_db",
    )

    assert result.returncode != 0
    assert "only Pic and Emoji may be cleaned" in result.stderr


def test_skill_packager_includes_qq_cleanup_script():
    packager = (
        Path(__file__).parents[1] / "skills" / "disk-cleaner" / "scripts" / "package_skill.py"
    ).read_text(encoding="utf-8")

    assert '"scripts/qq_cleanup_macos.zsh"' in packager
