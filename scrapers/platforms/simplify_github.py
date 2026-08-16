"""SimplifyJobs GitHub internship lists (public listings.json).

Uses the community-maintained JSON on GitHub, not Simplify's product API
and not any proprietary scraper. Application URLs are whatever the list
published — prefer employer ATS links when present.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from board.models import RawJob
from board.http import request_json
from scrapers.utils import make_raw_job

SUMMER_LISTINGS = (
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/"
    "dev/.github/scripts/listings.json"
)
NEWGRAD_LISTINGS = (
    "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/"
    "dev/.github/scripts/listings.json"
)


def _locations(item: dict[str, Any]) -> list[str]:
    raw = item.get("locations") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    return [str(part) for part in raw if part]


def _pick_location(locations: list[str]) -> str:
    if not locations:
        return ""
    from board.normalization import is_us_job, parse_location

    for loc in locations:
        parsed = parse_location(loc)
        if is_us_job(parsed, raw=loc):
            return loc
    return locations[0]


def _posted(item: dict[str, Any]) -> str | None:
    value = item.get("date_posted")
    if value in (None, ""):
        return None
    try:
        ts = int(value)
        if ts > 10_000_000_000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError, OverflowError):
        return str(value)


def parse_simplify_listings(
    payload: Any,
    *,
    source_key: str,
    source_label: str,
) -> list[RawJob]:
    items = payload if isinstance(payload, list) else (payload or {}).get("listings") or []
    jobs: list[RawJob] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("active") is False or item.get("is_visible") is False:
            continue
        title = (item.get("title") or "").strip()
        company = (item.get("company_name") or "").strip()
        url = (item.get("url") or "").strip()
        if not title or not company or not url:
            continue
        location = _pick_location(_locations(item))
        category = (item.get("category") or "").strip()
        if category.lower() in {"software", "hardware", "quant", "quantitative finance"}:
            continue
        jobs.append(
            make_raw_job(
                company=company,
                title=title,
                application_url=url,
                source=source_label,
                source_key=source_key,
                location=location,
                description=str(category),
                job_type="Internship" if "new-grad" not in source_key else "New Graduate",
                date_posted=_posted(item),
                source_url=url,
                source_job_id=item.get("id"),
                extra={"simplify_category": category, "commitment": "Internship"},
            )
        )
    return jobs


def collect_simplify_github(url: str, source_key: str, source_label: str) -> Iterable[RawJob]:
    payload = request_json(url, use_cache=True)
    return parse_simplify_listings(payload, source_key=source_key, source_label=source_label)
