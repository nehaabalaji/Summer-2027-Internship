"""Greenhouse public Job Board API adapter."""

from __future__ import annotations

from typing import Any, Iterable

from board.http import request_json
from board.models import RawJob
from scrapers.utils import make_raw_job, strip_html


def parse_greenhouse_jobs(
    payload: dict[str, Any],
    *,
    company: str,
    source_key: str,
    source_label: str,
) -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload.get("jobs") or []:
        location = ""
        loc = item.get("location")
        if isinstance(loc, dict):
            location = loc.get("name") or ""
        elif isinstance(loc, str):
            location = loc
        offices = item.get("offices") or []
        if not location and offices:
            location = offices[0].get("name") or ""
        departments = item.get("departments") or []
        dept = departments[0].get("name") if departments else ""
        title = item.get("title") or ""
        url = item.get("absolute_url") or ""
        if not title or not url:
            continue
        jobs.append(
            make_raw_job(
                company=item.get("company_name") or company,
                title=title,
                application_url=url,
                source=source_label,
                source_key=source_key,
                location=location,
                description=strip_html(item.get("content") or dept or ""),
                date_posted=item.get("first_published") or item.get("updated_at"),
                source_url=url,
                source_job_id=item.get("id"),
                extra={"department": dept},
            )
        )
    return jobs


def fetch_greenhouse_board(board_token: str) -> dict[str, Any]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    return request_json(url, params={"content": "false"})


def collect_greenhouse(board_token: str, company: str, source_key: str) -> Iterable[RawJob]:
    payload = fetch_greenhouse_board(board_token)
    return parse_greenhouse_jobs(
        payload,
        company=company,
        source_key=source_key,
        source_label=f"{company} Careers (Greenhouse)",
    )
