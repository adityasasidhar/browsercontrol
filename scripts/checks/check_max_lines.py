"""Fail when a text file exceeds a maximum number of lines."""

import argparse
import sys
from pathlib import Path


def count_lines(path: Path) -> int | None:
    """Return the line count of a UTF-8 text file, or None if unreadable."""
    try:
        with path.open(encoding="utf-8") as handle:
            return sum(1 for _ in handle)
    except (OSError, UnicodeDecodeError):
        return None


def main(argv: list[str] | None = None) -> int:
    """Return 1 if any given file is longer than ``--max-lines``, else 0."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-lines", type=int, default=800)
    parser.add_argument("files", nargs="*")
    args = parser.parse_args(argv)

    failed = False
    for name in args.files:
        lines = count_lines(Path(name))
        if lines is not None and lines > args.max_lines:
            print(f"{name}: {lines} lines (max {args.max_lines})")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
