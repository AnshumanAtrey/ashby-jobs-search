"""
Ashby's two public sources, both read live at run time:

- The board page, https://jobs.ashbyhq.com/<board>: the page embeds `window.__appData`, with the company
  (name, website, demo flag) and a short list of every open job (title, location, work type, job type,
  pay summary). About 20 KB per board. No posting dates, so it is the first pass only.
- The public job posting API, https://api.ashbyhq.com/posting-api/job-board/<board>, the one Ashby
  documents for companies' own career pages: every listed job with its posting date, addresses, pay and
  description. About 13 KB per job, so it is fetched only for boards whose short list has a match.

A board page for a name nobody uses answers 200 with `organization: null`; the API answers 404.
"""
import asyncio
import json
from urllib.parse import quote

import httpx

BOARD_URL = 'https://jobs.ashbyhq.com/{}'
POSTINGS_URL = 'https://api.ashbyhq.com/posting-api/job-board/{}'
USER_AGENT = ('Mozilla/5.0 (compatible; ashby-jobs-search/1.0; '
              '+https://apify.com/anshumanatrey/ashby-jobs-search)')
RETRY_STATUS = {429, 500, 502, 503, 504}
BACKOFF_S = (1, 3, 7)
APP_DATA = 'window.__appData = '


class BoardError(Exception):
    """A board that could not be read after the retries (network or server trouble, not a missing board)."""


def client() -> httpx.AsyncClient:
    limits = httpx.Limits(max_connections=64, max_keepalive_connections=64)
    return httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=15.0), limits=limits, follow_redirects=True,
                             headers={'User-Agent': USER_AGENT, 'Accept-Encoding': 'gzip'})


def parse_board(html: str) -> dict | None:
    """Board page HTML -> {'org': {...}, 'postings': [...]}, or None when no company uses the name."""
    start = html.find(APP_DATA)
    if start < 0:
        return None
    try:
        data, _ = json.JSONDecoder().raw_decode(html, start + len(APP_DATA))
    except ValueError:
        return None
    org = data.get('organization')
    if not isinstance(org, dict):
        return None
    board = data.get('jobBoard') or {}
    website = (org.get('publicWebsite') or '').strip() or None
    if website and '://' not in website:
        website = f'https://{website}'          # Ashby keeps what the company typed: joinhomebase.com
    return {
        'org': {
            'name': (org.get('name') or '').strip() or None,
            'slug': org.get('hostedJobsPageSlug'),
            'website': website,
            'demo': bool(org.get('isDemoOrg')),
        },
        'postings': [p for p in board.get('jobPostings') or [] if isinstance(p, dict)],
    }


async def _get(http: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
    last = None
    for attempt in range(len(BACKOFF_S) + 1):
        try:
            response = await http.get(url, params=params)
            if response.status_code not in RETRY_STATUS:
                return response
            last = f'HTTP {response.status_code}'
        except httpx.HTTPError as exc:
            last = f'{type(exc).__name__}: {exc}'[:200]
        if attempt < len(BACKOFF_S):
            await asyncio.sleep(BACKOFF_S[attempt])
    raise BoardError(last or 'no answer')


async def fetch_board(http: httpx.AsyncClient, slug: str) -> dict | None:
    response = await _get(http, BOARD_URL.format(quote(slug, safe='')))
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise BoardError(f'HTTP {response.status_code}')
    return parse_board(response.text)


async def fetch_jobs(http: httpx.AsyncClient, slug: str) -> list[dict] | None:
    """Every listed job of a board with its date, addresses, pay and description; None for no board."""
    response = await _get(http, POSTINGS_URL.format(quote(slug, safe='')), {'includeCompensation': 'true'})
    if response.status_code == 404:
        return None
    if response.status_code != 200:
        raise BoardError(f'HTTP {response.status_code}')
    try:
        jobs = response.json().get('jobs')
    except ValueError as exc:
        raise BoardError('the job list was not JSON') from exc
    return [j for j in jobs or [] if isinstance(j, dict)]
