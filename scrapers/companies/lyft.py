"""Lyft collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class LyftScraper(ConfiguredCompanyScraper):
    source_id = "lyft"
    name = "lyft"
    company = "Lyft"
