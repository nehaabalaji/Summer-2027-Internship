"""Boeing collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class BoeingScraper(ConfiguredCompanyScraper):
    source_id = "boeing"
    name = "boeing"
    company = "Boeing"
