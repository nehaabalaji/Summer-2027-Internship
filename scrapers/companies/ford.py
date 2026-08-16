"""Ford collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class FordScraper(ConfiguredCompanyScraper):
    source_id = "ford"
    name = "ford"
    company = "Ford"
