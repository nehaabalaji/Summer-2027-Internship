"""Instacart collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class InstacartScraper(ConfiguredCompanyScraper):
    source_id = "instacart"
    name = "instacart"
    company = "Instacart"
