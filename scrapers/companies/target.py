"""Target collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class TargetScraper(ConfiguredCompanyScraper):
    source_id = "target"
    name = "target"
    company = "Target"
