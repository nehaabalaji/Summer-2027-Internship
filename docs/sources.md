# Source limitations

Enabled sources are limited to public, unauthenticated job feeds.

| Company / source | Status | Why |
| --- | --- | --- |
| Amazon | Implemented and verified | Public `amazon.jobs/en/search.json` |
| DoorDash | Implemented and verified | Greenhouse token `doordashusa` |
| Instacart | Implemented and verified | Greenhouse public board API |
| Airbnb | Implemented and verified | Greenhouse public board API |
| Stripe | Implemented and verified | Greenhouse public board API |
| Lyft | Implemented and verified | Greenhouse public board API |
| HubSpot | Implemented and verified | Greenhouse token `hubspotjobs` |
| Databricks | Implemented and verified | Greenhouse public board API |
| Palantir | Implemented and verified | Lever public postings API |
| Wayfair | Disabled | Greenhouse token was not found |
| Workday companies (Walmart, Target, Nike, Tesla, Boeing, …) | Adapter ready, disabled | Need official tenant/shard/site from the careers URL |
| Microsoft | Disabled | Eightfold careers site, no public unauthenticated API |
| Google | Disabled | Previous careers JSON paths return 404 |
| Apple | Disabled | jobs.apple.com search is not a stable public feed |
| Consulting / logistics custom sites (Accenture, Deloitte, FedEx, DHL, Siemens, Costco) | Disabled | No verified public feed |

Greenhouse/Lever boards are collected successfully even when they currently have **zero** in-scope internships (for example HubSpot or Palantir software internships that are out of category). That is not a scraper failure.

When a source is disabled, do not invent listings for it. Contributors can still submit individual roles through the job-submission issue template.
