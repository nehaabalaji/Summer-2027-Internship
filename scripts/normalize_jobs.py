#!/usr/bin/env python3
"""Re-normalize jobs already stored in data/jobs.json (does not scrape)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.normalization import (
    infer_job_type,
    infer_work_arrangement,
    normalize_application_url,
    normalize_company,
    normalize_title,
    normalized_title_key,
    parse_location,
)
from board.storage import JsonJobRepository


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = JsonJobRepository()
    jobs = repo.load()
    for job in jobs:
        job.company = normalize_company(job.company)
        job.title = normalize_title(job.title)
        job.normalized_title = normalized_title_key(job.title)
        parsed = parse_location(job.location)
        job.location = parsed["location"] or job.location
        job.city = parsed["city"] or job.city
        job.state = parsed["state"] or job.state
        job.country = parsed["country"] or job.country
        job.job_type = infer_job_type(job.title, job.job_type)
        job.work_arrangement = infer_work_arrangement(job.location, job.work_arrangement, job.description)
        job.application_url = normalize_application_url(job.application_url)
    if args.write:
        repo.save(jobs)
        print(f"Normalized {len(jobs)} jobs")
    else:
        print(f"Normalized {len(jobs)} jobs in memory. Re-run with --write to save.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
