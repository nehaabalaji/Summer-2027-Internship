"""Workday public CXS job list adapter.

Uses the unauthenticated JSON endpoint that powers public Workday career sites.
Requires tenant, shard, and site from an official careers URL — these cannot be guessed.
"""

from __future__ import annotations

from typing import Any, Iterable
from urllib.parse import quote

from board.classification import looks_like_early_career
from board.config import settings
from board.http import request_json
from board.models import RawJob
from scrapers.base import ScraperError
from scrapers.utils import make_raw_job


def workday_jobs_url(tenant: str, shard: str, site: str) -> str:
    return f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"


def workday_apply_url(tenant: str, shard: str, site: str, external_path: str) -> str:
    path = external_path if external_path.startswith("/") else f"/{external_path}"
    return f"https://{tenant}.{shard}.myworkdayjobs.com/{site}{path}"


def _location_from_workday(item: dict[str, Any]) -> str:
    location = item.get("locationsText") or ""
    if location and location[0].isdigit() and location.lower().endswith("locations"):
        location = ""
    if location:
        return location
    path = item.get("externalPath") or ""
    if "/job/" in path:
        slug = path.split("/job/", 1)[1].split("/", 1)[0]
        slug = slug.replace("---", ", ").replace("--", ", ").replace("-", " ")
        return slug.replace("  ", " ").strip()
    return ""


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
        location = _location_from_workday(item)
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
    max_jobs: int | None = None,
) -> Iterable[RawJob]:
    if not tenant or not shard or not site:
        raise ScraperError(
            f"{company} Workday scraper is missing tenant/shard/site. "
            "Copy them from the official myworkdayjobs.com careers URL."
        )
    cap = max_jobs if max_jobs is not None else 150
    queries = ["intern", "co-op"]
    seen: set[str] = set()
    collected: list[RawJob] = []
    for query in queries:
        offset = 0
        first = fetch_workday_page(tenant, shard, site, offset=0, limit=20, search_text=query)
        page_jobs = parse_workday_jobs(
            first, company=company, source_key=source_key, tenant=tenant, shard=shard, site=site
        )
        total = int(first.get("total") or len(page_jobs))
        max_offset = min(total, 400)
        while True:
            for job in page_jobs:
                if job.application_url in seen:
                    continue
                if not looks_like_early_career(job.title, job.job_type):
                    continue
                seen.add(job.application_url)
                collected.append(job)
                if len(collected) >= cap:
                    return collected
            offset += 20
            if offset >= max_offset:
                break
            page = fetch_workday_page(tenant, shard, site, offset=offset, limit=20, search_text=query)
            page_jobs = parse_workday_jobs(
                page, company=company, source_key=source_key, tenant=tenant, shard=shard, site=site
            )
            if not page_jobs:
                break
    return collected
