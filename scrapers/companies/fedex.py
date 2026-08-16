"""FedEx adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class FedExScraper(BaseScraper):
    name = "fedex"
    company = "FedEx"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "FedEx careers are custom-hosted; no verified public unauthenticated job API. Existing listings, if any, are preserved."
        )
