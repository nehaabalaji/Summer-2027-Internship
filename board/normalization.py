"""Normalize titles, companies, locations, dates, types, and URLs."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser

from board.constants import (
    COMPANY_ALIASES,
    COUNTRY_ALIASES,
    ISO3_COUNTRIES,
    JOB_TYPES,
    US_ABBREV_TO_NAME,
    US_STATE_ABBREV,
    WORK_ARRANGEMENTS,
)
from board.urls import application_url_for_storage

_WHITESPACE = re.compile(r"\s+")
_REMOTE_RE = re.compile(r"\b(remote|work from home|wfh|virtual)\b", re.I)
_HYBRID_RE = re.compile(r"\bhybrid\b", re.I)
_ONSITE_RE = re.compile(r"\b(on[\s-]?site|in[\s-]?office)\b", re.I)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def collapse_ws(value: str) -> str:
    return _WHITESPACE.sub(" ", (value or "").replace("\xa0", " ")).strip()


def phrase_in(text: str, phrase: str) -> bool:
    """Whole-phrase match after normalizing punctuation to spaces."""
    haystack = f" {_NON_ALNUM.sub(' ', (text or '').lower()).strip()} "
    needle = f" {_NON_ALNUM.sub(' ', (phrase or '').lower()).strip()} "
    return needle != "  " and needle in haystack


def collapse_ws(value: str) -> str:
    return _WHITESPACE.sub(" ", (value or "").replace("\xa0", " ")).strip()


def normalize_company(name: str) -> str:
    cleaned = collapse_ws(name)
    return COMPANY_ALIASES.get(cleaned.lower(), cleaned)


def normalize_title(title: str) -> str:
    """Light cleanup only — keep season/year because they are meaningful."""
    cleaned = collapse_ws(title)
    cleaned = cleaned.replace("–", "-").replace("—", "-")
    cleaned = re.sub(r"\s*[-|/]\s*", " - ", cleaned)
    cleaned = collapse_ws(cleaned)
    return cleaned.strip(" -")


def normalized_title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize_title(title).lower()).strip()


def parse_iso_date(value: object) -> Optional[str]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        # Lever uses epoch milliseconds.
        ts = float(value)
        if ts > 10_000_000_000:
            ts = ts / 1000.0
        try:
            return datetime.utcfromtimestamp(ts).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    relative = _relative_workday_date(text)
    if relative:
        return relative
    try:
        parsed = date_parser.parse(text, fuzzy=True)
        return parsed.date().isoformat()
    except (ValueError, OverflowError, TypeError):
        return None


def _relative_workday_date(text: str) -> Optional[str]:
    lowered = text.lower().strip()
    today = datetime.utcnow().date()
    if "today" in lowered:
        return today.isoformat()
    if "yesterday" in lowered:
        from datetime import timedelta

        return (today - timedelta(days=1)).isoformat()
    match = re.search(r"posted\s+(\d+)\s+days?\s+ago", lowered)
    if match:
        from datetime import timedelta

        return (today - timedelta(days=int(match.group(1)))).isoformat()
    if "30+" in lowered:
        return None
    return None


def infer_job_type(title: str, source_type: Optional[str] = None) -> str:
    title_has_intern = phrase_in(title, "intern") or phrase_in(title, "internship")
    if source_type in JOB_TYPES:
        if source_type in {"Internship", "Summer Internship", "Fall Internship", "Spring Internship", "Part-time Internship", "Full-time Internship"} and not title_has_intern:
            source_type = None
        elif source_type:
            return source_type
    blob = title or ""
    if phrase_in(blob, "co-op") or phrase_in(blob, "coop") or phrase_in(blob, "co op"):
        return "Co-op"
    if phrase_in(blob, "new grad") or phrase_in(blob, "new graduate"):
        return "New Graduate"
    if phrase_in(blob, "entry level") or phrase_in(blob, "entry-level"):
        return "Entry Level"
    if phrase_in(blob, "intern") or phrase_in(blob, "internship"):
        if phrase_in(blob, "summer"):
            return "Summer Internship"
        if phrase_in(blob, "fall") or phrase_in(blob, "autumn"):
            return "Fall Internship"
        if phrase_in(blob, "spring"):
            return "Spring Internship"
        if phrase_in(blob, "part-time") or phrase_in(blob, "part time"):
            return "Part-time Internship"
        if phrase_in(blob, "full-time") or phrase_in(blob, "full time"):
            return "Full-time Internship"
        return "Internship"
    return "Unknown"


def infer_work_arrangement(
    location: str,
    source_arrangement: Optional[str] = None,
    description: str = "",
) -> str:
    if source_arrangement in WORK_ARRANGEMENTS:
        return source_arrangement
    blob = f"{location} {source_arrangement or ''} {description[:400]}"
    if _REMOTE_RE.search(blob) and _HYBRID_RE.search(blob):
        return "Hybrid"
    if _HYBRID_RE.search(blob):
        return "Hybrid"
    if _REMOTE_RE.search(location) or (
        _REMOTE_RE.search(blob) and not _ONSITE_RE.search(location)
    ):
        # Only treat as Remote when the location/source says so — never guess from job family.
        if _REMOTE_RE.search(location) or (source_arrangement and _REMOTE_RE.search(source_arrangement)):
            return "Remote"
    if _ONSITE_RE.search(blob):
        return "On-site"
    return "Unknown"


def parse_location(raw: str) -> dict[str, Optional[str]]:
    text = collapse_ws(raw.replace("—", ",").replace("–", ","))
    if not text:
        return {"location": "Unknown", "city": None, "state": None, "country": None}
    if _REMOTE_RE.search(text) and "," not in text and "united states" in text.lower():
        return {
            "location": "Remote — United States",
            "city": None,
            "state": None,
            "country": "United States",
        }
    if _REMOTE_RE.search(text) and len(text.split(",")) == 1:
        country = None
        for alias, name in COUNTRY_ALIASES.items():
            if re.search(rf"\b{re.escape(alias)}\b", text.lower()):
                country = name
                break
        label = f"Remote — {country}" if country else "Remote"
        return {"location": label, "city": None, "state": None, "country": country}

    parts = [collapse_ws(p) for p in text.split(",") if collapse_ws(p)]
    city = parts[0] if parts else None
    state = None
    country = None
    rest = [p for p in parts[1:]]
    for token in rest:
        upper = token.upper()
        lower = token.lower()
        if upper in US_STATE_ABBREV.values() and len(upper) == 2:
            state = upper
        elif lower in US_STATE_ABBREV:
            state = US_STATE_ABBREV[lower]
        elif upper in ISO3_COUNTRIES:
            country = ISO3_COUNTRIES[upper]
        elif lower in COUNTRY_ALIASES:
            country = COUNTRY_ALIASES[lower]
        elif not state and len(token) > 2:
            maybe_state = US_STATE_ABBREV.get(lower)
            if maybe_state:
                state = maybe_state
    if state and not country:
        country = "United States"
    if city and city.lower() in {"remote", "virtual", "anywhere"}:
        location = "Remote — United States" if country == "United States" else "Remote"
        return {"location": location, "city": None, "state": None, "country": country}
    if city and state:
        location = f"{city}, {state}"
    elif city and country:
        location = f"{city}, {country}"
    else:
        location = text
    return {"location": location, "city": city, "state": state, "country": country}


_FOREIGN_LOCATION_MARKERS: tuple[str, ...] = (
    "united kingdom",
    "great britain",
    "canada",
    "china",
    "brazil",
    "india",
    "mexico",
    "germany",
    "france",
    "italy",
    "ireland",
    "australia",
    "japan",
    "singapore",
    "netherlands",
    "spain",
    "poland",
    "czech",
    "south africa",
    "south korea",
    "hong kong",
    "taiwan",
    "united arab emirates",
    "new zealand",
    "costa rica",
    "colombia",
    "argentina",
    "philippines",
    "indonesia",
    "malaysia",
    "thailand",
    "vietnam",
    "israel",
    "sweden",
    "norway",
    "denmark",
    "switzerland",
    "austria",
    "belgium",
    "portugal",
    "romania",
    "hungary",
    "luxembourg",
)


def is_us_job(
    parsed: dict[str, Optional[str]],
    raw: str = "",
    arrangement: str = "",
) -> bool:
    """Keep United States roles only, including US remote."""
    country = parsed.get("country") or ""
    if country and country != "United States":
        return False
    raw_l = collapse_ws(raw or "").lower()
    if any(re.search(rf"\b{re.escape(marker)}\b", raw_l) for marker in _FOREIGN_LOCATION_MARKERS):
        return False
    for token in re.split(r"[^a-z0-9]+", raw_l):
        if not token:
            continue
        iso = token.upper()
        if iso in ISO3_COUNTRIES and ISO3_COUNTRIES[iso] != "United States":
            return False
        if token in COUNTRY_ALIASES and COUNTRY_ALIASES[token] != "United States":
            return False
    if (parsed.get("state") or "") in US_ABBREV_TO_NAME:
        city = (parsed.get("city") or "").lower()
        if city == "amsterdam" and parsed.get("state") == "NH":
            return False
        return True
    if country == "United States":
        return True
    location = (parsed.get("location") or "").lower()
    if arrangement == "Remote" or location.startswith("remote"):
        return True
    return False


def normalize_application_url(url: str) -> str:
    return application_url_for_storage(url)
