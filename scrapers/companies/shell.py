"""Shell collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class ShellScraper(ConfiguredCompanyScraper):
    source_id = "shell"
    name = "shell"
    company = "Shell"
