from board.expiration import expire_missing_jobs
from board.models import Job
from board.pipeline import merge_jobs, raw_to_job
from board.models import RawJob
from board.storage import utc_today


def _job(**overrides) -> Job:
    data = {
        "id": "amazon-1",
        "company": "Amazon",
        "title": "Supply Chain Intern",
        "location": "Seattle, WA",
        "category": "Supply Chain",
        "job_type": "Internship",
        "application_url": "https://www.amazon.jobs/en/jobs/1",
        "source": "Amazon Careers",
        "source_key": "amazon",
        "date_discovered": "2026-08-01",
        "last_verified": "2026-08-01",
        "active": True,
        "consecutive_misses": 0,
    }
    data.update(overrides)
    return Job.model_validate(data)


def test_failed_source_does_not_expire_jobs():
    existing = [_job()]
    updated, expired = expire_missing_jobs(existing, seen_ids_by_source={}, successful_sources=set())
    assert expired == 0
    assert updated[0].active is True


def test_successful_source_expires_after_repeated_misses():
    existing = [_job(consecutive_misses=1)]
    updated, expired = expire_missing_jobs(
        existing,
        seen_ids_by_source={"amazon": set()},
        successful_sources={"amazon"},
    )
    assert expired == 1
    assert updated[0].active is False


def test_merge_keeps_discovered_date():
    existing = [_job()]
    incoming = [_job(title="Supply Chain Intern - Seattle", last_verified="2026-08-16")]
    merged, new_count, updated_count = merge_jobs(existing, incoming, "2026-08-16")
    assert new_count == 0
    assert updated_count == 1
    assert merged[0].date_discovered == "2026-08-01"
    assert merged[0].title.startswith("Supply Chain Intern")


def test_raw_to_job_drops_unrelated_full_time():
    raw = RawJob(
        company="Amazon",
        title="Software Development Engineer",
        application_url="https://www.amazon.jobs/en/jobs/9",
        source="Amazon Careers",
        source_key="amazon",
        location="Austin, TX",
    )
    assert raw_to_job(raw, today=utc_today()) is None


def test_raw_to_job_keeps_relevant_intern():
    raw = RawJob(
        company="Amazon.com Services LLC",
        title="Supply Chain Intern - Summer 2027",
        application_url="https://www.amazon.jobs/en/jobs/12345/supply-chain-intern",
        source="Amazon Careers",
        source_key="amazon",
        location="Seattle, WA",
        source_job_id="12345",
        date_posted="August 15, 2026",
    )
    job = raw_to_job(raw, today="2026-08-16")
    assert job is not None
    assert job.company == "Amazon"
    assert job.category == "Supply Chain"
    assert job.id == "amazon-12345"


def test_raw_to_job_drops_non_us_location():
    raw = RawJob(
        company="Amazon",
        title="Supply Chain Intern",
        application_url="https://www.amazon.jobs/en/jobs/10404513/instock-intern",
        source="Amazon Careers",
        source_key="amazon",
        location="Sao Paulo, Sao Paulo, BRA",
        source_job_id="10404513",
    )
    assert raw_to_job(raw, today=utc_today()) is None


def test_raw_to_job_drops_finance_intern():
    raw = RawJob(
        company="Amazon",
        title="2027 Amazon Operations Finance Rotational Program Summer Internship",
        application_url="https://www.amazon.jobs/en/jobs/10435673/finance",
        source="Amazon Careers",
        source_key="amazon",
        location="Seattle, WA",
        source_job_id="10435673",
    )
    assert raw_to_job(raw, today=utc_today()) is None
