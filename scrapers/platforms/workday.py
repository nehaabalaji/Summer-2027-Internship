"""Workday public CXS job list adapter.

Uses the unauthenticated JSON endpoint that powers public Workday career sites.
Requires tenant, shard, and site from an official careers URL — these cannot be guessed.
"""

from __future__ import annotations

from typing import Any, Iterable
from urllib.parse import quote

from board.http import request_json
from board.models import RawJob
from scrapers.base import ScraperError
from scrapers.utils import make_raw_job


def workday_jobs_url(tenant: str, shard: str, site: str) -> str:
    return f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"


def workday_apply_url(tenant: str, shard: str, site: str, external_path: str) -> str:
    path = external_path if external_path.startswith("/") else f"/{external_path}"
    return f"https://{tenant}.{shard}.myworkdayjobs.com/{site}{path}"


def parse_workday_jobs(
    payload: dict[str, Any],
    *,
    company: str,
    source_key: str,
    tenant: str,
    shard: str,
    site: str,
) -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload.get("jobPostings") or []:
        title = item.get("title") or ""
        external_path = item.get("externalPath") or ""
        if not title or not external_path:
            continue
        url = workday_apply_url(tenant, shard, site, external_path)
        location = item.get("locationsText") or ""
        if location.lower().endswith("locations") and location[0].isdigit():
            location = ""
        bullets = item.get("bulletFields") or []
        source_job_id = bullets[0] if bullets else None
        jobs.append(
            make_raw_job(
                company=company,
                title=title,
                application_url=url,
                source=f"{company} Careers (Workday)",
                source_key=source_key,
                location=location,
                date_posted=item.get("postedOn"),
                source_url=url,
                source_job_id=source_job_id or quote(external_path, safe=""),
            )
        )
    return jobs


def fetch_workday_page(
    tenant: str,
    shard: str,
    site: str,
    *,
    offset: int = 0,
    limit: int = 20,
    search_text: str = "intern",
) -> dict[str, Any]:
    url = workday_jobs_url(tenant, shard, site)
    return request_json(
        url,
        method="POST",
        json_body={"limit": limit, "offset": offset, "searchText": search_text},
        headers={"Content-Type": "application/json"},
        use_cache=offset == 0,
    )


def collect_workday(
    *,
    tenant: str,
    shard: str,
    site: str,
    company: str,
    source_key: str,
    max_jobs: int = 200,
) -> Iterable[RawJob]:
    if not tenant or not shard or not site:
        raise ScraperError(
            f"{company} Workday scraper is missing tenant/shard/site. "
            "Copy them from the official myworkdayjobs.com careers URL."
        )
    first = fetch_workday_page(tenant, shard, site, offset=0, limit=20)
    collected = parse_workday_jobs(
        first, company=company, source_key=source_key, tenant=tenant, shard=shard, site=site
    )
    total = int(first.get("total") or len(collected))
    offset = 20
    while len(collected) < min(total, max_jobs) and offset < total:
        page = fetch_workday_page(tenant, shard, site, offset=offset, limit=20)
        chunk = parse_workday_jobs(
            page, company=company, source_key=source_key, tenant=tenant, shard=shard, site=site
        )
        if not chunk:
            break
        collected.extend(chunk)
        offset += 20
    return collected[:max_jobs]
