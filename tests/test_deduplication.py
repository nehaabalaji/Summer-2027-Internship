from board.deduplication import deduplicate_jobs
from board.models import Job
from board.storage import utc_today


def _job(**overrides) -> Job:
    data = {
        "id": "acme-1",
        "company": "Acme",
        "title": "Supply Chain Intern",
        "location": "Houston, TX",
        "category": "Supply Chain",
        "job_type": "Internship",
        "application_url": "https://jobs.acme.com/supply-chain-intern",
        "source": "Acme Careers",
        "date_discovered": utc_today(),
        "last_verified": utc_today(),
        "date_posted": "2026-08-01",
    }
    data.update(overrides)
    return Job.model_validate(data)


def test_exact_duplicate():
    jobs, removed = deduplicate_jobs([_job(), _job(id="acme-2")])
    assert len(jobs) == 1
    assert removed == 1


def test_url_duplicate_ignores_tracking_params():
    first = _job(application_url="https://jobs.acme.com/role?utm_source=board")
    second = _job(
        id="acme-2",
        application_url="https://jobs.acme.com/role",
        date_posted="2026-08-10",
    )
    jobs, removed = deduplicate_jobs([first, second])
    assert len(jobs) == 1
    assert removed == 1
    assert jobs[0].date_posted == "2026-08-10"


def test_title_location_duplicate():
    first = _job(application_url="https://jobs.acme.com/a")
    second = _job(
        id="acme-2",
        application_url="https://careers.acme.com/a",
        title="Supply Chain Intern",
        location="Houston, TX",
    )
    jobs, removed = deduplicate_jobs([first, second])
    assert len(jobs) == 1
    assert removed == 1
