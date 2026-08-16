#!/usr/bin/env python3
"""CLI entry point for the internship board."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board.pipeline import run_update
from board.readme import generate_readme
from board.storage import JsonJobRepository
from board.validation import JobValidationError, assert_jobs_valid
from scrapers.registry import get_enabled_scrapers


def cmd_update(args: argparse.Namespace) -> int:
    if args.source:
        scrapers = get_enabled_scrapers(source=args.source)
    else:
        scrapers = get_enabled_scrapers()
    report = run_update(scrapers, dry_run=args.dry_run)
    if not args.dry_run:
        generate_readme()
    return 0 if report.sources_attempted else 1


def cmd_validate(_: argparse.Namespace) -> int:
    jobs = JsonJobRepository().load()
    try:
        assert_jobs_valid([job for job in jobs if job.active])
    except JobValidationError as exc:
        print(exc)
        return 1
    print(f"OK: {sum(1 for job in jobs if job.active)} active jobs validated")
    return 0


def cmd_readme(_: argparse.Namespace) -> int:
    generate_readme()
    print("README.md updated")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supply Chain internships board")
    sub = parser.add_subparsers(dest="command", required=True)
    update = sub.add_parser("update", help="Collect, normalize, and store jobs")
    update.add_argument("--all", action="store_true", help="Run every enabled source")
    update.add_argument("--source", help="Run a single source id")
    update.add_argument("--dry-run", action="store_true", help="Do not write production files")
    update.set_defaults(func=cmd_update)
    validate = sub.add_parser("validate", help="Validate production jobs.json")
    validate.set_defaults(func=cmd_validate)
    readme = sub.add_parser("generate-readme", help="Regenerate README from jobs.json")
    readme.set_defaults(func=cmd_readme)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
