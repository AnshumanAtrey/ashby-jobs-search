# Ashby Jobs Scraper & API - All Companies, Remote, Last 24 Hours

Ashby jobs scraper and API for every company on jobs.ashbyhq.com: type a job title and get the newest matching jobs from all 3,478 hiring companies on Ashby at once, with the company, locations, remote or onsite, job type, department, pay, posting date and the job and apply links. Filter by location, work type, job type and how recently the job was posted (last 24 hours, 7 days, 30 days). Turn on Full details for the description, salary numbers and address, or paste job links to check whether they are still open.

Use it as an Ashby jobs API, an Ashby job board scraper, a startup jobs feed, a remote jobs search or a hiring-signal source, for job boards, job seekers, recruiters, sales teams and AI agents, with nothing to install: run it from the Apify Console, the Apify API, Python, JavaScript, n8n, Make or an AI agent through the Apify MCP server, and export JSON, CSV or Excel. It reads the public job boards and Ashby's public job posting API, the pages any visitor sees, and does what the Google dork site:jobs.ashbyhq.com does, for every board and without Google's limits. **$1.20 per 1,000 jobs** ($1.35 with full details), so Apify's free $5 monthly credit covers 4,166 jobs. No start fee, no login, no API key, no proxy.

---

## What does it do?

It searches the job boards of every company on Ashby at once, live, and returns one row per open job, newest first. Ashby is the applicant tracking system behind the job boards of OpenAI, Ramp, Notion, Linear, Snowflake and thousands of startups. Every company gets its own board at jobs.ashbyhq.com followed by the company's name, and Ashby has no search across companies. This actor is that search.

- **Every company at once**: the actor carries a list of 3,814 Ashby boards (3,478 hiring, 61,272 open jobs on 2026-09-30), found in the Wayback Machine index of jobs.ashbyhq.com, Hacker News hiring posts and public job lists, each one checked live. Name any other company in Only these companies and it is searched too.
- **Read live during your run**: each board is read from Ashby itself when you press Start, so every job returned is open at that moment. The newest jobs come first.
- **Filters that match how jobs are written**: title words (frontend also finds Front-End and Front End, java does not find JavaScript), places by city, state, country or region (US, USA and United States are the same; EMEA, Europe, LatAm and APAC find their countries; Worldwide finds jobs open everywhere), remote, hybrid or onsite, full-time, contract or intern, and posting date.
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
- **AI agents and data teams**: a clean Ashby jobs feed through the Apify API or as an MCP tool, with every field named by its JSON key.

## How much does it cost to scrape Ashby jobs?

**$1.20 per 1,000 jobs** ($0.0012 a job), or **$1.35 per 1,000 with full details** ($0.00135 a job), pay per event. A checked link that is closed or not found is one job row. No start fee, no monthly fee, platform usage included. A run that matches nothing, a skipped entry and a spending limit too low for one job cost $0.

| Apify plan | Job | Job with details |
|---|---|---|
| Free and Starter | $0.0012 ($1.20 per 1,000) | $0.00135 ($1.35 per 1,000) |
| Scale, 10% less | $0.00108 ($1.08 per 1,000) | $0.001215 ($1.215 per 1,000) |
| Business and above, 20% less | $0.00096 ($0.96 per 1,000) | $0.00108 ($1.08 per 1,000) |

The "from $0.96 / 1,000 jobs" on the Store page is the Business price.

| Run (Free and Starter price) | Rows | Price | With full details |
|---|---|---|---|
| One job title and the defaults (the 100 newest matches) | 100 | $0.12 | $0.135 |
| software engineer, last 7 days, 20 jobs | 20 | $0.024 | $0.027 |
| 1,000 jobs | 1,000 | $1.20 | $1.35 |
| Every open job on Ashby (about 60,000) | 60,000 | $72 | $81 |

Number of jobs (`maxJobs`) caps every run, and a spending limit on the run caps it harder: the actor stops cleanly at the limit and every row you paid for is kept. Apify's free plan includes $5 of monthly credit: 4,166 jobs at $0.0012, or 3,703 with full details.

## How does the price compare with other Ashby job scrapers?

List price per 1,000 jobs on the Apify free plan on 2026-09-30, same inclusion rule as above; this actor's row is its current price, with the Store discounts it added on 2026-10-29. Where the price drops on paid Apify plans, the lowest paid-plan price is in brackets.

| Actor | Per 1,000 jobs |
|---|---|
| **This actor** | **$1.20 ($0.96), or $1.35 ($1.08) with full details** |
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
| Where the job is (`location`) | anywhere | Cities, states, countries or regions, one per line. US, USA and United States are the same. A region (EMEA, Europe, EU, LatAm, APAC, Africa, DACH, Nordics and more) finds jobs in its countries and jobs posted for it. Worldwide finds jobs marked worldwide or anywhere, and plain "Remote" jobs with no country. Remote typed here means remote jobs. |
| Remote or onsite (`workType`) | all | remote, hybrid, onsite, or several. Typed words such as wfh or office work too. |
| Posted in the last (`postedWithin`) | any time | 24 hours, 3 days, 7 days, 30 days, or your own period such as 48 hours or 2 weeks. |
| Number of jobs (`maxJobs`) | 100 | How many jobs to get, newest first. 0 gets every match. Same as maxItems in other actors, which this actor does not read. |
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

Every row has the first 17 fields below; Full details (`includeDetails`) adds the last 11. A checked link that is no longer open has `status` closed (or not found), its `jobUrl`, `jobId` and company.

| Field | What it holds |
|---|---|
| Job title (`title`) | The job title as the company wrote it on Ashby |
| Company name (`company`) | The company's name on its Ashby job board |
| Main location (`location`) | The job's main location as the company wrote it, such as New York, NY or Remote (US) |
| Other locations (`otherLocations`) | Every other location the job is open in |
| Remote or onsite (`workType`) | remote, hybrid or onsite; empty when Ashby has none |
| Job type (`employmentType`) | full-time, part-time, contract, intern or temporary, as the company set it |
| Hiring department (`department`) | The department the job is in |
| Hiring team (`team`) | The team the job is in |
| Pay summary (`salary`) | The pay range the company publishes, as Ashby shows it, often with equity; empty when it shows no pay |
| Posted on (`postedAt`) | When the job was published on Ashby, in UTC |
| Job link (`jobUrl`) | The job's page on the company's Ashby board |
| Apply link (`applyUrl`) | The page where a candidate applies |
| Still open? (`status`) | open for every search result; for a checked link open, closed or not found |
| Ashby board name (`companySlug`) | The board's name in jobs.ashbyhq.com links; put it in Only these companies to search that company alone |
| Company website (`companyWebsite`) | The website the company gives on its Ashby board |
| Job ID (`jobId`) | Ashby's ID of the job, the last part of the job link |
| Checked at (`checkedAt`) | When the run read the boards, in UTC |
| Job description (`description`) | Full details: the job description as plain text |
| Description as HTML (`descriptionHtml`) | Full details: the job description as the company formatted it, in HTML |
| Lowest pay (`salaryMin`) | Full details: the bottom of the published salary range, as a number |
| Highest pay (`salaryMax`) | Full details: the top of the published salary range, as a number |
| Pay currency (`salaryCurrency`) | Full details: the currency code of the salary range |
| Pay per (`salaryPeriod`) | Full details: year, month, week, day or hour |
| Offers equity? (`offersEquity`) | Full details: true when the published pay includes equity |
| Job city (`city`) | Full details: the city of the job's main address |
| State or region (`region`) | Full details: the state or region of the job's main address |
| Job country (`country`) | Full details: the country of the job's main address, as the company wrote it |
| Country code (`countryCode`) | Full details: the two-letter code of that country |

The run summary is the OUTPUT record: boards read, boards and companies with a match, jobs matched and saved, duplicates left out, the checked links, every note about how the input was read, and the settings used.

## How fast is it?

About two minutes to search all 3,814 boards. Measured on Apify with the default settings (1024 MB of memory, 32 boards read at once):

- **The example input** (software engineer, the 100 newest jobs), build 1.1.5 on 2026-10-29: 146 seconds. 4,694 jobs matched at 1,314 companies; the 100 newest were saved and 100 charged (run 6hcFeE2vcZZtjuWo5).
- **A job title, last 7 days, 20 jobs** (every board), build 1.0.1 on 2026-09-30: 103 seconds. The first pass reads the 3,814 board pages; the second reads the full job list only of the 1,389 boards whose titles could match. Peak memory 184 MB.
- **An empty form** (the full job list of every board read, the worst case): 127 seconds on build 1.1.5 on 2026-10-29 (run dgUNTjJsfqIGdXSKu) and 143 seconds on build 1.0.1 on 2026-09-30, about 60,000 matching jobs each time (59,938 and 59,641, after about 1,300 duplicate postings were left out), the 100 newest saved. Peak memory 254 MB on build 1.0.1.
- **A few named companies**: about a second.
- No board refused or failed in any of these runs. CPU stayed near a quarter of a core on build 1.0.1, so more memory buys little speed.

## Common questions

### Can I just type one keyword and press Start?

Yes. Type a job title such as product designer and press Start: you get the 100 newest matching jobs from every Ashby company, from any place, any work type and any date. Add the other fields only to narrow the search.

### Does it work on the free Apify plan?

Yes. The free plan's $5 monthly credit pays for 4,166 jobs at $1.20 per 1,000, or 3,703 with full details. There is no start fee, so all of it goes to jobs, and Number of jobs (`maxJobs`) caps each run at 100 by default ($0.12).

### What happens if I type something the actor cannot read?

The run still goes ahead. A value it cannot read falls back to the field's default (a period such as soonish means any time, a job count such as lots means 100), and the run summary, the OUTPUT record, lists every note about how the input was read.

### Is this the same as the Google dork site:jobs.ashbyhq.com?

It is that search done at the source. Googling site:jobs.ashbyhq.com intext:frontend, with Tools set to Past 24 hours, shows only the pages Google has indexed, and indexed job links go stale: of the Greenhouse job links in a September 2026 web crawl, 30% were already closed two to four weeks later (checked on 2026-09-30). This actor reads every board from Ashby during the run, so every job it returns is open. Paste the dork into the job titles field and its keyword is used.

### How is it different from Ashby's own job posting API?

Ashby's public job posting API (developers.ashbyhq.com) returns one company's board per call, and you need the board's name to call it; it needs no key and has no search across companies. This actor holds 3,814 board names, reads them all in one run, applies your filters, keeps one job per title and place on a board, and returns one table, newest first. For one company you already know, the API alone is enough; for every company at once, this actor is that search.

### Which companies are included?

3,814 Ashby boards, last rebuilt on 2026-09-30 from the Wayback Machine index of jobs.ashbyhq.com, Hacker News hiring posts and public job lists. Any company can be added for one run in Only these companies, even if it is not on the list.

### How do I search one company?

Type it in Only these companies (`companies`): the company name (OpenAI), its board name (openai) or its board link (https://jobs.ashbyhq.com/openai), one per line. Leave Job titles to find empty and set Number of jobs to 0 for every open job there. A few named companies take seconds, and a company that is not on the list is looked up anyway.

### How fresh are the jobs?

As fresh as Ashby: every board is read during your run. The first row of the example run was posted 6 minutes before the run finished.

### Are there dead links?

No. A job is returned only when it is on the company's board at run time. For links you already have, use Job links to check: each one comes back open, closed or not found.

### How do I check a list of job links?

Paste the Ashby job links into Job links to check (`jobUrls`), one per line; the actor then checks them instead of searching. Each link comes back as one row: open (with the job's data), closed (no longer on the board) or not found (no such Ashby board). Each row is one Job charge ($0.0012), or one Job with details ($0.00135) for an open job when Full details is on. A link the actor could not reach is counted in the run summary and not charged.

### How do I get only remote jobs, or jobs in one country?

Pick remote in Remote or onsite, and type the country in Location (United States, Germany, India, UK). A job matches when any of its locations is in that country, remote locations such as Remote (US) included, and also when it is posted for a region that holds the country (Kenya finds "Remote - EMEA") or marked worldwide. To find remote jobs you can take from anywhere, type Worldwide: it finds jobs marked worldwide, global or anywhere, and plain "Remote" jobs that name no country. Regions work too: EMEA finds "Greece (Remote)" and "Remote - Europe".

### How often should I run it?

Once a day suits most job feeds: save the input as a task with Posted in the last set to 24 hours and schedule it daily in Apify. Each run returns only the last day's jobs, and a run that finds nothing costs $0. A job board can check its saved Ashby links on the same schedule.

### Can I get every job on Ashby?

Yes: leave the search empty and set Number of jobs to 0, about 60,000 rows ($72). Reading every board took 127 to 143 seconds in the tests above, which saved the 100 newest; writing 60,000 rows to the dataset adds to that.

### Does it need a login, an API key or a proxy?

No. It reads Ashby's public job boards and Ashby's public job posting API, the same sources a visitor's browser uses.

### How do I call it from the API, Python, JavaScript, n8n or an AI agent?

With an Apify API token from Apify Console (Settings, API & Integrations). Each example searches for software engineer and returns the jobs.

The Apify API in one call, which waits for the run and returns the rows as JSON. This endpoint waits up to 300 seconds; the example input took 146, and the clients below wait for runs of any length.

```bash
curl -X POST "https://api.apify.com/v2/actors/anshumanatrey~ashby-jobs-search/run-sync-get-dataset-items" \
  -H "Authorization: Bearer <YOUR_APIFY_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"searchTerms": ["software engineer"]}'
```

Python, with `pip install apify-client` (version 3 or later):

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")
run = client.actor("anshumanatrey/ashby-jobs-search").call(run_input={"searchTerms": ["software engineer"]})
for job in client.dataset(run.default_dataset_id).iterate_items():
    print(job["title"], job["company"], job["location"], job["salary"], job["jobUrl"])
```

JavaScript, with `npm install apify-client`:

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('anshumanatrey/ashby-jobs-search').call({ searchTerms: ['software engineer'] });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
for (const job of items) console.log(job.title, job.company, job.location, job.salary, job.jobUrl);
```

n8n: add the Apify node (`@apify/n8n-nodes-apify`), choose Run an Actor and get dataset, pick `anshumanatrey/ashby-jobs-search` and paste the input JSON. Make and Zapier have Apify apps that do the same.

AI agents: add the Apify MCP server with this actor as a tool, `https://mcp.apify.com?tools=anshumanatrey/ashby-jobs-search`, and sign in with OAuth or send an `Authorization: Bearer <YOUR_APIFY_TOKEN>` header. The agent sees every input by its JSON key. The number of jobs is `maxJobs`, 100 by default: the actor has no `maxItems` field, and a test run through the MCP server on 2026-10-29 that sent `maxItems: 5` got the 100 newest data engineer jobs in 88 seconds (run 28CpyA9m1tau9GAaW).

### Is it legal to scrape Ashby jobs?

It reads job postings that companies publish for anyone to read, from Ashby's public job boards and public job posting API, with no login. Use the data lawfully: job search, job boards that link to the original posting, hiring research and outreach. You are responsible for how you use it, including the site's terms and the privacy laws that apply to you.

## Limitations

- Ashby only. Greenhouse, Lever, Workday and other applicant tracking systems are not read here: the sibling actors below search them.
- Only companies on the list or named in the run are searched. A company that has never appeared in the sources above, or joined Ashby after the list was rebuilt on 2026-09-30, is missing until you name it.
- Places match by country, by region and by the words of the place: London finds London, but Bangalore does not find Bengaluru (city spellings are matched as typed).
- Titles match by words, not by meaning: ML engineer does not find Machine Learning Engineer. Add both lines.
- Pay is what the company publishes; about 45% of Ashby jobs have it.

---

## About the maintainer (priority response within 1-2 hours)

Built and maintained by **Anshuman Atrey** ([@AnshumanAtrey](https://github.com/AnshumanAtrey)).

- Purple-team security researcher, 5x hackathon winner
- Co-founder of **Walrus Securitas** (AI cybersecurity SaaS) and **The Drone Syndicate** (autonomous defence drones)
- Author of the [OSINT and data actor portfolio on Apify Store](https://apify.com/anshumanatrey)

### Custom feature requests shipped within 1-2 hours (priority)

If you need a field, a filter or an output format this actor does not have, the maintainer ships it directly into this actor, typically within 1-2 hours for priority requests during active hours and within 24 hours overnight.

**Fastest contact channels (ranked by response speed):**
1. **LinkedIn DM** -> [linkedin.com/in/anshumanatrey](https://linkedin.com/in/anshumanatrey), typically under 1 hour during active hours
2. **GitHub issue** on this actor's repo
3. **Apify Console** DM to `@anshumanatrey`
4. **Email** via [atrey.dev](https://atrey.dev)

---

## Sibling actors by the same maintainer

| Actor | What it searches |
|---|---|
| [Cornerstone Jobs Scraper](https://apify.com/anshumanatrey/cornerstone-jobs-search) | Jobs from every company on Cornerstone (csod.com), searched live |
| [Workday Jobs Scraper](https://apify.com/anshumanatrey/workday-job-search) | Jobs from every company on Workday (myworkdayjobs.com), searched live |
| [Deel Jobs Scraper](https://apify.com/anshumanatrey/deel-jobs-search) | Jobs from every company on Deel ATS (jobs.deel.com), with pay |
| [Greenhouse Jobs Scraper](https://apify.com/anshumanatrey/greenhouse-jobs-search) | Jobs from every company on Greenhouse (boards.greenhouse.io), searched live |
| [SmartRecruiters Jobs Scraper](https://apify.com/anshumanatrey/smartrecruiters-jobs-search) | Jobs from 2,900+ companies on SmartRecruiters, searched live |
| [Workable Jobs Scraper](https://apify.com/anshumanatrey/workable-job-search) | Jobs from every company on Workable, in one search |
| [Lever Jobs Scraper](https://apify.com/anshumanatrey/lever-jobs-search) | Jobs from 2,300+ companies on Lever (jobs.lever.co), searched live |

---

## Documentation

- Apify Store: https://apify.com/anshumanatrey/ashby-jobs-search
- GitHub repo: https://github.com/AnshumanAtrey/ashby-jobs-search
- Ashby's public job posting API: https://developers.ashbyhq.com/docs/public-job-posting-api
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Issues / feature requests: open an issue on the GitHub repo or DM LinkedIn for the fastest response
- License: MIT

## Last updated

2026-11-03 (version 1.1)
