"""Apple adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class AppleScraper(BaseScraper):
    name = "apple"
    company = "Apple"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Apple jobs.apple.com does not expose a stable public unauthenticated search API. Existing listings, if any, are preserved."
        )
