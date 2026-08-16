"""Tesla collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class TeslaScraper(ConfiguredCompanyScraper):
    source_id = "tesla"
    name = "tesla"
    company = "Tesla"
