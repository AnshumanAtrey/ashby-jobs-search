"""
Rebuild src/companies.tsv: every company board on jobs.ashbyhq.com we can find, each checked live.

Sources (all free, no key):
- the boards already in src/companies.tsv, so a board stays until Ashby stops serving it;
- the Wayback Machine index of jobs.ashbyhq.com (the first part of every archived path);
- Hacker News comments that link jobs.ashbyhq.com (Algolia's HN search, 60-day windows since 2020);
- public job lists on GitHub that link Ashby boards (SimplifyJobs and others).

Each candidate is kept when its board page names a company that is not a demo board, under the board
name Ashby itself uses (hostedJobsPageSlug); one company is kept once. On 2026-09-30: 7,566 candidates,
3,814 boards, 3,478 hiring, 61,272 open jobs, about 2 minutes at 24 requests in parallel.

Run: python3 scripts/refresh_companies.py   (needs httpx; writes src/companies.tsv, prints a summary)
"""
import asyncio
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.ashby import BOARD_URL, USER_AGENT, parse_board  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / 'src' / 'companies.tsv'
LINK = re.compile(r'jobs\.ashbyhq\.com/([A-Za-z0-9][A-Za-z0-9._%~ &-]{0,99})', re.I)
GITHUB_LISTS = [
    'SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json',
    'SimplifyJobs/New-Grad-Positions/dev/README.md',
    'SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json',
    'SimplifyJobs/Summer2026-Internships/dev/README.md',
    'speedyapply/2026-SWE-College-Jobs/main/README.md',
    'vanshb03/Summer2026-Internships/dev/.github/scripts/listings.json',
]
PARALLEL = 24


def first_part(path: str) -> str | None:
    part = urllib.parse.unquote(path.strip('/').split('/')[0]).strip()
    return part if part and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._~ &-]{0,99}', part) else None


def wayback(http: httpx.Client) -> set[str]:
    found, key = set(), None
    while True:
        params = {'url': 'jobs.ashbyhq.com/', 'matchType': 'prefix', 'fl': 'original', 'collapse': 'urlkey',
                  'limit': '150000', 'showResumeKey': 'true'}
        if key:
            params['resumeKey'] = key
        body = http.get('https://web.archive.org/cdx/search/cdx', params=params, timeout=300).text
        rows, _, rest = body.rstrip('\n').partition('\n\n')
        for line in rows.splitlines():
            part = first_part(urllib.parse.urlparse(line.strip()).path)
            if part:
                found.add(part.lower())
        key = rest.strip() or None
        if not key or not rows:
            return found


def hacker_news(http: httpx.Client) -> set[str]:
    found, start, step = set(), 1577836800, 86400 * 60
    while start < time.time():
        for page in range(5):
            params = {'query': 'ashbyhq', 'tags': 'comment', 'hitsPerPage': 1000, 'page': page,
                      'numericFilters': f'created_at_i>{start},created_at_i<={start + step}'}
            data = http.get('https://hn.algolia.com/api/v1/search_by_date', params=params, timeout=60).json()
            for hit in data.get('hits', []):
                for m in LINK.finditer((hit.get('comment_text') or '').replace('&#x2F;', '/')):
                    part = first_part(m.group(1))
                    if part:
                        found.add(part.lower())
            if page >= data.get('nbPages', 1) - 1:
                break
        start += step
    return found


def github_lists(http: httpx.Client) -> set[str]:
    found = set()
    for path in GITHUB_LISTS:
        response = http.get(f'https://raw.githubusercontent.com/{path}', timeout=60)
        if response.status_code == 200:
            for m in LINK.finditer(response.text):
                part = first_part(m.group(1))
                if part:
                    found.add(part.lower())
    return found


def current() -> set[str]:
    if not OUT.exists():
        return set()
    return {line.split('\t', 1)[0].strip() for line in OUT.read_text(encoding='utf-8').splitlines()
            if line.strip() and not line.startswith('#')}


async def check(candidates: list[str]) -> dict[str, dict]:
    boards: dict[str, dict] = {}
    sem = asyncio.Semaphore(PARALLEL)
    headers = {'User-Agent': USER_AGENT, 'Accept-Encoding': 'gzip'}
    async with httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True) as http:
        async def one(slug: str) -> None:
            async with sem:
                for attempt in range(3):
                    try:
                        response = await http.get(BOARD_URL.format(urllib.parse.quote(slug, safe='')))
                        if response.status_code in (429, 500, 502, 503, 504):
                            await asyncio.sleep(3 * (attempt + 1))
                            continue
                        board = parse_board(response.text) if response.status_code == 200 else None
                        if board and not board['org']['demo']:
                            name = board['org']['slug'] or slug
                            boards.setdefault(name.lower(), {'slug': name, 'name': board['org']['name'] or name,
                                                             'jobs': len(board['postings'])})
                        return
                    except httpx.HTTPError:
                        await asyncio.sleep(2)
        await asyncio.gather(*(one(s) for s in candidates))
    return boards


def main() -> None:
    t0 = time.time()
    with httpx.Client(headers={'User-Agent': USER_AGENT}, follow_redirects=True) as http:
        sources = {'current list': current(), 'Wayback Machine': wayback(http), 'Hacker News': hacker_news(http),
                   'GitHub job lists': github_lists(http)}
    seen: dict[str, str] = {}
    for names in sources.values():
        for name in names:
            seen.setdefault(name.lower(), name)
    boards = asyncio.run(check(sorted(seen.values())))
    hiring = sum(1 for b in boards.values() if b['jobs'])
    jobs = sum(b['jobs'] for b in boards.values())
    day = datetime.now(timezone.utc).date().isoformat()
    lines = [f'# Ashby job boards, updated {day}, {len(boards):,} boards ({hiring:,} hiring, {jobs:,} open jobs that day).',
             '# Board name<TAB>company name. Built by scripts/refresh_companies.py from the Wayback Machine index of '
             'jobs.ashbyhq.com, Hacker News hiring posts and public job lists, each board checked live.']
    lines += [f'{b["slug"]}\t{b["name"]}' for b in sorted(boards.values(), key=lambda b: b['slug'].lower())]
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'candidates': {k: len(v) for k, v in sources.items()}, 'unique': len(seen),
                      'boards': len(boards), 'hiring': hiring, 'openJobs': jobs,
                      'seconds': round(time.time() - t0)}, indent=1))


if __name__ == '__main__':
    main()
