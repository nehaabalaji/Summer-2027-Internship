"""Manual corrections that survive future scraper runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from board.config import path_from_settings
from board.models import Job
from board.storage import load_json


def load_overrides(path: Path | None = None) -> dict[str, Any]:
    payload = load_json(path or path_from_settings("overrides"), {"jobs": {}})
    if not isinstance(payload, dict):
        return {}
    jobs = payload.get("jobs") or {}
    return jobs if isinstance(jobs, dict) else {}


def apply_overrides(jobs: list[Job], overrides: dict[str, Any] | None = None) -> list[Job]:
    mapping = overrides if overrides is not None else load_overrides()
    allowed = {
        "category",
        "title",
        "location",
        "sponsorship",
        "active",
        "job_type",
        "work_arrangement",
        "application_url",
        "city",
        "state",
        "country",
    }
    for job in jobs:
        patch = mapping.get(job.id)
        if not patch:
            continue
        for key, value in patch.items():
            if key in allowed:
                setattr(job, key, value)
    return jobs
