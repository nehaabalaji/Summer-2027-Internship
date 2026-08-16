"""Databricks collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class DatabricksScraper(ConfiguredCompanyScraper):
    source_id = "databricks"
    name = "databricks"
    company = "Databricks"
