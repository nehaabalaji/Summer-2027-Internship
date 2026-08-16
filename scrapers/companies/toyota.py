"""Toyota collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class ToyotaScraper(ConfiguredCompanyScraper):
    source_id = "toyota"
    name = "toyota"
    company = "Toyota"
