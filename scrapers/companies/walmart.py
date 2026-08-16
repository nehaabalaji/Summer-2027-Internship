"""Walmart collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class WalmartScraper(ConfiguredCompanyScraper):
    source_id = "walmart"
    name = "walmart"
    company = "Walmart"
