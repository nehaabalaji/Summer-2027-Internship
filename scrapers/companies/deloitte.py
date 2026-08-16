"""Deloitte adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class DeloitteScraper(BaseScraper):
    name = "deloitte"
    company = "Deloitte"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Deloitte careers are custom-hosted; no verified public unauthenticated job API. Existing listings, if any, are preserved."
        )
