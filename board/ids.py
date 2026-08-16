"""Stable job identifiers."""

from __future__ import annotations

import hashlib
import re

from board.urls import canonicalize_url

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str, *, max_length: int = 48) -> str:
    slug = _SLUG_RE.sub("-", (value or "").lower()).strip("-")
    return slug[:max_length] or "job"


def short_hash(value: str, length: int = 10) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def make_job_id(
    company: str,
    *,
    source_job_id: str | None,
    title: str,
    location: str,
    application_url: str,
) -> str:
    company_slug = slugify(company, max_length=32)
    if source_job_id:
        return f"{company_slug}-{slugify(str(source_job_id), max_length=40)}"
    url_hash = short_hash(canonicalize_url(application_url))
    return (
        f"{company_slug}-{slugify(title, max_length=40)}-"
        f"{slugify(location, max_length=24)}-{url_hash}"
    )
