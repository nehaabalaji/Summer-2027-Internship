#!/usr/bin/env python3
"""Collect internships from public employer feeds."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.pipeline import run_update
from board.readme import generate_readme
from scrapers.registry import get_enabled_scrapers


def main() -> int:
    parser = argparse.ArgumentParser(description="Update internship listings")
    parser.add_argument("--all", action="store_true", help="Run every enabled source")
    parser.add_argument("--source", help="Run a single source, e.g. amazon")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and process without writing files")
    args = parser.parse_args()
    scrapers = get_enabled_scrapers(source=args.source) if args.source else get_enabled_scrapers()
    run_update(scrapers, dry_run=args.dry_run)
    if not args.dry_run:
        generate_readme()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
