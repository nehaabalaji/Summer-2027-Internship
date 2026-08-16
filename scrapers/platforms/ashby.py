"""Ashby public job board API adapter."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from board.http import request_json
from board.models import RawJob
from scrapers.utils import make_raw_job, strip_html


def _arrangement(item: dict[str, Any]) -> Optional[str]:
    workplace = (item.get("workplaceType") or "").lower()
    if item.get("isRemote") is True or workplace == "remote":
        return "Remote"
    if workplace == "hybrid":
        return "Hybrid"
    if workplace in {"onsite", "on-site"}:
        return "On-site"
    return None


def _job_type(item: dict[str, Any]) -> Optional[str]:
    employment = (item.get("employmentType") or "").lower()
    if "intern" in employment:
        return "Internship"
    return item.get("employmentType")


def parse_ashby_jobs(
    payload: dict[str, Any],
    *,
    company: str,
    source_key: str,
) -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload.get("jobs") or []:
        title = (item.get("title") or "").strip()
        url = item.get("jobUrl") or item.get("applyUrl") or ""
        if not title or not url:
            continue
        location = item.get("location") or ""
        jobs.append(
            make_raw_job(
                company=company,
                title=title,
                application_url=url,
                source=f"{company} Careers (Ashby)",
                source_key=source_key,
                location=location,
                description=strip_html(item.get("descriptionHtml") or item.get("department") or ""),
                job_type=_job_type(item),
                work_arrangement=_arrangement(item),
                date_posted=item.get("publishedAt"),
                source_url=url,
                source_job_id=item.get("id"),
                extra={"department": item.get("department") or "", "team": item.get("team") or ""},
            )
        )
    return jobs


def fetch_ashby_board(slug: str) -> dict[str, Any]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    return request_json(url)


def collect_ashby(slug: str, company: str, source_key: str) -> Iterable[RawJob]:
    payload = fetch_ashby_board(slug)
    return parse_ashby_jobs(payload, company=company, source_key=source_key)
