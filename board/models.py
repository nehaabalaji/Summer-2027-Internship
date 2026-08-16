"""Job data model. Storage is JSON today; this schema can map to SQLite later."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from board.constants import CATEGORIES, JOB_TYPES, SPONSORSHIP_VALUES, WORK_ARRANGEMENTS


class Job(BaseModel):
    """Normalized internship / early-career listing."""

    id: str
    company: str
    company_logo: str = ""
    title: str
    normalized_title: str = ""
    location: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    category_confidence: float = 0.0
    job_type: str = "Unknown"
    work_arrangement: str = "Unknown"
    date_posted: Optional[str] = None
    date_discovered: str
    application_url: str
    source_url: str = ""
    source: str
    source_key: str = ""
    source_job_id: Optional[str] = None
    description: str = ""
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    sponsorship: str = "Unknown"
    active: bool = True
    last_verified: str
    needs_review: bool = False
    consecutive_misses: int = 0
    seed: bool = False

    @field_validator("category")
    @classmethod
    def _category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError(f"Unknown category: {value}")
        return value

    @field_validator("job_type")
    @classmethod
    def _job_type(cls, value: str) -> str:
        if value not in JOB_TYPES:
            raise ValueError(f"Unknown job_type: {value}")
        return value

    @field_validator("work_arrangement")
    @classmethod
    def _arrangement(cls, value: str) -> str:
        if value not in WORK_ARRANGEMENTS:
            raise ValueError(f"Unknown work_arrangement: {value}")
        return value

    @field_validator("sponsorship")
    @classmethod
    def _sponsorship(cls, value: str) -> str:
        if value not in SPONSORSHIP_VALUES:
            raise ValueError(f"Unknown sponsorship: {value}")
        return value

    def merge_from(self, incoming: "Job") -> "Job":
        """Update mutable fields from a newly scraped copy while keeping stable IDs."""
        self.title = incoming.title
        self.normalized_title = incoming.normalized_title
        self.location = incoming.location
        self.city = incoming.city
        self.state = incoming.state
        self.country = incoming.country
        self.category = incoming.category
        self.subcategory = incoming.subcategory
        self.category_confidence = incoming.category_confidence
        self.job_type = incoming.job_type
        self.work_arrangement = incoming.work_arrangement
        if incoming.date_posted:
            self.date_posted = incoming.date_posted
        self.application_url = incoming.application_url
        self.source_url = incoming.source_url or self.source_url
        self.description = incoming.description
        self.salary_min = incoming.salary_min
        self.salary_max = incoming.salary_max
        self.salary_currency = incoming.salary_currency
        if incoming.sponsorship != "Unknown":
            self.sponsorship = incoming.sponsorship
        self.active = True
        self.last_verified = incoming.last_verified
        self.needs_review = incoming.needs_review
        self.consecutive_misses = 0
        return self


class RawJob(BaseModel):
    """Minimally structured record returned by a scraper before normalization."""

    company: str
    title: str
    application_url: str
    source: str
    source_key: str
    location: str = ""
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    description: str = ""
    job_type: Optional[str] = None
    work_arrangement: Optional[str] = None
    date_posted: Optional[str] = None
    source_url: str = ""
    source_job_id: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: Optional[str] = None
    sponsorship: Optional[str] = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ScraperRunResult(BaseModel):
    source: str
    status: str
    jobs_found: int = 0
    error: Optional[str] = None
    attempted_at: str
    succeeded_at: Optional[str] = None
