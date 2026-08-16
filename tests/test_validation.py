from board.models import Job
from board.storage import utc_today
from board.validation import validate_job


def _job(**overrides) -> Job:
    data = {
        "id": "amazon-12345",
        "company": "Amazon",
        "title": "Supply Chain Intern",
        "location": "Seattle, WA",
        "category": "Supply Chain",
        "job_type": "Internship",
        "application_url": "https://www.amazon.jobs/en/jobs/12345/supply-chain-intern",
        "source": "Amazon Careers",
        "date_discovered": utc_today(),
        "last_verified": utc_today(),
    }
    data.update(overrides)
    return Job.model_validate(data)


def test_valid_job_has_no_errors():
    assert validate_job(_job()) == []


def test_missing_company():
    errors = validate_job(_job(company=" "))
    assert any("company" in error for error in errors)


def test_missing_title():
    errors = validate_job(_job(title=""))
    assert any("title" in error for error in errors)


def test_invalid_url():
    errors = validate_job(_job(application_url="not-a-url"))
    assert any("application_url" in error for error in errors)


def test_placeholder_url_rejected():
    errors = validate_job(_job(application_url="https://example.com/job"))
    assert any("placeholder" in error for error in errors)


def test_invalid_category():
    try:
        _job(category="Marketing")
        assert False, "expected category validation error"
    except Exception as exc:
        assert "category" in str(exc).lower()
