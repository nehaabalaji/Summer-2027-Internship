# Deployment

This project is designed to run as a GitHub repository. The README is the product.

## 1. Create the GitHub repository

Suggested name: `Supply-Chain-Internships`

Suggested description:

> Continuously updated internships and entry-level roles in Supply Chain, Operations, Product, Procurement, Logistics, and Analytics.

Suggested topics:

`internships` `supply-chain` `operations` `product-management` `jobs` `career` `students` `internship` `co-op` `business-analytics` `procurement` `logistics`

## 2. Enable GitHub Actions

1. Push the repository.
2. Open **Settings → Actions → General**.
3. Allow Actions and permit GitHub Actions to create pull requests / push commits.
4. Confirm **Workflow permissions** include **Read and write** so `update-jobs.yml` can commit listing updates.

No extra secrets are required. `GITHUB_TOKEN` is provided automatically.

## 3. First scheduled run

The `Update jobs` workflow runs every 6 hours and on **Run workflow**.

It will:

1. Run tests
2. Collect from enabled public sources
3. Normalize, classify, deduplicate, validate
4. Expire listings only after repeated confirmed absences
5. Regenerate README.md
6. Commit `chore: update internship listings` when files changed

## 4. Optional GitHub Pages

Do not make Pages the primary product. If you later add a frontend, serve
`data/jobs.json` as a static API. A placeholder lives in `web/`.

## 5. Renaming the project

Change `config/settings.yaml` (`project.slug`, `project.title`, `github_user`,
`github_repo`, `user_agent`) and regenerate the README.
