"""Google adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class GoogleScraper(BaseScraper):
    name = "google"
    company = "Google"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Google careers JSON endpoints previously used by aggregators currently return 404. Existing listings, if any, are preserved."
        )
