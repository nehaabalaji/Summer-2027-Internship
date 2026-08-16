"""KPMG collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class KPMGScraper(ConfiguredCompanyScraper):
    source_id = "kpmg"
    name = "kpmg"
    company = "KPMG"
