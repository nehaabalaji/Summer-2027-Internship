"""Dell collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class DellScraper(ConfiguredCompanyScraper):
    source_id = "dell"
    name = "dell"
    company = "Dell"
