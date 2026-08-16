"""Stripe collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class StripeScraper(ConfiguredCompanyScraper):
    source_id = "stripe"
    name = "stripe"
    company = "Stripe"
