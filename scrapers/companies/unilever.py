"""Unilever collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class UnileverScraper(ConfiguredCompanyScraper):
    source_id = "unilever"
    name = "unilever"
    company = "Unilever"
