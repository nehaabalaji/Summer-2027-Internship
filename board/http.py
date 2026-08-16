"""Polite HTTP client with retries, rate limiting, and optional disk cache."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from board.config import path_from_settings, settings, user_agent

_last_request_at: dict[str, float] = {}


class HttpError(RuntimeError):
    def __init__(self, message: str, *, status_code: Optional[int] = None, temporary: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.temporary = temporary


def _cache_path(method: str, url: str, body: str) -> Path:
    digest = hashlib.sha256(f"{method}:{url}:{body}".encode()).hexdigest()
    cache_dir = path_from_settings("cache_dir")
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{digest}.json"


def _read_cache(path: Path, ttl: int) -> Optional[Any]:
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("body")


def _write_cache(path: Path, body: Any) -> None:
    path.write_text(json.dumps({"body": body}), encoding="utf-8")


def _respect_rate_limit(url: str, min_interval: float) -> None:
    host = urlparse(url).netloc
    last = _last_request_at.get(host)
    now = time.monotonic()
    if last is not None:
        wait = min_interval - (now - last)
        if wait > 0:
            time.sleep(wait)
    _last_request_at[host] = time.monotonic()


def request_json(
    url: str,
    *,
    method: str = "GET",
    json_body: Any = None,
    params: Optional[dict[str, Any]] = None,
    use_cache: bool = True,
    headers: Optional[dict[str, str]] = None,
) -> Any:
    """Fetch JSON with retries. Temporary failures raise HttpError(temporary=True)."""
    cfg = settings()["http"]
    timeout = cfg["timeout_seconds"]
    retries = cfg["max_retries"]
    backoff = cfg["backoff_seconds"]
    min_interval = cfg["min_interval_seconds"]
    ttl = cfg["cache_ttl_seconds"]
    body_key = json.dumps(json_body, sort_keys=True) if json_body is not None else ""
    cache_file = _cache_path(method, url, body_key + json.dumps(params or {}, sort_keys=True))
    if use_cache:
        cached = _read_cache(cache_file, ttl)
        if cached is not None:
            return cached

    request_headers = {"User-Agent": user_agent(), "Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            _respect_rate_limit(url, min_interval)
            with httpx.Client(timeout=timeout, follow_redirects=True, headers=request_headers) as client:
                response = client.request(method, url, params=params, json=json_body)
            if response.status_code in {429, 500, 502, 503, 504}:
                raise HttpError(
                    f"HTTP {response.status_code} for {url}",
                    status_code=response.status_code,
                    temporary=True,
                )
            if response.status_code in {401, 403}:
                raise HttpError(
                    f"HTTP {response.status_code} for {url} — access denied, not retrying with evasion",
                    status_code=response.status_code,
                    temporary=False,
                )
            if response.status_code == 404:
                raise HttpError(f"HTTP 404 for {url}", status_code=404, temporary=False)
            if response.status_code >= 400:
                raise HttpError(
                    f"HTTP {response.status_code} for {url}",
                    status_code=response.status_code,
                    temporary=response.status_code >= 500,
                )
            data = response.json()
            if use_cache:
                _write_cache(cache_file, data)
            return data
        except HttpError as exc:
            last_error = exc
            if not exc.temporary or attempt >= retries:
                raise
            time.sleep(backoff * (2**attempt))
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last_error = HttpError(f"Network error for {url}: {exc}", temporary=True)
            if attempt >= retries:
                raise last_error from exc
            time.sleep(backoff * (2**attempt))
    raise last_error or HttpError(f"Request failed for {url}", temporary=True)


def check_url(url: str) -> str:
    """Return ACTIVE, NOT_FOUND, TEMPORARY_ERROR, or UNKNOWN without aggressive retries."""
    try:
        _respect_rate_limit(url, settings()["http"]["min_interval_seconds"])
        headers = {"User-Agent": user_agent()}
        with httpx.Client(timeout=10, follow_redirects=True, headers=headers) as client:
            response = client.head(url)
            if response.status_code in {405, 501}:
                response = client.get(url)
        if response.status_code == 404:
            return "NOT_FOUND"
        if response.status_code in {429, 500, 502, 503, 504}:
            return "TEMPORARY_ERROR"
        if 200 <= response.status_code < 400:
            return "ACTIVE"
        return "UNKNOWN"
    except (httpx.TimeoutException, httpx.NetworkError):
        return "TEMPORARY_ERROR"
    except Exception:
        return "UNKNOWN"
