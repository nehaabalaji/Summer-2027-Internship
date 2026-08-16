# Adding a company

The collector registry is configuration-first. You usually do **not** need to change Python.

## 1. Confirm a public feed exists

Only add a source when one of these is true:

- The employer publishes a Greenhouse, Lever, Ashby, SmartRecruiters, or Workday career board with a public JSON feed.
- The employer has a documented public jobs API (like `amazon.jobs/en/search.json`).

Do not add a source that requires logging in, solving a CAPTCHA, or bypassing bot protection.

## 2. Add the company registry entry

Edit `config/companies.yaml`:

```yaml
NewCo:
  display_name: NewCo
  category_focus:
    - Supply Chain
  source: newco
  enabled: true
```

## 3. Add the source

Edit `config/sources.yaml`:

### Greenhouse

```yaml
- id: newco
  company: NewCo
  source: newco
  platform: greenhouse
  board_token: newco
  enabled: true
  career_url: https://boards.greenhouse.io/newco
```

The token is the slug in `boards.greenhouse.io/{token}`.

### Lever

```yaml
- id: newco
  company: NewCo
  source: newco
  platform: lever
  board_token: newco
  enabled: true
  career_url: https://jobs.lever.co/newco
```

### Workday

Copy tenant, shard, and site from the official careers URL
`https://{tenant}.{shard}.myworkdayjobs.com/{site}`:

```yaml
- id: newco
  company: NewCo
  source: newco
  platform: workday
  tenant: newco
  shard: wd1
  site: External
  enabled: true
```

Do not guess Workday values. A wrong combination 404s.

## 4. Optional company module

If you want a named module for `--source newco`, add `scrapers/companies/newco.py`
using `ConfiguredCompanyScraper`. This is optional; the registry can build a
generic scraper from YAML alone.

## 5. Verify

```bash
python scripts/update_jobs.py --source newco --dry-run
pytest
```
