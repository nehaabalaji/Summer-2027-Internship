"""PwC collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class PwCScraper(ConfiguredCompanyScraper):
    source_id = "pwc"
    name = "pwc"
    company = "PwC"
