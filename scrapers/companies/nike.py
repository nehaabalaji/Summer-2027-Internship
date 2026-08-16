"""Nike collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class NikeScraper(ConfiguredCompanyScraper):
    source_id = "nike"
    name = "nike"
    company = "Nike"
