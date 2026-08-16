"""Palantir collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class PalantirScraper(ConfiguredCompanyScraper):
    source_id = "palantir"
    name = "palantir"
    company = "Palantir"
