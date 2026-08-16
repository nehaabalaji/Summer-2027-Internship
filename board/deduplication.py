"""Deduplicate listings by URL first, then company + title + location."""

from __future__ import annotations

from board.models import Job
from board.normalization import normalized_title_key
from board.urls import canonicalize_url


def _fingerprint(job: Job) -> str:
    return "|".join(
        [
            job.company.strip().lower(),
            normalized_title_key(job.title),
            (job.location or "").strip().lower(),
        ]
    )


def deduplicate_jobs(jobs: list[Job]) -> tuple[list[Job], int]:
    """Keep the newest / most complete record for each duplicate group."""
    by_url: dict[str, Job] = {}
    order: list[str] = []
    removed = 0

    def better(existing: Job, incoming: Job) -> Job:
        existing_date = existing.date_posted or ""
        incoming_date = incoming.date_posted or ""
        if incoming_date > existing_date:
            incoming.date_discovered = min(existing.date_discovered, incoming.date_discovered)
            incoming.id = existing.id
            return incoming
        existing.date_discovered = min(existing.date_discovered, incoming.date_discovered)
        if incoming.description and not existing.description:
            existing.description = incoming.description
        return existing

    for job in jobs:
        key = canonicalize_url(job.application_url)
        if not key:
            continue
        if key in by_url:
            by_url[key] = better(by_url[key], job)
            removed += 1
        else:
            by_url[key] = job
            order.append(key)

    by_fp: dict[str, str] = {}
    keep_keys: list[str] = []
    for key in order:
        job = by_url[key]
        fp = _fingerprint(job)
        if fp in by_fp:
            winner_key = by_fp[fp]
            by_url[winner_key] = better(by_url[winner_key], job)
            removed += 1
            continue
        by_fp[fp] = key
        keep_keys.append(key)

    return [by_url[key] for key in keep_keys], removed
