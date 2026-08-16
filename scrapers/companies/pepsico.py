"""PepsiCo collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class PepsiCoScraper(ConfiguredCompanyScraper):
    source_id = "pepsico"
    name = "pepsico"
    company = "PepsiCo"
