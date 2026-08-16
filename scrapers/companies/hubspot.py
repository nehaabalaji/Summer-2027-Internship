"""HubSpot collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class HubSpotScraper(ConfiguredCompanyScraper):
    source_id = "hubspot"
    name = "hubspot"
    company = "HubSpot"
