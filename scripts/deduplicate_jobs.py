#!/usr/bin/env python3
"""Deduplicate jobs already stored in data/jobs.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.deduplication import deduplicate_jobs
from board.storage import JsonJobRepository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = JsonJobRepository()
    jobs, removed = deduplicate_jobs(repo.load())
    print(f"Duplicates removed: {removed}. Remaining: {len(jobs)}")
    if args.write:
        repo.save(jobs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
