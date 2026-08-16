"""Lever public postings API adapter."""

from __future__ import annotations

from typing import Any, Iterable

from board.http import request_json
from board.models import RawJob
from scrapers.utils import make_raw_job


def _arrangement(item: dict[str, Any]) -> str | None:
    workplace = (item.get("workplaceType") or "").lower()
    if workplace == "remote":
        return "Remote"
    if workplace == "hybrid":
        return "Hybrid"
    if workplace in {"onsite", "on-site"}:
        return "On-site"
    return None


def _job_type(item: dict[str, Any]) -> str | None:
    commitment = ((item.get("categories") or {}).get("commitment") or "").lower()
    if "intern" in commitment:
        return "Internship"
    if "co-op" in commitment or "coop" in commitment:
        return "Co-op"
    return commitment or None


def parse_lever_jobs(
    payload: list[dict[str, Any]],
    *,
    company: str,
    source_key: str,
) -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload:
        title = item.get("text") or item.get("title") or ""
        url = item.get("hostedUrl") or item.get("applyUrl") or ""
        if not title or not url:
            continue
        categories = item.get("categories") or {}
        location = categories.get("location") or ""
        all_locations = categories.get("allLocations") or []
        if not location and all_locations:
            location = all_locations[0]
        description = " ".join(
            [
                item.get("descriptionPlain") or "",
                categories.get("department") or "",
                categories.get("team") or "",
            ]
        )
        jobs.append(
            make_raw_job(
                company=company,
                title=title,
                application_url=url,
                source=f"{company} Careers (Lever)",
                source_key=source_key,
                location=location,
                description=description,
                job_type=_job_type(item),
                work_arrangement=_arrangement(item),
                date_posted=item.get("createdAt"),
                source_url=url,
                source_job_id=item.get("id"),
                extra={"commitment": (item.get("categories") or {}).get("commitment") or ""},
            )
        )
    return jobs


def fetch_lever_board(site: str) -> list[dict[str, Any]]:
    url = f"https://api.lever.co/v0/postings/{site}"
    data = request_json(url, params={"mode": "json"})
    if not isinstance(data, list):
        raise ValueError(f"Unexpected Lever payload for {site}")
    return data


def collect_lever(site: str, company: str, source_key: str) -> Iterable[RawJob]:
    payload = fetch_lever_board(site)
    return parse_lever_jobs(payload, company=company, source_key=source_key)
