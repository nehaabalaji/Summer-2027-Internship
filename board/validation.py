"""Reject incomplete or fabricated job records before they enter production data."""

from __future__ import annotations

from urllib.parse import urlsplit

from board.constants import CATEGORIES, JOB_TYPES
from board.models import Job
from board.urls import is_placeholder_url


class JobValidationError(ValueError):
    pass


def validate_job(job: Job | dict) -> list[str]:
    errors: list[str] = []
    data = job.model_dump() if isinstance(job, Job) else job
    for field in ("id", "company", "title", "location", "category", "job_type", "application_url", "source"):
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing {field}")
    url = str(data.get("application_url") or "").strip()
    if url:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            errors.append("invalid application_url")
        elif is_placeholder_url(url):
            errors.append("placeholder application_url")
    category = data.get("category")
    if category and category not in CATEGORIES:
        errors.append(f"invalid category: {category}")
    job_type = data.get("job_type")
    if job_type and job_type not in JOB_TYPES:
        errors.append(f"invalid job_type: {job_type}")
    if data.get("seed") and data.get("active"):
        errors.append("seed data cannot be marked active in production")
    return errors


def assert_jobs_valid(jobs: list[Job]) -> None:
    problems: list[str] = []
    seen_ids: set[str] = set()
    for job in jobs:
        if not job.active:
            continue
        job_errors = validate_job(job)
        if job.id in seen_ids:
            job_errors.append("duplicate id")
        seen_ids.add(job.id)
        for error in job_errors:
            problems.append(f"{job.id}: {error}")
    if problems:
        raise JobValidationError("Invalid production jobs:\n" + "\n".join(problems[:50]))
