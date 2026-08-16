"""ExxonMobil collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class ExxonMobilScraper(ConfiguredCompanyScraper):
    source_id = "exxonmobil"
    name = "exxonmobil"
    company = "ExxonMobil"
