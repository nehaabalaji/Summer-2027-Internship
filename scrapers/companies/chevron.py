"""Chevron collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class ChevronScraper(ConfiguredCompanyScraper):
    source_id = "chevron"
    name = "chevron"
    company = "Chevron"
