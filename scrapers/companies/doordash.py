"""DoorDash collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class DoorDashScraper(ConfiguredCompanyScraper):
    source_id = "doordash"
    name = "doordash"
    company = "DoorDash"
