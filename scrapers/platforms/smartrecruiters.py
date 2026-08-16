"""SmartRecruiters public postings API adapter."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from board.http import request_json
from board.models import RawJob
from scrapers.utils import make_raw_job


def _arrangement(location: dict[str, Any]) -> Optional[str]:
    if location.get("remote") is True:
        return "Remote"
    if location.get("hybrid") is True:
        return "Hybrid"
    return None


def parse_smartrecruiters_jobs(
    payload: dict[str, Any],
    *,
    company: str,
    source_key: str,
    identifier: str,
) -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload.get("content") or []:
        title = item.get("name") or ""
        job_id = item.get("id")
        if not title or not job_id:
            continue
        loc = item.get("location") or {}
        location = loc.get("fullLocation") or ", ".join(
            part for part in [loc.get("city"), loc.get("region"), loc.get("country")] if part
        )
        url = f"https://jobs.smartrecruiters.com/{identifier}/{job_id}"
        employment = ((item.get("typeOfEmployment") or {}).get("label") or "")
        jobs.append(
            make_raw_job(
                company=(item.get("company") or {}).get("name") or company,
                title=title,
                application_url=url,
                source=f"{company} Careers (SmartRecruiters)",
                source_key=source_key,
                location=location,
                description=(item.get("department") or {}).get("label") or "",
                job_type=employment or None,
                work_arrangement=_arrangement(loc),
                date_posted=item.get("releasedDate"),
                source_url=url,
                source_job_id=job_id,
                extra={"employment": employment},
            )
        )
    return jobs


def fetch_smartrecruiters_page(identifier: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    url = f"https://api.smartrecruiters.com/v1/companies/{identifier}/postings"
    return request_json(url, params={"offset": offset, "limit": limit})


def collect_smartrecruiters(identifier: str, company: str, source_key: str) -> Iterable[RawJob]:
    offset = 0
    collected: list[RawJob] = []
    while True:
        payload = fetch_smartrecruiters_page(identifier, offset=offset)
        chunk = parse_smartrecruiters_jobs(
            payload, company=company, source_key=source_key, identifier=identifier
        )
        collected.extend(chunk)
        total = int(payload.get("totalFound") or 0)
        offset += len(payload.get("content") or [])
        if not chunk or offset >= total:
            break
    return collected
