"""EY collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class EYScraper(ConfiguredCompanyScraper):
    source_id = "ey"
    name = "ey"
    company = "EY"
