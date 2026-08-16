"""Home Depot collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class HomeDepotScraper(ConfiguredCompanyScraper):
    source_id = "homedepot"
    name = "homedepot"
    company = "Home Depot"
