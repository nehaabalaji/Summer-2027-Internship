from board.models import Job
from board.readme import JOBS_END, JOBS_START, render_jobs_section, replace_generated_section, sort_jobs
from board.storage import utc_today


def _job(**overrides) -> Job:
    data = {
        "id": "amazon-1",
        "company": "Amazon",
        "title": "Supply Chain Intern",
        "location": "Seattle, WA",
        "category": "Supply Chain",
        "job_type": "Internship",
        "application_url": "https://www.amazon.jobs/en/jobs/1/supply-chain-intern",
        "source": "Amazon Careers",
        "date_discovered": utc_today(),
        "last_verified": utc_today(),
        "date_posted": "2026-08-15",
        "active": True,
    }
    data.update(overrides)
    return Job.model_validate(data)


def test_readme_contains_category_and_apply_url():
    markdown = render_jobs_section(
        [
            _job(),
            _job(
                id="msft-1",
                company="Microsoft",
                title="Product Management Intern",
                category="Product Management",
                location="Remote",
                work_arrangement="Remote",
                application_url="https://jobs.careers.microsoft.com/job/pm-intern",
                date_posted="2026-08-01",
            ),
        ],
        today="2026-08-16",
    )
    assert "Supply Chain" in markdown
    assert "Product Management" in markdown
    assert "[Apply ↗](https://www.amazon.jobs/en/jobs/1/supply-chain-intern)" in markdown
    assert "active jobs" in markdown.lower()
    assert "| Company | Position | Location | Type | Posted | Apply |" in markdown


def test_readme_markers_only_replace_generated_block():
    original = "# Title\n\nkeep me\n\n<!-- JOBS:START -->\nold\n<!-- JOBS:END -->\n\nfooter\n"
    updated = replace_generated_section(original, "new table\n")
    assert "keep me" in updated
    assert "footer" in updated
    assert "old" not in updated
    assert JOBS_START in updated and JOBS_END in updated


def test_newest_jobs_first_unknown_last():
    older = _job(id="a", date_posted="2026-08-01", title="A")
    newer = _job(id="b", date_posted="2026-08-15", title="B")
    unknown = _job(id="c", date_posted=None, title="C")
    ordered = sort_jobs([older, unknown, newer])
    assert [job.id for job in ordered] == ["b", "a", "c"]


def test_inactive_jobs_omitted():
    markdown = render_jobs_section([_job(active=False)], today="2026-08-16")
    assert "Apply ↗" not in markdown
