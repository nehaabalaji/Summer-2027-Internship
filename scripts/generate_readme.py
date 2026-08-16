#!/usr/bin/env python3
"""Regenerate README.md from data/jobs.json."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.readme import generate_readme


def main() -> int:
    generate_readme()
    print("README.md updated from data/jobs.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
