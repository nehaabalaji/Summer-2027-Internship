"""Load YAML configuration from the repository."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return ROOT


def _read_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@lru_cache(maxsize=1)
def settings() -> dict[str, Any]:
    data = _read_yaml(ROOT / "config" / "settings.yaml")
    max_jobs = os.environ.get("MAX_README_JOBS_PER_CATEGORY")
    if max_jobs:
        data.setdefault("readme", {})["max_jobs_per_category"] = int(max_jobs)
    cache_dir = os.environ.get("CACHE_DIR")
    if cache_dir:
        data.setdefault("paths", {})["cache_dir"] = cache_dir
    github_repo = os.environ.get("GITHUB_REPOSITORY")
    if github_repo and "/" in github_repo:
        user, repo = github_repo.split("/", 1)
        data.setdefault("project", {})["github_user"] = user
        data["project"]["github_repo"] = repo
    return data


def sources() -> list[dict[str, Any]]:
    items = list(_read_yaml(ROOT / "config" / "sources.yaml") or [])
    boards_path = ROOT / "config" / "ats_boards.yaml"
    if boards_path.exists():
        extra = _read_yaml(boards_path)
        extra_items = extra.get("boards") if isinstance(extra, dict) else extra
        items.extend(extra_items or [])
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for item in items:
        key = item.get("id") or item.get("source")
        if not key:
            continue
        if key not in by_id:
            order.append(key)
        by_id[key] = item
    return [by_id[key] for key in order]


@lru_cache(maxsize=1)
def excluded_companies() -> set[str]:
    path = ROOT / "config" / "excluded_companies.yaml"
    names = _read_yaml(path) or []
    return {str(name).strip().lower() for name in names if name}


def companies() -> dict[str, Any]:
    return dict(_read_yaml(ROOT / "config" / "companies.yaml"))


def classification_rules() -> dict[str, Any]:
    return dict(_read_yaml(ROOT / "config" / "classification_rules.yaml"))


def path_from_settings(key: str) -> Path:
    relative = settings()["paths"][key]
    return ROOT / relative


def user_agent() -> str:
    return settings()["project"]["user_agent"]
