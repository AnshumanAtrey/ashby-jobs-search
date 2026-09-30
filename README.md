# Ashby Jobs Scraper & API - All Companies, Remote, Last 24 Hours

Ashby jobs scraper and API for every company on jobs.ashbyhq.com: type a job title and get the newest matching jobs from all 3,478 hiring companies on Ashby at once, with the company, locations, remote or onsite, job type, department, pay, posting date and the job and apply links. Filter by location, work type, job type and how recently the job was posted (last 24 hours, 7 days, 30 days). Turn on Full details for the description, salary numbers and address, or paste job links to check whether they are still open.

Use it as an Ashby job board scraper, a startup jobs feed, a remote jobs search or a hiring-signal source, with nothing to install: run it from the Apify Console, the Apify API, Python, JavaScript, n8n, Make or an AI agent through the Apify MCP server, and export JSON, CSV or Excel. It does what the Google dork site:jobs.ashbyhq.com does, for every board and without Google's limits. **$1.20 per 1,000 jobs** ($1.35 with full details). No start fee, no login, no API key, no proxy.

---

## What does it do?

Ashby is the applicant tracking system behind the job boards of OpenAI, Ramp, Notion, Linear, Snowflake and thousands of startups. Every company gets its own board at jobs.ashbyhq.com followed by the company's name, and Ashby has no search across companies. This actor is that search.

- **Every company at once**: the actor carries a list of 3,814 Ashby boards (3,478 hiring, 61,272 open jobs on 2026-09-30), found in the Wayback Machine index of jobs.ashbyhq.com, Hacker News hiring posts and public job lists, each one checked live. Name any other company in Only these companies and it is searched too.
- **Read live during your run**: each board is read from Ashby itself when you press Start, so every job returned is open at that moment. The newest jobs come first.
- **Filters that match how jobs are written**: title words (frontend also finds Front-End and Front End, java does not find JavaScript), places by city, state or country (US, USA and United States are the same), remote, hybrid or onsite, full-time, contract or intern, and posting date.
- **Two row sizes**: a job row with the links and the basics, or a row with full details (description as text and HTML, salary minimum and maximum, currency, period, equity, city, region, country).
- **Job link checker**: paste Ashby job links and each one comes back open (with its data), closed, or not found. Clean dead links out of a job board or a spreadsheet.

## How is it different from other Ashby job scrapers?

Most Ashby actors on the Store read only the companies you list. This one searches every company it knows, live, with no list to build.

Inclusion rule: every actor with Ashby in its title and 10 or more users in the last 30 days on 2026-09-30, ordered by users (data from the Apify Store API that day).

| Actor | Users (30 days) | Which companies it reads |
|---|---|---|
| **This actor** | new | **3,814 Ashby boards, each read live**, plus any you name |
| bovi/greenhouse-lever-ashby-job-scraper | 107 | the companies you list, or its preset lists |
| fantastic-jobs/ashby-jobs-api | 81 | its own jobs database |
| jobo.world/ashby-jobs-scraper-api | 27 | its own jobs database |
| webdata_labs/greenhouse-lever-ashby-jobs-scraper | 17 | the companies you list |
| viridian_layout_ea2/company-career-site-jobs | 15 | its curated list or yours |
| get_anything/ats-jobs-scraper | 13 | the companies you list |
| johnvc/ashby-job-board-scraper | 13 | the companies you list, or a discovery search |
| k1ra/ats-jobs-scraper | 12 | the companies you list |
| blackfalcondata/greenhouse-scraper | 12 | the boards you list, or its preset lists |
| scrapesage/multi-ats-job-scraper | 10 | the companies you list |
| pulsedata/career-page-jobs-scraper | 10 | the career pages you list |

The database actors (fantastic-jobs, jobo.world) answer from jobs they stored earlier; this actor asks Ashby during the run, so a job closed an hour ago is not in the results and a job posted a minute ago is.

## When should I use it?

- **Job seekers and job alerts**: new remote frontend jobs at startups, every morning, from the last 24 hours.
- **Job boards and aggregators**: a fresh Ashby feed for your niche (AI, crypto, climate, a country), and a daily dead-link check of the Ashby jobs you already list.
- **Recruiters and sales teams**: which companies are hiring for a role right now, with their websites, as hiring signals and leads.
- **Researchers and analysts**: salary ranges, remote shares and hiring trends across thousands of startups.

## How much does it cost to scrape Ashby jobs?

Pay per event: **$1.20 per 1,000 jobs** ($0.0012 a row), or **$1.35 per 1,000 with full details** ($0.00135 a row). A checked link that is closed or not found is one job row. No start fee, no monthly fee, platform usage included. A run that matches nothing, a skipped entry and a run that fails on its input cost $0.

| Run | Rows | Price | With full details |
|---|---|---|---|
| One job title and the defaults (the 100 newest matches) | 100 | $0.12 | $0.135 |
| software engineer, last 7 days, 20 jobs | 20 | $0.024 | $0.027 |
| 100 jobs | 100 | $0.12 | $0.135 |
| 1,000 jobs | 1,000 | $1.20 | $1.35 |
| Every open job on Ashby (about 60,000) | 60,000 | $72 | $81 |

Number of jobs caps every run, and a spending limit on the run caps it harder: the actor stops cleanly at the limit and every row you paid for is kept. Apify's free plan includes $5 of monthly credit, which covers about 4,100 job rows.

## How does the price compare with other Ashby job scrapers?

List price per 1,000 jobs on the Apify free plan on 2026-09-30, same inclusion rule as above. Where the price drops on paid Apify plans, the lowest paid-plan price is in brackets.

| Actor | Per 1,000 jobs |
|---|---|
| **This actor** | **$1.20, or $1.35 with full details** |
| bovi/greenhouse-lever-ashby-job-scraper | $1.50 ($1.43) |
| fantastic-jobs/ashby-jobs-api | $2.00 |
| jobo.world/ashby-jobs-scraper-api | $0.99 |
| webdata_labs/greenhouse-lever-ashby-jobs-scraper | $1.00 |
| viridian_layout_ea2/company-career-site-jobs | $1.51 |
| get_anything/ats-jobs-scraper | $1.50 |
| johnvc/ashby-job-board-scraper | $0.50, plus $0.20 per 1,000 descriptions |
| k1ra/ats-jobs-scraper | $2.00 |
| blackfalcondata/greenhouse-scraper | $0.95, plus $0.005 a run |
| scrapesage/multi-ats-job-scraper | $3.00 ($2.56) |
| pulsedata/career-page-jobs-scraper | $2.00 |

Where others are cheaper: jobo.world, webdata_labs, blackfalcondata and johnvc charge less per job. jobo.world answers from its database; the other three read only the companies you give them. This actor is cheaper than the most used Ashby actors (bovi, fantastic-jobs) and searches every company without a list.

## Which inputs does it take?

Nothing is required. Type one job title and press Start, and every other field uses its default: every place, every work type, any posting date, the 100 newest jobs. Press Start with the form empty for the 100 newest jobs on all of Ashby. No input stops a run: anything the actor cannot read falls back to the field's default, and the run summary says so.

| Field | Default | What it does |
|---|---|---|
| Job titles to find (`searchTerms`) | every job | One title or keyword per line. A job matches when its title has every word of a line. A pasted Google dork or jobs.ashbyhq.com link works too. |
| Where the job is (`location`) | anywhere | Cities, states or countries, one per line. US, USA and United States are the same. Remote typed here means remote jobs. |
| Remote or onsite (`workType`) | all | remote, hybrid, onsite, or several. Typed words such as wfh or office work too. |
| Posted in the last (`postedWithin`) | any time | 24 hours, 3 days, 7 days, 30 days, or your own period such as 48 hours or 2 weeks. |
| Number of jobs (`maxJobs`) | 100 | How many jobs to get, newest first. 0 gets every match. |
| Full details (`includeDetails`) | off | Adds the description (text and HTML), salary numbers, equity, city, region and country. |
| Leave out words (`excludeTerms`) | nothing | Words that leave a job out when its title has them, such as senior or manager. |
| Job type (`employmentType`) | every type | full-time, part-time, contract, intern, temporary, or several. |
| Match descriptions (`searchDescriptions`) | off | Also match keywords as a phrase in the description (python finds every job that asks for Python). |
| Only these companies (`companies`) | every company | Company names, board names or board links. Companies outside the actor's list are looked up anyway. |
| Job links to check (`jobUrls`) | none | Ashby job links to check instead of searching: open, closed or not found. |

The simplest input, one job title:

```json
{
  "searchTerms": ["software engineer"]
}
```

## What does the output look like?

One row per job, newest first. A row from the example input on 2026-09-30:

```json
{
  "title": "Full Stack Software Engineer, Growth (Hybrid)",
  "company": "Homebase",
  "location": "Toronto",
  "otherLocations": [],
  "workType": "hybrid",
  "employmentType": "full-time",
  "department": "Engineering",
  "team": "Engineering",
  "salary": "$175K - $205K - Offers Equity",
  "postedAt": "2026-09-30T17:12:16.713+00:00",
  "jobUrl": "https://jobs.ashbyhq.com/homebase/bedf5c72-448a-4801-a6ac-63ada13c5db6",
  "applyUrl": "https://jobs.ashbyhq.com/homebase/bedf5c72-448a-4801-a6ac-63ada13c5db6/application",
  "status": "open",
  "companySlug": "homebase",
  "companyWebsite": "https://joinhomebase.com",
  "jobId": "bedf5c72-448a-4801-a6ac-63ada13c5db6",
  "checkedAt": "2026-09-30T17:18:12+00:00"
}
```

With Full details on, the same row also has `description`, `descriptionHtml`, `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` (year, month, week, day or hour), `offersEquity`, `city`, `region`, `country` and `countryCode`. A checked link that is no longer open has `status` closed (or not found), its `jobUrl`, `jobId` and company.

The run summary is the OUTPUT record: boards read, boards and companies with a match, jobs matched and saved, duplicates left out, the checked links, every note about how the input was read, and the settings used.

## How fast is it?

Measured on Apify on 2026-09-30 (build 1.0.1) with the default settings (1024 MB of memory, 32 boards read at once):

- **A job title, last 7 days, 20 jobs** (every board): 103 seconds. The first pass reads the 3,814 board pages; the second reads the full job list only of the 1,389 boards whose titles could match. Peak memory 184 MB.
- **Every open job on Ashby** (an empty form, the worst case): 143 seconds for 59,641 jobs at 3,464 companies, 1,282 duplicate postings left out. Peak memory 254 MB.
- **A few named companies**: about a second.
- No board refused or failed in either run. CPU stayed near a quarter of a core, so more memory buys little speed.

## Common questions

### Can I just type one keyword and press Start?

Yes. Type a job title such as product designer and press Start: you get the 100 newest matching jobs from every Ashby company, from any place, any work type and any date. Add the other fields only to narrow the search.

### What happens if I type something the actor cannot read?

The run still goes ahead. A value it cannot read falls back to the field's default (a period such as soonish means any time, a job count such as lots means 100), and the run summary, the OUTPUT record, lists every note about how the input was read.

### Is this the same as the Google dork site:jobs.ashbyhq.com?

It is that search done at the source. Googling site:jobs.ashbyhq.com intext:frontend, with Tools set to Past 24 hours, shows only the pages Google has indexed, and indexed job links go stale: of the Greenhouse job links in a September 2026 web crawl, 30% were already closed two to four weeks later (checked on 2026-09-30). This actor reads every board from Ashby during the run, so every job it returns is open. Paste the dork into the job titles field and its keyword is used.

### Which companies are included?

3,814 Ashby boards on 2026-09-30, rebuilt regularly from the Wayback Machine index of jobs.ashbyhq.com, Hacker News hiring posts and public job lists. Any company can be added for one run in Only these companies, even if it is not on the list.

### How fresh are the jobs?

As fresh as Ashby: every board is read during your run. The first row of the example run was posted 6 minutes before the run finished.

### Are there dead links?

No. A job is returned only when it is on the company's board at run time. For links you already have, use Job links to check: each one comes back open, closed or not found.

### How do I get only remote jobs, or jobs in one country?

Pick remote in Remote or onsite, and type the country in Location (United States, Germany, India, UK). A job matches when any of its locations is in that country, remote locations such as Remote (US) included.

### How do I get new jobs every day?

Save the input as a task with Posted in the last set to 24 hours and schedule it daily in Apify. Each run returns only the last day's jobs.

### Can I get every job on Ashby?

Yes: leave the search empty and set Number of jobs to 0. About 60,000 rows, in under three minutes (143 seconds in the test above).

### Does it need a login, an API key or a proxy?

No. It reads Ashby's public job boards and Ashby's public job posting API, the same sources a visitor's browser uses.

### Can I call it from code or an AI agent?

Yes. Use the Apify API or the Python and JavaScript clients (the API tab shows ready code), n8n, Make and Zapier, or the Apify MCP server, where agents see every field by its JSON key.

### What may I use it for?

Job postings are published for the public to read. Use the data lawfully: job search, job boards that link to the original posting, hiring research and outreach within the rules that apply to you.

## Limitations

- Ashby only. Greenhouse, Lever, Workday and other applicant tracking systems are not read.
- Only companies on the list or named in the run are searched. A company that has never appeared in the sources above is missing until you name it.
- Places match by country and by the words of the place: London finds London, but Bangalore does not find Bengaluru, and Europe matches only locations that say Europe.
- Titles match by words, not by meaning: ML engineer does not find Machine Learning Engineer. Add both lines.
- Pay is what the company publishes; about 45% of Ashby jobs have it.

---

## About the maintainer (priority response within 1-2 hours)

Built and maintained by **Anshuman Atrey** ([@AnshumanAtrey](https://github.com/AnshumanAtrey)).

- Purple-team security researcher, 5x hackathon winner
- Co-founder of **Walrus Securitas** (AI cybersecurity SaaS) and **The Drone Syndicate** (autonomous defence drones)
- Author of the OSINT and data actor portfolio on Apify Store

### Custom feature requests shipped within 1-2 hours (priority)

If you need a field, a filter or an output format this actor does not have, the maintainer ships it directly into this actor, typically within 1-2 hours for priority requests during active hours and within 24 hours overnight.

**Fastest contact channels (ranked by response speed):**
1. **LinkedIn DM** -> [linkedin.com/in/anshumanatrey](https://linkedin.com/in/anshumanatrey), typically under 1 hour during active hours
2. **GitHub issue** on this actor's repo
3. **Apify Console** DM to `@anshumanatrey`
4. **Email** via [atrey.dev](https://atrey.dev)

---

## Sibling actors by the same maintainer

| Actor | Use case |
|---|---|
| [google-trends-api-scraper](https://apify.com/anshumanatrey/google-trends-api-scraper) | Google Trends interest over time, regions, related queries and Trending Now, no login |
| [linkedin-harvester](https://apify.com/anshumanatrey/linkedin-harvester) | Email -> best-match public LinkedIn profile URL + confidence score |
| [holehe-email-osint](https://apify.com/anshumanatrey/holehe-email-osint) | Email -> registered accounts across 120+ platforms |
| [theharvester-osint](https://apify.com/anshumanatrey/theharvester-osint) | Domain -> emails + subdomains + IPs from 54+ public sources |
| [facebook-ads-library-api](https://apify.com/anshumanatrey/facebook-ads-library-api) | Facebook/Meta Ad Library -> ads, landing pages, creatives, advertiser leads, scam checks (no login) |
| [telegram-channel-scraper](https://apify.com/anshumanatrey/telegram-channel-scraper) | Public Telegram channel -> posts, media links, inline buttons, reactions (no login) |

---

## Documentation

- Apify Store: https://apify.com/anshumanatrey/ashby-jobs-search
- GitHub repo: https://github.com/AnshumanAtrey/ashby-jobs-search
- Ashby's public job posting API: https://developers.ashbyhq.com/docs/public-job-posting-api
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Issues / feature requests: open an issue on the GitHub repo or DM LinkedIn for the fastest response
- License: MIT

## Last updated

2026-10-01 (version 1.1)
