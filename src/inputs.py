"""
What people type -> a clean run configuration (manager/rules/SEO.md section 11.5).

No field is required and no input stops a run (owner rule, 2026-10-01: type one keyword, press Start,
get the newest jobs). An empty form returns the newest jobs from every company. Accepted as typed:
several entries on one line split by commas, a pasted Google dork (site:jobs.ashbyhq.com intext:frontend
reads as the keyword frontend), board links instead of company names, work types and job types in
everyday words ("offline" is onsite, "internship" is intern), "remote" typed as a location, and periods
such as "24h", "2 weeks" or a number of days. Anything that cannot be read falls back to the field's
default, and the OUTPUT record and the log say what was read and how.

Pure module: no Apify or network import, so the tests run offline.
"""
import re
from dataclasses import dataclass, field
from urllib.parse import unquote, urlparse

DEFAULT_MAX_JOBS = 100
MAX_JOBS_CAP = 100_000             # our guard: more than every open Ashby job (61,272 on 2026-09-30)
SPLIT = re.compile(r'[,;\n\r\t]+')
ASHBY_HOST = 'jobs.ashbyhq.com'
UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
SLUG = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._~ &-]{0,99}$')    # board names can hold spaces: "Blackpoint Cyber"
DORK_OPERATOR = re.compile(r'\b(?:site|inurl|filetype|ext|before|after|cache|related):\S+', re.I)
DORK_TEXT = re.compile(r'\b(?:intext|intitle|allintext|allintitle):', re.I)

WORK_TYPES = ('remote', 'hybrid', 'onsite')
WORK_TYPE_ALIASES = {
    'remote': 'remote', 'fully remote': 'remote', 'remote only': 'remote', 'wfh': 'remote',
    'work from home': 'remote', 'anywhere': 'remote', 'distributed': 'remote',
    'hybrid': 'hybrid', 'flexible': 'hybrid',
    'onsite': 'onsite', 'on site': 'onsite', 'on-site': 'onsite', 'in office': 'onsite', 'in-office': 'onsite',
    'office': 'onsite', 'offline': 'onsite', 'in person': 'onsite', 'in-person': 'onsite',
}
JOB_TYPES = ('full-time', 'part-time', 'contract', 'intern', 'temporary')
JOB_TYPE_ALIASES = {
    'full time': 'full-time', 'fulltime': 'full-time', 'full-time': 'full-time', 'permanent': 'full-time',
    'part time': 'part-time', 'parttime': 'part-time', 'part-time': 'part-time',
    'contract': 'contract', 'contractor': 'contract', 'freelance': 'contract', 'freelancer': 'contract',
    'intern': 'intern', 'internship': 'intern', 'internships': 'intern', 'co-op': 'intern', 'coop': 'intern',
    'temporary': 'temporary', 'temp': 'temporary', 'seasonal': 'temporary',
}
PERIOD = re.compile(r'^(?:last|past)?\s*(\d+(?:\.\d+)?)?\s*(h|hr|hrs|hour|hours|d|day|days|w|wk|week|weeks|m|mo|month|months)?$')
PERIOD_DAYS = {'h': 1 / 24, 'hr': 1 / 24, 'hrs': 1 / 24, 'hour': 1 / 24, 'hours': 1 / 24, 'd': 1, 'day': 1,
               'days': 1, 'w': 7, 'wk': 7, 'week': 7, 'weeks': 7, 'm': 30, 'mo': 30, 'month': 30, 'months': 30}
ANY_TIME = {'', 'any', 'any time', 'anytime', 'all', 'all time', 'ever', 'none', '0'}
EVERY = {'any', 'all', 'every', 'both', 'either', 'any type', 'all types', 'no preference'}


@dataclass
class Config:
    search_terms: list[str] = field(default_factory=list)
    exclude_terms: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    work_types: list[str] = field(default_factory=list)       # empty: every work type
    job_types: list[str] = field(default_factory=list)        # empty: every job type
    posted_within_days: float | None = None                  # None: any time
    max_jobs: int | None = DEFAULT_MAX_JOBS                  # None: every match
    include_details: bool = False
    search_descriptions: bool = False
    companies: list[str] = field(default_factory=list)        # empty: every known company
    job_urls: list[tuple[str, str, str]] = field(default_factory=list)   # (board, job id, as typed)
    notes: list[str] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)


def _items(value) -> list[str]:
    """A list, or one string, -> the separate entries (commas, semicolons and new lines split)."""
    raw = value if isinstance(value, list) else [value] if isinstance(value, (str, int, float)) else []
    return [part.strip() for item in raw if isinstance(item, (str, int, float))
            for part in SPLIT.split(str(item)) if part.strip()]


def _clean(text: str) -> str:
    return text.strip().strip('"\'<>()[]{}').strip()


def read_search_term(token: str) -> tuple[str | None, str | None, str | None]:
    """One entry -> (search term, note, board). A pasted Google dork keeps only its words:
    'site:jobs.ashbyhq.com intext:"frontend"' reads as frontend, and a site: that names one board
    ('site:jobs.ashbyhq.com/ramp') also limits the search to that company."""
    text = _clean(token)
    if DORK_OPERATOR.search(text) or DORK_TEXT.search(text):
        board = None
        for site in re.findall(r'\bsite:(\S+)', text, re.I):
            parts = _board_path(site.strip('"\''))
            if parts and SLUG.match(parts[0]):
                board = parts[0]
        words = DORK_TEXT.sub(' ', DORK_OPERATOR.sub(' ', text)).replace('"', ' ').replace("'", ' ')
        words = ' '.join(w for w in words.split() if w.upper() not in ('OR', 'AND', '|'))
        where = f' on the {board} board' if board else ''
        if not words:
            if board:
                return None, f'Read the Google dork "{text}" as every job{where}.', board
            return None, f'"{text}" is a Google dork with no keyword in it, such as intext:frontend.', None
        return words, f'Read the Google dork "{text}" as the keyword "{words}"{where}.', board
    return (text, None, None) if text else (None, None, None)


def parse_terms(value, key: str, notes: list[str], skipped: list[tuple[str, str]],
                boards: list[str] | None = None) -> list[str]:
    """Search words -> terms. Boards named by a pasted dork are added to boards."""
    terms, seen = [], set()
    for token in _items(value):
        term, note, board = read_search_term(token)
        if board is not None and boards is not None and board.lower() not in (b.lower() for b in boards):
            boards.append(board)
        if term is None:
            if note and board is None:
                skipped.append((token, note))
            elif note:
                notes.append(note)
            continue
        if not re.search(r'[A-Za-z0-9]', term):
            skipped.append((token, f'"{term}" in {key} has no letters or digits to match.'))
            continue
        if note:
            notes.append(note)
        if term.lower() not in seen:
            seen.add(term.lower())
            terms.append(term)
    return terms


def route_links(value, notes: list[str]) -> tuple[list[str], list[str], list[str]]:
    """Main search box -> (words, job links, board links). A jobs.ashbyhq.com link pasted there is read
    for what it is: a job link is checked, a board link searches that company."""
    words, jobs, boards = [], [], []
    for token in _items(value):
        text = _clean(token)
        if ASHBY_HOST in text.lower() and not DORK_OPERATOR.search(text) and not DORK_TEXT.search(text):
            found, _ = read_job_url(text)
            if found:
                jobs.append(text)
                notes.append(f'Read {text} in searchTerms as a job link to check.')
                continue
            board, _ = read_company(text)
            if board:
                boards.append(board)
                notes.append(f'Read {text} in searchTerms as the {board} board.')
                continue
        words.append(token)
    return words, jobs, boards


def _alias(text: str, aliases: dict[str, str]) -> str | None:
    key = ' '.join(text.lower().replace('_', ' ').split())
    return aliases.get(key) or aliases.get(key.replace(' ', '')) or aliases.get(key.replace(' ', '-'))


def parse_choices(value, key: str, allowed: tuple[str, ...], aliases: dict[str, str], notes: list[str]) -> list[str]:
    """Work types or job types in everyday words -> the fixed values, empty for every one. Unknown words
    are dropped with a note; when none is known, every one is kept."""
    chosen, unknown = [], []
    for token in _items(value):
        if ' '.join(token.lower().split()) in EVERY:
            return []
        name = _alias(token, aliases)
        if name is None:
            unknown.append(token)
            continue
        if token.strip().lower() not in allowed:
            notes.append(f'Read "{token}" in {key} as {name}.')
        if name not in chosen:
            chosen.append(name)
    if unknown and chosen:
        notes.append(f'{key} has no option {", ".join(unknown)}, so it was left out.')
    if unknown and not chosen:
        notes.append(f'{key} has no option {", ".join(unknown)}, so every one is kept. The options are '
                     f'{", ".join(allowed)}.')
    return chosen if len(chosen) < len(allowed) else []


def parse_locations(value, work_types: list[str], notes: list[str]) -> tuple[list[str], list[str]]:
    """Places -> (places, work types). "Remote" typed as a place asks for remote jobs, so it moves to
    the work type (a place next to it still filters, as in "Remote, United States")."""
    places, moved = [], list(work_types)
    for token in _items(value):
        text = _clean(token)
        kind = _alias(text, WORK_TYPE_ALIASES)
        if kind:
            if kind not in moved:
                moved.append(kind)
            notes.append(f'Read "{text}" in location as the {kind} work type.')
            continue
        if text and text.lower() not in (p.lower() for p in places):
            places.append(text)
    if len(moved) == len(WORK_TYPES):
        moved = []
    return places, moved


def parse_period(value, notes: list[str]) -> float | None:
    """'24 hours', '24h', '7 days', '2 weeks', 'month', 3, 'any time' -> days, or None for any time."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else None
    text = ' '.join(str(value).strip().lower().replace('_', ' ').split())
    if text in ANY_TIME:
        return None
    if text in ('today', '24 hours', 'day', 'past day', 'last day'):
        return 1.0
    m = PERIOD.match(text)
    if m and (m.group(1) or m.group(2)):
        number = float(m.group(1)) if m.group(1) else 1.0
        days = number * PERIOD_DAYS[m.group(2) or 'd']
        if days > 0:
            return days
    notes.append(f'Could not read "{value}" as a period such as 24 hours, 7 days or 30 days, so any posting '
                 f'date is kept.')
    return None


def parse_max_jobs(value, notes: list[str]) -> int | None:
    """Missing -> 100. Empty, 0 or "all" -> every match. A number -> that many, newest first."""
    if value is None:
        return DEFAULT_MAX_JOBS
    if str(value).strip().lower() in ('', 'all', '0', 'every', 'unlimited'):
        return None
    try:
        n = int(float(str(value).strip().replace(',', '')))
    except ValueError:
        notes.append(f'Could not read maxJobs "{value}" as a number, so it is {DEFAULT_MAX_JOBS}.')
        return DEFAULT_MAX_JOBS
    if n < 0:
        notes.append(f'maxJobs {n} is below 0, so it is {DEFAULT_MAX_JOBS}.')
        return DEFAULT_MAX_JOBS
    if n > MAX_JOBS_CAP:
        notes.append(f'maxJobs {n:,} is above {MAX_JOBS_CAP:,}, so every match is returned.')
        return None
    return n


def parse_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().lower() in ('true', 'yes', 'on', '1'):
        return True
    if isinstance(value, str) and value.strip().lower() in ('false', 'no', 'off', '0'):
        return False
    return default


def _board_path(text: str) -> list[str] | None:
    """A jobs.ashbyhq.com link -> its path parts, or None when it is not one."""
    link = text if re.match(r'^[a-z][a-z0-9+.-]*://', text, re.I) else f'https://{text}'
    parsed = urlparse(link)
    if (parsed.hostname or '').lower() != ASHBY_HOST:
        return None
    return [unquote(p) for p in parsed.path.split('/') if p]


def read_company(token: str, names: dict[str, str] | None = None) -> tuple[str | None, str | None]:
    """One entry -> (board name, note). Accepts a board name (ramp), a board link
    (https://jobs.ashbyhq.com/ramp) or a company name we know (Ramp)."""
    text = _clean(token)
    parts = _board_path(text) if ASHBY_HOST in text.lower() else None
    if parts is not None:
        if parts and SLUG.match(parts[0]):
            return parts[0], None
        return None, f'"{text}" is an Ashby link with no company in it. Paste a link such as https://jobs.ashbyhq.com/ramp.'
    if re.match(r'^[a-z][a-z0-9+.-]*://', text, re.I) or '/' in text:
        return None, (f'"{text}" is not a jobs.ashbyhq.com link. Type the company name, or paste its board link '
                      f'such as https://jobs.ashbyhq.com/ramp.')
    if names:
        slug = names.get(text.lower()) or names.get(re.sub(r'[^a-z0-9]', '', text.lower()))
        if slug:
            return slug, (None if slug.lower() == text.lower() else f'Read the company "{text}" as the board {slug}.')
    name = ' '.join(text.split())
    if SLUG.match(name):
        return name, None          # Ashby reads board names in any case, spaces included
    return None, f'"{text}" is not a company name or board link.'


def parse_companies(value, names, notes, skipped) -> list[str]:
    companies, seen = [], set()
    for token in _items(value):
        slug, note = read_company(token, names)
        if slug is None:
            skipped.append((token, note))
            continue
        if note:
            notes.append(note)
        if slug.lower() not in seen:
            seen.add(slug.lower())
            companies.append(slug)
    return companies


def read_job_url(token: str) -> tuple[tuple[str, str] | None, str | None]:
    """A job link -> ((board, job id), None), or (None, reason). Accepts the job page, its /application
    page and links with tracking parameters."""
    text = _clean(token)
    parts = _board_path(text) if ASHBY_HOST in text.lower() else None
    if parts is None:
        return None, (f'"{text}" is not a jobs.ashbyhq.com job link. Paste links such as '
                      f'https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245.')
    if len(parts) >= 2 and SLUG.match(parts[0]) and UUID.match(parts[1]):
        return (parts[0], parts[1].lower()), None
    return None, f'"{text}" is an Ashby link without a job in it. Paste the link of one job.'


def parse_job_urls(value, skipped) -> list[tuple[str, str, str]]:
    urls, seen = [], set()
    for token in _items(value):
        found, why = read_job_url(token)
        if found is None:
            skipped.append((token, why))
            continue
        if found[1] not in seen:
            seen.add(found[1])
            urls.append((found[0], found[1], _clean(token)))
    return urls


def parse_input(raw: dict | None, company_names: dict[str, str] | None = None) -> Config:
    raw = raw or {}
    notes: list[str] = []
    skipped: list[tuple[str, str]] = []
    words, pasted_jobs, pasted_boards = route_links(raw.get('searchTerms'), notes)
    job_urls = parse_job_urls(_items(raw.get('jobUrls')) + pasted_jobs, skipped)
    if _items(raw.get('jobUrls')) and not job_urls:
        notes.append('None of the job links could be read, so the run searched instead. ' + skipped[0][1])
    work_types = parse_choices(raw.get('workType'), 'workType', WORK_TYPES, WORK_TYPE_ALIASES, notes)
    locations, work_types = parse_locations(raw.get('location'), work_types, notes)
    companies = parse_companies(_items(raw.get('companies')) + pasted_boards, company_names, notes, skipped)
    if _items(raw.get('companies')) and not companies:
        notes.append('None of the companies could be read, so every company was searched. ' + skipped[-1][1])
    search_terms = parse_terms(words, 'searchTerms', notes, skipped, companies)
    cfg = Config(
        search_terms=search_terms,
        exclude_terms=parse_terms(raw.get('excludeTerms'), 'excludeTerms', notes, skipped),
        locations=locations,
        work_types=work_types,
        job_types=parse_choices(raw.get('employmentType'), 'employmentType', JOB_TYPES, JOB_TYPE_ALIASES, notes),
        posted_within_days=parse_period(raw.get('postedWithin'), notes),
        max_jobs=parse_max_jobs(raw.get('maxJobs'), notes),
        include_details=parse_bool(raw.get('includeDetails'), False),
        search_descriptions=parse_bool(raw.get('searchDescriptions'), False),
        companies=companies,
        job_urls=job_urls,
        notes=notes,
        skipped=skipped,
    )
    if cfg.job_urls and (cfg.search_terms or cfg.locations or cfg.companies):
        cfg.notes.append('Job links were given, so the run checks those links and does not search. '
                         'Run again without job links to search.')
    if cfg.search_descriptions and not cfg.search_terms:
        cfg.search_descriptions = False
    return cfg
