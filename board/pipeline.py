"""SOURCE → SCRAPE → NORMALIZE → CLASSIFY → DEDUPE → VALIDATE → STORE → README."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

from board.classification import classify_text, is_relevant, looks_like_early_career
from board.config import path_from_settings, settings
from board.deduplication import deduplicate_jobs
from board.expiration import expire_missing_jobs
from board.ids import make_job_id
from board.models import Job, RawJob
from board.normalization import (
    infer_job_type,
    infer_work_arrangement,
    normalize_application_url,
    normalize_company,
    normalize_title,
    normalized_title_key,
    parse_iso_date,
    parse_location,
)
from board.overrides import apply_overrides
from board.storage import JsonJobRepository, load_json, save_json, utc_now_iso, utc_today
from board.validation import assert_jobs_valid, validate_job


@dataclass
class UpdateReport:
    sources_attempted: int = 0
    sources_successful: int = 0
    sources_failed: int = 0
    jobs_discovered: int = 0
    new_jobs: int = 0
    updated_jobs: int = 0
    expired_jobs: int = 0
    duplicates_removed: int = 0
    total_active: int = 0
    failed_sources: list[str] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)

    def render(self) -> str:
        lines = [
            "=====================================",
            "INTERNSHIP BOARD UPDATE",
            "=====================================",
            "",
            f"Sources attempted: {self.sources_attempted}",
            f"Sources successful: {self.sources_successful}",
            f"Sources failed: {self.sources_failed}",
            "",
            f"Jobs discovered: {self.jobs_discovered}",
            f"New jobs: {self.new_jobs}",
            f"Updated jobs: {self.updated_jobs}",
            f"Expired jobs: {self.expired_jobs}",
            f"Duplicates removed: {self.duplicates_removed}",
            "",
            f"Total active jobs: {self.total_active:,}",
            "=====================================",
        ]
        if self.failed_sources:
            lines.insert(-1, "")
            for name in self.failed_sources:
                lines.insert(-1, f"{name} scraper failed:")
                lines.insert(-1, f"  {self.errors.get(name, 'unknown error')}")
                lines.insert(-1, "  Existing listings preserved.")
        return "\n".join(lines)


def raw_to_job(raw: RawJob, *, today: str) -> Job | None:
    title = normalize_title(raw.title)
    if not looks_like_early_career(title, raw.job_type, raw.extra.get("commitment", "")):
        return None
    company = normalize_company(raw.company)
    parsed_loc = parse_location(raw.location)
    location = parsed_loc["location"] or "Unknown"
    classification = classify_text(title, raw.description)
    if not is_relevant(title, raw.description, classification.category):
        return None
    application_url = normalize_application_url(raw.application_url)
    if not application_url:
        return None
    job_type = infer_job_type(title, raw.job_type)
    arrangement = infer_work_arrangement(raw.location, raw.work_arrangement, raw.description)
    if arrangement == "Unknown" and parsed_loc["location"] == "Remote":
        arrangement = "Remote"
    date_posted = parse_iso_date(raw.date_posted)
    max_desc = int(settings()["pipeline"]["description_max_chars"])
    description = (raw.description or "")[:max_desc]
    source_job_id = str(raw.source_job_id) if raw.source_job_id else None
    job_id = make_job_id(
        company,
        source_job_id=source_job_id,
        title=title,
        location=location,
        application_url=application_url,
    )
    job = Job(
        id=job_id,
        company=company,
        title=title,
        normalized_title=normalized_title_key(title),
        location=location if arrangement != "Remote" else "Remote",
        city=parsed_loc["city"],
        state=parsed_loc["state"],
        country=parsed_loc["country"],
        category=classification.category,
        subcategory=classification.subcategory,
        category_confidence=classification.confidence,
        job_type=job_type,
        work_arrangement=arrangement,
        date_posted=date_posted,
        date_discovered=today,
        application_url=application_url,
        source_url=raw.source_url or application_url,
        source=raw.source,
        source_key=raw.source_key,
        source_job_id=source_job_id,
        description=description,
        salary_min=raw.salary_min,
        salary_max=raw.salary_max,
        salary_currency=raw.salary_currency,
        sponsorship=raw.sponsorship or "Unknown",
        active=True,
        last_verified=today,
        needs_review=classification.needs_review,
    )
    if validate_job(job):
        return None
    return job


def refresh_classifications(jobs: list[Job]) -> list[Job]:
    """Re-apply current rules so config edits take effect without waiting for expiry."""
    for job in jobs:
        result = classify_text(job.title, job.description)
        job.category = result.category
        job.category_confidence = result.confidence
        job.subcategory = result.subcategory
        job.needs_review = result.needs_review
        job.job_type = infer_job_type(job.title)
        if job.active and (
            not looks_like_early_career(job.title)
            or not is_relevant(job.title, job.description, job.category)
        ):
            job.active = False
    return [
        job
        for job in jobs
        if job.active or (job.consecutive_misses > 0 and looks_like_early_career(job.title))
    ]


def merge_jobs(existing: list[Job], incoming: list[Job], today: str) -> tuple[list[Job], int, int]:
    by_id = {job.id: job for job in existing}
    new_count = 0
    updated_count = 0
    for job in incoming:
        current = by_id.get(job.id)
        if current is None:
            job.date_discovered = today
            by_id[job.id] = job
            new_count += 1
            continue
        before = current.model_dump()
        current.merge_from(job)
        current.date_discovered = min(current.date_discovered, job.date_discovered)
        if current.model_dump() != before:
            updated_count += 1
    return list(by_id.values()), new_count, updated_count


def collect_from_scrapers(
    scrapers: Iterable,
    *,
    persist_status: bool = True,
) -> tuple[list[RawJob], UpdateReport, set[str], dict[str, set[str]]]:
    report = UpdateReport()
    discovered: list[RawJob] = []
    successful: set[str] = set()
    seen_ids: dict[str, set[str]] = defaultdict(set)
    status_path = path_from_settings("status")
    status = load_json(status_path, {"sources": {}})
    sources_status = status.setdefault("sources", {})
    now = utc_now_iso()
    cap = int(settings()["pipeline"]["max_jobs_per_source"])

    for scraper in scrapers:
        name = scraper.name
        report.sources_attempted += 1
        entry = sources_status.setdefault(name, {})
        entry["last_attempted_run"] = now
        try:
            jobs = list(scraper.fetch_jobs())
            jobs = [
                job
                for job in jobs
                if looks_like_early_career(job.title, job.job_type, job.extra.get("commitment", ""))
            ]
            if len(jobs) > cap:
                jobs = jobs[:cap]
            discovered.extend(jobs)
            successful.add(name)
            report.sources_successful += 1
            report.source_counts[name] = len(jobs)
            report.jobs_discovered += len(jobs)
            entry["status"] = "ok"
            entry["error"] = None
            entry["last_successful_run"] = now
            entry["jobs_found"] = len(jobs)
            print(f"[{scraper.company if hasattr(scraper, 'company') else name}] Found {len(jobs)} jobs")
        except Exception as exc:  # noqa: BLE001 — scraper isolation is intentional
            report.sources_failed += 1
            report.failed_sources.append(name)
            message = str(exc)
            report.errors[name] = message
            entry["status"] = "error"
            entry["error"] = message[:500]
            entry["jobs_found"] = entry.get("jobs_found", 0)
            label = getattr(scraper, "company", name)
            print(f"[{label}] scraper failed:")
            print(f"  {message}")
            print("  Existing listings preserved.")
        sources_status[name] = entry

    if persist_status:
        save_json(status_path, status)
    return discovered, report, successful, seen_ids


def run_update(
    scrapers: Iterable,
    *,
    dry_run: bool = False,
    repository: JsonJobRepository | None = None,
) -> UpdateReport:
    today = utc_today()
    repo = repository or JsonJobRepository()
    existing = repo.load()
    raw_jobs, report, successful, _ = collect_from_scrapers(scrapers, persist_status=not dry_run)

    incoming: list[Job] = []
    for raw in raw_jobs:
        job = raw_to_job(raw, today=today)
        if job:
            incoming.append(job)

    incoming, dupes = deduplicate_jobs(incoming)
    report.duplicates_removed += dupes

    merged, new_count, updated_count = merge_jobs(existing, incoming, today)
    report.new_jobs = new_count
    report.updated_jobs = updated_count
    merged = refresh_classifications(merged)

    seen_ids: dict[str, set[str]] = defaultdict(set)
    for job in incoming:
        seen_ids[job.source_key].add(job.id)
    for name in successful:
        seen_ids.setdefault(name, set())

    merged, expired = expire_missing_jobs(merged, seen_ids, successful)
    report.expired_jobs = expired
    merged = apply_overrides(merged)
    merged, more_dupes = deduplicate_jobs(merged)
    report.duplicates_removed += more_dupes

    active = [job for job in merged if job.active]
    assert_jobs_valid(active)
    report.total_active = len(active)

    print(f"Added: {report.new_jobs}")
    print(f"Updated: {report.updated_jobs}")
    print(f"Expired: {report.expired_jobs}")
    print(f"Duplicates removed: {report.duplicates_removed}")
    print(report.render())

    if not dry_run:
        repo.save(merged)
    return report
