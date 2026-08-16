"""Shared scraper helpers."""

from __future__ import annotations

import html
import re
from typing import Any, Optional

from board.models import RawJob
from board.urls import application_url_for_storage

_HTML_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(value: str) -> str:
    if not value:
        return ""
    text = html.unescape(html.unescape(value))
    text = _HTML_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def make_raw_job(
    *,
    company: str,
    title: str,
    application_url: str,
    source: str,
    source_key: str,
    location: str = "",
    description: str = "",
    job_type: Optional[str] = None,
    work_arrangement: Optional[str] = None,
    date_posted: Any = None,
    source_url: str = "",
    source_job_id: Any = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    salary_currency: Optional[str] = None,
    sponsorship: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> RawJob:
    url = application_url_for_storage(application_url)
    return RawJob(
        company=company,
        title=title.strip(),
        application_url=url,
        source=source,
        source_key=source_key,
        location=location or "",
        description=strip_html(description)[:800],
        job_type=job_type,
        work_arrangement=work_arrangement,
        date_posted=str(date_posted) if date_posted not in (None, "") else None,
        source_url=source_url or url,
        source_job_id=str(source_job_id) if source_job_id not in (None, "") else None,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        sponsorship=sponsorship,
        extra=extra or {},
    )
