# Changelog

## [1.1] - 2026-10-01

One keyword and Start is the whole job (owner rule): nothing is prefilled but the job count, and no input stops a run.

### Changed
- The form opens with no keyword and no date filter: type a job title and press Start for the 100 newest matches
  (`maxJobs` is the only prefilled field, at its default of 100). Empty boxes show an example as grey hint text.
- Plainer field names and help texts; the JSON key stays in brackets.
- Remote or onsite and Job type accept typed words next to the listed choices (`enumSuggestedValues`), so an API
  call with "Remote", "wfh" or "freelance" is read instead of refused by the platform.
- Nothing fails on input any more: unreadable companies, job links, work types or job types fall back to their
  defaults with a note; a negative job count means 100; a spending limit too low for one job ends the run at $0
  without an error.

### Added
- Ten published example tasks (`.actor/tasks.json`, published by `scripts/publish-tasks.mjs` in CI).

## [1.0] - 2026-10-01 (listing)

- Logo: the Ashby wordmark with JOBS on Ashby purple (option 6 in manager/rules/logos/ashby-jobs-search/).
- Description names the site:jobs.ashbyhq.com Google dork, so Store search finds the actor for it (the README body is not searched).

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
  reads as its keyword and board, board and job links in the search box, work types typed as a place
  ("Remote", "offline" is onsite), company names, periods such as 24h or 2 weeks. Unreadable entries are
  skipped with a plain note; a form with nothing readable fails at $0, and so does a spending limit too low
  for one row.
- Pay per event: `job` per row, `job-details` per row with details, no start fee.
