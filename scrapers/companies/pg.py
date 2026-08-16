"""Procter & Gamble collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class PGScraper(ConfiguredCompanyScraper):
    source_id = "pg"
    name = "pg"
    company = "Procter & Gamble"
