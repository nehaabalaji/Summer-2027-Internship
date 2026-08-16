import json

from scrapers.companies.amazon import parse_amazon_jobs
from scrapers.platforms.ashby import parse_ashby_jobs
from scrapers.platforms.greenhouse import parse_greenhouse_jobs
from scrapers.platforms.lever import parse_lever_jobs
from scrapers.platforms.workday import parse_workday_jobs
from tests.conftest import FIXTURES


def test_amazon_parser_extracts_official_url():
    payload = json.loads((FIXTURES / "amazon_search.json").read_text())
    jobs = parse_amazon_jobs(payload)
    intern = next(job for job in jobs if "Supply Chain" in job.title)
    assert intern.application_url.startswith("https://www.amazon.jobs/en/jobs/12345/")
    assert intern.source == "Amazon Careers"
    assert intern.source_job_id == "12345"


def test_greenhouse_parser_uses_absolute_url():
    payload = json.loads((FIXTURES / "greenhouse_jobs.json").read_text())
    jobs = parse_greenhouse_jobs(payload, company="ExampleCo", source_key="example", source_label="ExampleCo Careers")
    pm = next(job for job in jobs if "Product" in job.title)
    assert pm.application_url.startswith("https://boards.greenhouse.io/exampleco/jobs/111")
    assert "utm_" not in pm.application_url
    assert "gh_src" not in pm.application_url


def test_lever_parser_uses_hosted_url():
    payload = json.loads((FIXTURES / "lever_jobs.json").read_text())
    jobs = parse_lever_jobs(payload, company="ExampleCo", source_key="example")
    assert jobs[0].application_url.startswith("https://jobs.lever.co/exampleco/lev-1")
    assert jobs[0].work_arrangement == "Hybrid"


def test_ashby_parser_trims_title():
    payload = json.loads((FIXTURES / "ashby_jobs.json").read_text())
    jobs = parse_ashby_jobs(payload, company="ExampleCo", source_key="example")
    assert jobs[0].title == "Logistics Intern"
    assert "ashbyhq.com" in jobs[0].application_url


def test_workday_parser_builds_employer_url():
    payload = json.loads((FIXTURES / "workday_jobs.json").read_text())
    jobs = parse_workday_jobs(
        payload,
        company="ExampleCo",
        source_key="example",
        tenant="exampleco",
        shard="wd1",
        site="External",
    )
    assert jobs[0].application_url.startswith("https://exampleco.wd1.myworkdayjobs.com/External/job/")
    assert "Procurement" in jobs[0].title


def test_simplify_parser_keeps_active_employer_url():
    from scrapers.platforms.simplify_github import parse_simplify_listings

    payload = json.loads((FIXTURES / "simplify_listings.json").read_text())
    jobs = parse_simplify_listings(payload, source_key="simplify_summer", source_label="SimplifyJobs GitHub")
    assert len(jobs) == 1
    assert jobs[0].company == "Acme Logistics"
    assert jobs[0].title == "Supply Chain Intern"
    assert jobs[0].application_url.startswith("https://boards.greenhouse.io/acme/jobs/99")
    assert jobs[0].location == "Austin, TX"
