"""Wayfair collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class WayfairScraper(ConfiguredCompanyScraper):
    source_id = "wayfair"
    name = "wayfair"
    company = "Wayfair"
