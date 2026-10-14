"""Tests for ai-screenshot CLI."""

from __future__ import annotations

import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ai_screenshot import cli


class FakeRunResult:
    def __init__(self, returncode: int, stderr: str = ""):
        self.returncode = returncode
        self.stderr = stderr


# ── 1. 文件名生成 ────────────────────────────────────────────────────────


def test_timestamp_filename_format_and_no_colon(monkeypatch) -> None:
    class _FakeNow:
        def strftime(self, fmt: str) -> str:
            return "2026-07-10T09-41-23-123456"

    class _FakeDateTime:
        @classmethod
        def now(cls) -> _FakeNow:
            return _FakeNow()

    class _FakeDatetimeModule:
        datetime = _FakeDateTime

    monkeypatch.setattr(cli, "datetime", _FakeDatetimeModule())
    monkeypatch.setattr(cli.secrets, "token_hex", lambda n: "a" * (n * 2))
    filename = cli._timestamp_filename()
    assert filename == "screenshot-2026-07-10T09-41-23-123456-aaaaaa.png"
    assert ":" not in filename


# ── 2. 失败路径（mock） ──────────────────────────────────────────────────


def test_capture_fails_when_display_missing(monkeypatch, capsys) -> None:
    monkeypatch.delenv("DISPLAY", raising=False)
    assert cli.capture() is None
    rc = cli.main()
    assert rc == 1
    err = capsys.readouterr().err
    assert "[error]" in err
    assert "DISPLAY" in err


def test_capture_fails_when_import_binary_missing(monkeypatch, capsys) -> None:
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(shutil, "which", lambda _bin: None)
    assert cli.capture() is None
    rc = cli.main()
    assert rc == 1
    err = capsys.readouterr().err
    assert "[error]" in err
    assert "imagemagick" in err


def test_capture_fails_when_subprocess_returns_nonzero(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(shutil, "which", lambda _bin: "/usr/bin/import")
    monkeypatch.setattr(cli, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(cli, "_timestamp_filename", lambda: "test.png")

    def _fake_run(*args: Any, **kwargs: Any) -> FakeRunResult:
        return FakeRunResult(1, "no display name")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    assert cli.capture() is None
    rc = cli.main()
    assert rc == 1
    err = capsys.readouterr().err
    assert "[error]" in err
    assert "退出码 1" in err
    assert "no display name" in err


def test_capture_fails_when_output_file_is_empty(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(shutil, "which", lambda _bin: "/usr/bin/import")
    monkeypatch.setattr(cli, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(cli, "_timestamp_filename", lambda: "test.png")

    def _fake_run(*args: Any, **kwargs: Any) -> FakeRunResult:
        path = args[0][-1]
        Path(path).write_bytes(b"")
        return FakeRunResult(0, "")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    assert cli.capture() is None
    err = capsys.readouterr().err
    assert "[error]" in err
    assert "输出文件无效" in err


# ── 3. 成功路径 & 目录创建 ───────────────────────────────────────────────


def test_capture_creates_output_directory_and_returns_path(monkeypatch, tmp_path: Path) -> None:
    output_dir = tmp_path / "new" / "screenshots"
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setattr(shutil, "which", lambda _bin: "/usr/bin/import")
    monkeypatch.setattr(cli, "OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr(cli, "_timestamp_filename", lambda: "test.png")

    def _fake_run(*args: Any, **kwargs: Any) -> FakeRunResult:
        path = args[0][-1]
        output_dir.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"not empty")
        return FakeRunResult(0, "")

    monkeypatch.setattr(subprocess, "run", _fake_run)
    path = cli.capture()
    assert path == str(output_dir / "test.png")
    assert output_dir.exists()
    assert os.path.getsize(path) > 0


# ── 4. 真实端到端测试 ────────────────────────────────────────────────────


@pytest.mark.real
def test_real_screenshot_produces_valid_png() -> None:
    # Run the module from this interpreter so the test exercises this checkout,
    # not whatever `ai-screenshot` happens to be on PATH.
    result = subprocess.run(
        [sys.executable, "-m", "ai_screenshot.cli"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    path = result.stdout.strip()
    output_dir = os.path.expanduser("~/Pictures/screenshots/")
    assert path.startswith(output_dir + "screenshot-")
    assert path.endswith(".png")
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

    identify = subprocess.run(["identify", path], capture_output=True, text=True)
    assert identify.returncode == 0, identify.stderr
    assert "PNG" in identify.stdout
    parts = identify.stdout.split()
    size = parts[2]
    width, height = (int(x) for x in size.split("x"))
    # Screen size varies between machines, so only check that something was captured.
    assert width > 0
    assert height > 0
