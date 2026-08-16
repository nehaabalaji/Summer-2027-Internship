"""Build enabled scrapers from config/sources.yaml."""

from __future__ import annotations

from typing import Any

from board.config import sources as load_sources
from scrapers.base import BaseScraper, UnsupportedSourceError
from scrapers.companies.amazon import AmazonScraper
from scrapers.generic import GenericPlatformScraper

CUSTOM_SCRAPERS: dict[str, type[BaseScraper]] = {
    "amazon": AmazonScraper,
}


def build_scraper(source_config: dict[str, Any]) -> BaseScraper:
    source_id = source_config["source"]
    platform = (source_config.get("platform") or "").lower()
    if platform == "amazon" or source_id == "amazon":
        return AmazonScraper()
    custom = CUSTOM_SCRAPERS.get(source_id)
    if custom:
        return custom()
    return GenericPlatformScraper(source_config)


def get_enabled_scrapers(source: str | None = None) -> list[BaseScraper]:
    scrapers: list[BaseScraper] = []
    for item in load_sources():
        if source:
            if item.get("source") != source and item.get("id") != source:
                continue
        elif not item.get("enabled"):
            continue
        if source and not item.get("enabled") and item.get("platform") == "unsupported":
            raise UnsupportedSourceError(
                item.get("notes") or f"{item.get('company')} is not publicly collectable."
            )
        scrapers.append(build_scraper(item))
    if source and not scrapers:
        raise KeyError(f"Unknown source: {source}")
    return scrapers
