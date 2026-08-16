"""Siemens adapter — public collection is not available."""

from __future__ import annotations

from typing import Iterable

from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError


class SiemensScraper(BaseScraper):
    name = "siemens"
    company = "Siemens"

    def fetch_jobs(self) -> Iterable[RawJob]:
        raise UnsupportedSourceError(
            "Siemens careers are custom-hosted; no verified public unauthenticated job API. Existing listings, if any, are preserved."
        )
