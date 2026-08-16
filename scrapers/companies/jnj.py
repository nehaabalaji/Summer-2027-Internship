"""Johnson & Johnson collector configured via config/sources.yaml."""

from scrapers.generic import ConfiguredCompanyScraper


class JNJScraper(ConfiguredCompanyScraper):
    source_id = "jnj"
    name = "jnj"
    company = "Johnson & Johnson"
