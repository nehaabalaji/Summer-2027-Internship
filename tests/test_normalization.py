from board.ids import make_job_id
from board.normalization import (
    infer_job_type,
    is_us_job,
    normalize_application_url,
    normalize_company,
    normalize_title,
    parse_iso_date,
    parse_location,
)
from board.urls import canonicalize_url


def test_company_alias():
    assert normalize_company("Amazon.com Services LLC") == "Amazon"


def test_title_cleanup_keeps_season():
    assert "2027" in normalize_title("Supply Chain Intern - Summer 2027")
    assert normalize_title("Supply Chain Intern – Summer 2027").startswith("Supply Chain Intern")


def test_location_city_state():
    parsed = parse_location("Seattle, WA")
    assert parsed["city"] == "Seattle"
    assert parsed["state"] == "WA"
    assert parsed["location"] == "Seattle, WA"
    assert parsed["country"] == "United States"


def test_location_remote_us():
    parsed = parse_location("Remote — United States")
    assert parsed["location"].startswith("Remote")
    assert parsed["country"] == "United States"


def test_location_iso3_country():
    parsed = parse_location("Shanghai, CHN")
    assert parsed["country"] == "China"
    parsed = parse_location("Sao Paulo, Sao Paulo, BRA")
    assert parsed["country"] == "Brazil"
    parsed = parse_location("Melbourne, Victoria, AUS")
    assert parsed["country"] == "Australia"


def test_us_job_filter():
    assert is_us_job(parse_location("Seattle, WA"), raw="Seattle, WA")
    assert is_us_job(parse_location("Remote"), raw="Remote", arrangement="Remote")
    assert is_us_job(parse_location("Indianapolis, IN"), raw="Indianapolis, IN")
    assert not is_us_job(parse_location("Shanghai, CHN"), raw="Shanghai, CHN")
    assert not is_us_job(parse_location("London, GBR"), raw="London, GBR")
    assert not is_us_job(parse_location("Toronto, Canada"), raw="Toronto, Canada")
    assert not is_us_job(parse_location("Remote, Canada"), raw="Remote, Canada")


def test_date_parsing():
    assert parse_iso_date("August 15, 2026") == "2026-08-15"
    assert parse_iso_date("2026-08-15T10:00:00-04:00") == "2026-08-15"
    assert parse_iso_date(None) is None


def test_url_tracking_stripped_but_path_kept():
    url = "https://jobs.acme.com/apply/123?utm_source=board&gh_jid=123"
    cleaned = normalize_application_url(url)
    assert "utm_source" not in cleaned
    assert "gh_jid=123" in cleaned
    assert canonicalize_url(url) == canonicalize_url("https://jobs.acme.com/apply/123?gh_jid=123")


def test_job_type_from_title():
    assert infer_job_type("Summer Supply Chain Intern") == "Summer Internship"
    assert infer_job_type("Operations Co-op") == "Co-op"
    assert infer_job_type("New Graduate Analyst") == "New Graduate"
    assert infer_job_type("Director of Operations") == "Unknown"
    assert infer_job_type("Internal Auditor") == "Unknown"


def test_stable_ids():
    first = make_job_id(
        "Amazon",
        source_job_id="12345",
        title="Supply Chain Intern",
        location="Seattle, WA",
        application_url="https://www.amazon.jobs/en/jobs/12345",
    )
    second = make_job_id(
        "Amazon",
        source_job_id="12345",
        title="Supply Chain Intern",
        location="Seattle, WA",
        application_url="https://www.amazon.jobs/en/jobs/12345?utm_source=x",
    )
    assert first == second == "amazon-12345"
