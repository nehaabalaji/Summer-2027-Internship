"""Airbnb collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class AirbnbScraper(ConfiguredCompanyScraper):
    source_id = "airbnb"
    name = "airbnb"
    company = "Airbnb"
