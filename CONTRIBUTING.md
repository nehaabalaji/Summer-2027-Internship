# Contributing

Thanks for helping keep this internship board accurate.

## Submit a job

The fastest way to add a missed listing is a GitHub Issue using the
**Submit a job** template.

Please provide the original employer application URL whenever possible.

Do not submit:

- affiliate or tracking redirects
- a LinkedIn post when the employer career page exists
- guessed or placeholder URLs

Maintainers (or a follow-up PR) should add the role to `data/jobs.json` or
`data/overrides.json` so scraper runs do not clobber the correction.

## Add a company / scraper

See [docs/adding-a-company.md](docs/adding-a-company.md) and
[docs/scraper-development.md](docs/scraper-development.md).

Rules:

- Use a public API or permitted career-board feed.
- Do not bypass CAPTCHA, login walls, or anti-bot systems.
- Cover parsers with fixture tests. Do not hit live sites in CI.
- If a site cannot be collected appropriately, document it and leave it disabled.

## Development setup

```bash
git clone <repo>
cd Supply-Chain-Internships

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pytest
python scripts/update_jobs.py --dry-run
python scripts/generate_readme.py
```

Python 3.11+ is required.

## Commands

| Command | Purpose |
| --- | --- |
| `pytest` | Unit tests |
| `python scripts/update_jobs.py --dry-run` | Collect and process without writing production files |
| `python scripts/update_jobs.py --source amazon` | Run one source |
| `python scripts/update_jobs.py --all` | Run every enabled source and refresh the README |
| `python scripts/generate_readme.py` | Rebuild README from `data/jobs.json` |
| `python scripts/validate_jobs.py` | Fail if production data is invalid |

## How README generation works

`scripts/generate_readme.py` reads `data/jobs.json` and replaces only the block
between `<!-- JOBS:START -->` and `<!-- JOBS:END -->`. Hand-written sections
outside those markers are left alone.

## Standards

- Type hints on new functions
- Deterministic classification (edit `config/classification_rules.yaml`)
- Stable IDs (`company + source job id` when available)
- No fabricated jobs
- Keep descriptions short; the employer page is the source of truth
