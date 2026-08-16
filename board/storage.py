"""JSON storage with a replaceable interface."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from board.config import path_from_settings
from board.models import Job


class JobRepository(Protocol):
    def load(self) -> list[Job]: ...
    def save(self, jobs: Iterable[Job]) -> None: ...


class JsonJobRepository:
    """Canonical GitHub-friendly store. Swap for SQLite later without changing callers."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or path_from_settings("jobs")

    def load(self) -> list[Job]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"{self.path} must contain a JSON array of jobs")
        return [Job.model_validate(item) for item in raw]

    def save(self, jobs: Iterable[Job]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [job.model_dump() for job in jobs]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
