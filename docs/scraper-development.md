# Scraper development

Collectors sit behind a stable interface:

```python
class BaseScraper:
    name: str
    def fetch_jobs(self):
        ...
```

Each `fetch_jobs()` call must return `RawJob` records with:

- company
- title
- location (if the source provides one)
- application_url pointing at the **employer** page
- source name
- source job id when the ATS provides one

Normalization, classification, deduplication, validation, and README rendering
happen **after** scraping. Do not format Markdown inside a scraper.

## Allowed collection methods

- Public JSON APIs and career-board feeds (Greenhouse, Lever, Ashby, Workday CXS, SmartRecruiters, amazon.jobs search.json)
- Ordinary HTTP requests with the project User-Agent
- Timeouts, retries with backoff, and per-host rate limiting (already in `board/http.py`)

## Not allowed

- CAPTCHA / authentication / paywall bypass
- Circumventing anti-bot systems
- Fabricating jobs or application URLs
- Storing full copyrighted job descriptions

## Adding a custom source

1. Implement parsing against a **fixture** in `tests/fixtures/`.
2. Keep live HTTP in a thin `fetch_*` function.
3. Register the source in `config/sources.yaml`.
4. If the site cannot be reached appropriately, document it and leave the source disabled.

## Failure behavior

If a source fails, the pipeline logs the error, records it in
`data/scraper_status.json`, and **keeps existing jobs from that source**.

## Local cache

Successful JSON responses are cached under `.cache/` for local development.
The cache is gitignored. GitHub Actions starts with an empty cache.
