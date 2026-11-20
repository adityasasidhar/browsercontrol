"""Tests for scripts/checks/check_max_lines.py."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "checks" / "check_max_lines.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("check_max_lines", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(path: Path, lines: int) -> str:
    path.write_text("x\n" * lines, encoding="utf-8")
    return str(path)


def test_file_at_limit_passes(tmp_path: Path) -> None:
    assert _load().main(["--max-lines=5", _write(tmp_path / "a.py", 5)]) == 0


def test_file_over_limit_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = _write(tmp_path / "a.py", 6)
    assert _load().main(["--max-lines=5", target]) == 1
    assert target in capsys.readouterr().out


def test_missing_file_is_skipped(tmp_path: Path) -> None:
    assert _load().main(["--max-lines=5", str(tmp_path / "gone.py")]) == 0


def test_binary_file_is_skipped(tmp_path: Path) -> None:
    binary = tmp_path / "b.bin"
    binary.write_bytes(b"\xff\xfe\x00" * 100)
    assert _load().main(["--max-lines=1", str(binary)]) == 0
