#!/usr/bin/env python3
"""Validate production job data. Exits non-zero when invalid records exist."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.storage import JsonJobRepository
from board.validation import JobValidationError, assert_jobs_valid, validate_job


def main() -> int:
    jobs = JsonJobRepository().load()
    active = [job for job in jobs if job.active]
    try:
        assert_jobs_valid(active)
    except JobValidationError as exc:
        print(exc)
        return 1
    inactive_problems = 0
    for job in jobs:
        if job.active:
            continue
        errors = validate_job(job)
        if errors:
            inactive_problems += 1
    print(f"OK: {len(active)} active jobs validated ({len(jobs) - len(active)} inactive)")
    if inactive_problems:
        print(f"Note: {inactive_problems} inactive records have validation warnings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
