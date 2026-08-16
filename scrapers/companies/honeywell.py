"""Honeywell collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class HoneywellScraper(ConfiguredCompanyScraper):
    source_id = "honeywell"
    name = "honeywell"
    company = "Honeywell"
