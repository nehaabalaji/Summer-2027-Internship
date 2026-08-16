"""Scraper contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from board.models import RawJob


class ScraperError(RuntimeError):
    pass


class UnsupportedSourceError(ScraperError):
    pass


class BaseScraper(ABC):
    """Every collector returns normalized raw job dictionaries via RawJob models."""

    name: str
    company: str = ""
    source_label: str = ""

    @abstractmethod
    def fetch_jobs(self) -> Iterable[RawJob]:
        raise NotImplementedError
