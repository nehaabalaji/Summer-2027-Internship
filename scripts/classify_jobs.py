#!/usr/bin/env python3
"""Classify jobs already stored in data/jobs.json (does not scrape)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.classification import classify_text
from board.storage import JsonJobRepository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Save updated categories")
    args = parser.parse_args()
    repo = JsonJobRepository()
    jobs = repo.load()
    changed = 0
    for job in jobs:
        result = classify_text(job.title, job.description)
        if job.category != result.category or job.category_confidence != result.confidence:
            changed += 1
        job.category = result.category
        job.category_confidence = result.confidence
        job.subcategory = result.subcategory
        job.needs_review = result.needs_review
        print(f"{job.company} | {job.title} -> {result.category} ({result.confidence:.2f})")
    if args.write:
        repo.save(jobs)
        print(f"Wrote {changed} category updates")
    else:
        print(f"{changed} jobs would change. Re-run with --write to save.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
