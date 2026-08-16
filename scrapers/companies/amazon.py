"""Amazon public job search JSON feed (amazon.jobs/en/search.json)."""

from __future__ import annotations

from typing import Any, Iterable

from board.classification import looks_like_early_career
from board.config import settings
from board.http import request_json
from board.models import RawJob
from scrapers.base import BaseScraper
from scrapers.utils import make_raw_job, strip_html

SEARCH_URL = "https://www.amazon.jobs/en/search.json"
JOB_BASE = "https://www.amazon.jobs"


def parse_amazon_jobs(payload: dict[str, Any], *, source_key: str = "amazon") -> list[RawJob]:
    jobs: list[RawJob] = []
    for item in payload.get("jobs") or []:
        title = item.get("title") or ""
        path = item.get("job_path") or ""
        if not title or not path:
            continue
        url = JOB_BASE + path
        location = item.get("normalized_location") or item.get("location") or ""
        if item.get("city") == "Virtual" or (location or "").lower() == "virtual":
            location = "Remote"
        description = " ".join(
            [
                strip_html(item.get("description_short") or ""),
                item.get("job_category") or "",
                item.get("business_category") or "",
                item.get("job_family") or "",
            ]
        )
        arrangement = "Remote" if location.lower().startswith("remote") or location.lower() == "virtual" else None
        source_type = None
        if item.get("is_intern") is True or looks_like_early_career(title):
            source_type = "Internship"
        elif item.get("university_job"):
            source_type = "Internship"
        jobs.append(
            make_raw_job(
                company="Amazon",
                title=title,
                application_url=url,
                source="Amazon Careers",
                source_key=source_key,
                location=location,
                description=description,
                job_type=source_type,
                work_arrangement=arrangement,
                date_posted=item.get("posted_date"),
                source_url=url,
                source_job_id=item.get("id_icims") or item.get("id"),
                extra={
                    "business_category": item.get("business_category") or "",
                    "job_category": item.get("job_category") or "",
                    "is_intern": item.get("is_intern"),
                },
            )
        )
    return jobs


def fetch_amazon_search(offset: int, query: str, limit: int = 50, extra: dict | None = None) -> dict[str, Any]:
    params = {
        "base_query": query,
        "offset": offset,
        "result_limit": limit,
        "sort": "recent",
    }
    if extra:
        params.update(extra)
    return request_json(SEARCH_URL, params=params, use_cache=offset == 0)


class AmazonScraper(BaseScraper):
    name = "amazon"
    company = "Amazon"
    source_label = "Amazon Careers"

    def fetch_jobs(self) -> Iterable[RawJob]:
        cap = int(settings()["pipeline"]["max_jobs_per_source"])
        collected: list[RawJob] = []
        seen: set[str] = set()
        searches: list[tuple[str, dict]] = [
            ("intern", {"loc_query": "United States"}),
            ("co-op", {"loc_query": "United States"}),
            ("new graduate", {"loc_query": "United States"}),
            ("area manager intern", {}),
            ("supply chain intern", {}),
            ("operations intern", {}),
            ("product manager intern", {}),
            ("logistics intern", {}),
            ("procurement intern", {}),
            ("pathways intern", {}),
        ]
        for query, extra in searches:
            offset = 0
            while len(collected) < cap:
                payload = fetch_amazon_search(offset, query, extra=extra)
                chunk = parse_amazon_jobs(payload, source_key=self.name)
                if not chunk:
                    break
                for job in chunk:
                    if job.application_url in seen:
                        continue
                    seen.add(job.application_url)
                    collected.append(job)
                hits = int(payload.get("hits") or 0)
                offset += len(payload.get("jobs") or [])
                if offset >= hits or not payload.get("jobs"):
                    break
            if len(collected) >= cap:
                break
        return collected
