"""Microsoft adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class MicrosoftScraper(BaseScraper):
    name = "microsoft"
    company = "Microsoft"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Microsoft careers moved to Eightfold (apply.careers.microsoft.com), which has no public unauthenticated job API. Existing listings, if any, are preserved."
        )
