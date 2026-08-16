"""General Motors collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class GMScraper(ConfiguredCompanyScraper):
    source_id = "gm"
    name = "gm"
    company = "General Motors"
