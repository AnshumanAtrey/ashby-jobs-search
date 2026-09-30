# Changelog

## [1.0] - 2026-09-30

First release: every company's Ashby job board searched live, in one run.

### Added
- A list of 3,814 Ashby boards (3,478 hiring, 61,272 open jobs on 2026-09-30) from the Wayback Machine
  index of jobs.ashbyhq.com, Hacker News hiring posts and public job lists, each checked live
  (`scripts/refresh_companies.py` rebuilds it). `companies` searches any other board too.
- Two passes per run: every board page for its short job list, then Ashby's public job posting API only for
  the boards whose titles can match (posting dates, addresses, pay, descriptions). Newest first; one job per
  title and place on a board; only `maxJobs` jobs held in memory.
- Filters: title words (joined and split words match, a word inside another does not), places by name or
  country code, remote, hybrid or onsite, job type, posting date, excluded words, and phrases in descriptions.
- Full details: description as text and HTML, salary minimum, maximum, currency and period, equity, city,
  region, country and country code.
- Job link checker (`jobUrls`): each link comes back open, closed or not found.
- Input read as people type it: commas split, a pasted Google dork (site:jobs.ashbyhq.com intext:frontend)
  reads as its keyword and board, board and job links in the search box, everyday words for work and job
  types ("offline" is onsite), "Remote" typed as a place, periods such as 24h or 2 weeks. Unreadable entries
  are skipped with a plain note; a form with nothing readable fails at $0.
- Pay per event: `job` per row, `job-details` per row with details, no start fee.
