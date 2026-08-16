#!/usr/bin/env python3
"""Expire stale listings using scraper status — never because of a one-off failure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.config import path_from_settings
from board.expiration import expire_missing_jobs
from board.storage import JsonJobRepository, load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    status = load_json(path_from_settings("status"), {"sources": {}})
    successful = {
        name
        for name, entry in (status.get("sources") or {}).items()
        if entry.get("status") == "ok"
    }
    repo = JsonJobRepository()
    jobs, expired = expire_missing_jobs(repo.load(), {}, successful)
    print(f"Expired: {expired}")
    if args.write:
        repo.save(jobs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
