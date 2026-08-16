"""Costco adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class CostcoScraper(BaseScraper):
    name = "costco"
    company = "Costco"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Costco careers do not expose a verified public unauthenticated job API. Existing listings, if any, are preserved."
        )
