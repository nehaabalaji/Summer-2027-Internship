"""Expire listings only with strong evidence, never because one request failed."""

from __future__ import annotations

from board.config import settings
from board.http import check_url
from board.models import Job


def expire_missing_jobs(
    existing: list[Job],
    seen_ids_by_source: dict[str, set[str]],
    successful_sources: set[str],
) -> tuple[list[Job], int]:
    """Mark jobs inactive after repeated absences from a successful source run."""
    threshold = int(settings()["pipeline"]["expire_after_consecutive_misses"])
    expired = 0
    updated: list[Job] = []
    for job in existing:
        if not job.active:
            updated.append(job)
            continue
        source_key = job.source_key
        if source_key not in successful_sources:
            updated.append(job)
            continue
        if source_key not in seen_ids_by_source:
            updated.append(job)
            continue
        seen = seen_ids_by_source[source_key]
        if job.id in seen:
            job.consecutive_misses = 0
            updated.append(job)
            continue
        job.consecutive_misses += 1
        if job.consecutive_misses >= threshold:
            job.active = False
            expired += 1
        updated.append(job)
    return updated, expired


def verify_application_url(url: str) -> str:
    """ACTIVE | TEMPORARY_ERROR | NOT_FOUND | UNKNOWN."""
    return check_url(url)
