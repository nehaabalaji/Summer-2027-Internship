"""Coca-Cola collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class CocaColaScraper(ConfiguredCompanyScraper):
    source_id = "cocacola"
    name = "cocacola"
    company = "Coca-Cola"
