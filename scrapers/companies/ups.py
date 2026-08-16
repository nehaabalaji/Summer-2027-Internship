"""UPS collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class UPSScraper(ConfiguredCompanyScraper):
    source_id = "ups"
    name = "ups"
    company = "UPS"
