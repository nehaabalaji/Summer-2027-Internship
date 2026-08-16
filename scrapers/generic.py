"""Generic ATS adapters driven by config/sources.yaml."""

from __future__ import annotations

from typing import Any, Iterable

from board.config import sources as load_sources
from board.models import RawJob
from scrapers.base import BaseScraper, UnsupportedSourceError
from scrapers.platforms.ashby import collect_ashby
from scrapers.platforms.greenhouse import collect_greenhouse
from scrapers.platforms.lever import collect_lever
from scrapers.platforms.smartrecruiters import collect_smartrecruiters
from scrapers.platforms.workday import collect_workday


def source_config_by_id(source_id: str) -> dict[str, Any]:
    for item in load_sources():
        if item.get("source") == source_id or item.get("id") == source_id:
            return item
    raise KeyError(f"No source config for {source_id}")


class GenericPlatformScraper(BaseScraper):
    """Collect jobs from a configured Greenhouse, Lever, Ashby, Workday, or SmartRecruiters board."""

    def __init__(self, source_config: dict[str, Any]) -> None:
        self.config = source_config
        self.name = source_config["source"]
        self.company = source_config.get("company") or self.name
        self.platform = (source_config.get("platform") or "").lower()
        self.source_label = f"{self.company} Careers"

    def fetch_jobs(self) -> Iterable[RawJob]:
        platform = self.platform
        token = self.config.get("board_token") or self.config.get("site") or self.config.get("identifier")
        if platform == "greenhouse":
            return collect_greenhouse(token, self.company, self.name)
        if platform == "lever":
            return collect_lever(token, self.company, self.name)
        if platform == "ashby":
            return collect_ashby(token, self.company, self.name)
        if platform == "smartrecruiters":
            return collect_smartrecruiters(token, self.company, self.name)
        if platform == "workday":
            return collect_workday(
                tenant=self.config.get("tenant") or "",
                shard=self.config.get("shard") or "",
                site=self.config.get("site") or "",
                company=self.company,
                source_key=self.name,
            )
        if platform in {"unsupported", ""}:
            raise UnsupportedSourceError(
                self.config.get("notes")
                or f"{self.company} does not have a verified public job API. "
                "See docs/scraper-development.md."
            )
        raise UnsupportedSourceError(f"Unknown platform '{platform}' for {self.company}")


class ConfiguredCompanyScraper(GenericPlatformScraper):
    """Company wrapper that loads its own row from config/sources.yaml."""

    source_id: str

    def __init__(self) -> None:
        super().__init__(source_config_by_id(self.source_id))
