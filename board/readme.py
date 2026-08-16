"""Generate the GitHub README internship board from jobs.json."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable

from board.config import settings
from board.constants import CATEGORIES, CATEGORY_ANCHORS, CATEGORY_EMOJI
from board.models import Job
from board.storage import JsonJobRepository, utc_today

JOBS_START = "<!-- JOBS:START -->"
JOBS_END = "<!-- JOBS:END -->"


def format_posted(date_iso: str | None, today: str) -> str:
    if not date_iso:
        return "—"
    try:
        parsed = datetime.strptime(date_iso, "%Y-%m-%d").date()
    except ValueError:
        return "—"
    current_year = datetime.strptime(today, "%Y-%m-%d").year
    if parsed.year == current_year:
        return parsed.strftime("%b ") + str(parsed.day)
    return parsed.strftime("%b ") + f"{parsed.day}, {parsed.year}"


def _is_new(job: Job, today: str, hours: int) -> bool:
    try:
        discovered = datetime.strptime(job.date_discovered, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.strptime(today, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return now - discovered <= timedelta(hours=hours)


def display_location(job: Job) -> str:
    if job.work_arrangement == "Remote":
        return "Remote"
    return job.location or "Unknown"


def display_title(job: Job, today: str) -> str:
    hours = int(settings()["readme"]["new_job_hours"])
    badge = " 🆕" if _is_new(job, today, hours) else ""
    return f"{job.title}{badge}"


def sort_jobs(jobs: Iterable[Job]) -> list[Job]:
    secondary = settings()["readme"].get("secondary_sort") == "company"

    def key(job: Job) -> tuple:
        posted = job.date_posted or "0000-00-00"
        company = job.company.lower() if secondary else ""
        return (posted, company, job.title.lower())

    # Newest posted date first; missing dates sort as 0000-00-00 and land last.
    return sorted(jobs, key=key, reverse=True)


def stats_markdown(jobs: list[Job], today: str) -> str:
    active = [job for job in jobs if job.active]
    companies = {job.company for job in active}
    categories = {job.category for job in active if job.category != "Other"}
    hours = int(settings()["readme"]["new_job_hours"])
    added = sum(1 for job in active if _is_new(job, today, 24))
    last_updated = datetime.strptime(today, "%Y-%m-%d").strftime("%B ") + str(
        datetime.strptime(today, "%Y-%m-%d").day
    ) + datetime.strptime(today, "%Y-%m-%d").strftime(", %Y")
    return "\n".join(
        [
            f"📊 **{len(active):,}** active jobs",
            f"🏢 **{len(companies):,}** companies",
            f"🆕 **{added:,}** added in the last 24 hours",
            f"📁 **{len(categories):,}** categories with listings",
            f"🕒 Last updated: **{last_updated}**",
        ]
    )


def category_nav(present: set[str]) -> str:
    lines = ["## Categories", ""]
    for category in CATEGORIES:
        if category == "Other" and category not in present:
            continue
        emoji = CATEGORY_EMOJI[category]
        anchor = CATEGORY_ANCHORS[category]
        lines.append(f"- [{emoji} {category}](#{anchor})")
    lines.append("")
    return "\n".join(lines)


def category_table(category: str, jobs: list[Job], today: str, limit: int) -> str:
    emoji = CATEGORY_EMOJI[category]
    anchor = CATEGORY_ANCHORS[category]
    ordered = sort_jobs(jobs)
    visible = ordered[:limit]
    extra = len(ordered) - len(visible)
    rows = [
        f'<h2 id="{anchor}">{emoji} {category}</h2>',
        "",
        f"_{len(ordered)} active listing{'s' if len(ordered) != 1 else ''}_",
        "",
        "| Company | Position | Location | Type | Posted | Apply |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for job in visible:
        title = display_title(job, today).replace("|", "\\|")
        company = job.company.replace("|", "\\|")
        location = display_location(job).replace("|", "\\|")
        rows.append(
            f"| {company} | {title} | {location} | {job.job_type} | "
            f"{format_posted(job.date_posted, today)} | "
            f"[Apply ↗]({job.application_url}) |"
        )
    if extra > 0:
        rows.append("")
        rows.append(f"_Showing the {limit} newest listings. {extra} more are stored in `data/jobs.json`._")
    rows.append("")
    return "\n".join(rows)


def render_jobs_section(jobs: list[Job], today: str | None = None) -> str:
    today = today or utc_today()
    active = [job for job in jobs if job.active and not job.seed]
    by_category: dict[str, list[Job]] = defaultdict(list)
    for job in active:
        by_category[job.category].append(job)
    limit = int(settings()["readme"]["max_jobs_per_category"])
    parts = [
        stats_markdown(active, today),
        "",
        category_nav(set(by_category)),
    ]
    if not active:
        parts.append("_No active listings yet. Run `python scripts/update_jobs.py --all` to collect public postings._")
        parts.append("")
    for category in CATEGORIES:
        listings = by_category.get(category) or []
        if not listings:
            continue
        parts.append(category_table(category, listings, today, limit))
    return "\n".join(parts).rstrip() + "\n"


def replace_generated_section(readme: str, generated: str) -> str:
    if JOBS_START not in readme or JOBS_END not in readme:
        raise ValueError("README.md is missing <!-- JOBS:START --> / <!-- JOBS:END --> markers")
    before, rest = readme.split(JOBS_START, 1)
    _, after = rest.split(JOBS_END, 1)
    return f"{before}{JOBS_START}\n{generated.rstrip()}\n{JOBS_END}{after}"


def generate_readme(readme_path=None, jobs: list[Job] | None = None) -> str:
    from pathlib import Path

    from board.config import repo_root

    path = readme_path or settings()["paths"]["readme"]
    readme_file = Path(path)
    if not readme_file.is_absolute():
        readme_file = repo_root() / readme_file
    current = readme_file.read_text(encoding="utf-8")
    listings = jobs if jobs is not None else JsonJobRepository().load()
    generated = render_jobs_section(listings)
    updated = replace_generated_section(current, generated)
    readme_file.write_text(updated, encoding="utf-8")
    return updated
