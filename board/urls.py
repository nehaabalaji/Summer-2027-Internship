"""URL canonicalization that does not break employer application links."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from board.constants import PLACEHOLDER_URLS, TRACKING_QUERY_PARAMS

FAKE_HOSTS = {
    "example.com",
    "www.example.com",
    "example.org",
    "localhost",
    "127.0.0.1",
    "test.com",
    "foo.bar",
}


def is_placeholder_url(url: str) -> bool:
    cleaned = (url or "").strip().lower().rstrip("/")
    if cleaned in PLACEHOLDER_URLS:
        return True
    try:
        host = urlsplit(url).hostname or ""
    except ValueError:
        return True
    return host.lower() in FAKE_HOSTS


def canonicalize_url(url: str, *, strip_tracking: bool = True) -> str:
    """Normalize a URL for comparison while preserving required query params."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower() or "https"
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path or ""
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    if strip_tracking:
        query_pairs = [
            (key, value)
            for key, value in query_pairs
            if key.lower() not in TRACKING_QUERY_PARAMS
        ]
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))


def application_url_for_storage(url: str) -> str:
    """Store a cleaned URL that still points at the original employer page."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_PARAMS
    ]
    path = parts.path or ""
    return urlunsplit((parts.scheme, parts.netloc, path, urlencode(query_pairs, doseq=True), ""))
