"""
Matching and output rows. Pure module: no Apify or network import, so the tests run offline.

Matching is by words, not by a list of job titles: a search term matches a title when every word of
the term is in it. Words are cut at anything that is not a letter or digit (C++ and C# keep their
sign), an s plural is folded, and two neighbouring words also count joined, so frontend, front end and
front-end match each other while java does not match JavaScript. Descriptions, when searched, must hold
the term as a phrase.

Places match by what they stand for (src/places.py). A country matches jobs in it and jobs posted for a
region that holds it ("Kenya" finds "Remote - EMEA"); a region matches jobs in any of its countries or
posted for an overlapping region ("EMEA" finds "Greece (Remote)" and "Remote - Europe"); "Worldwide"
matches jobs marked worldwide, global or anywhere, and jobs whose location is just "Remote" with no
country in their address. Jobs marked worldwide match every country and region too. A city, or anything
else, matches by its words inside a location. Country codes come from the address Ashby stores (where
codes such as US or GB are allowed) and from full country names inside the location text (where a
two-letter part such as CA is a state, not Canada, so only names count).
"""
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache

from . import places

WORD = re.compile(r'[^\W_]+[+#]*')
WORK_TYPE = {'Remote': 'remote', 'Hybrid': 'hybrid', 'OnSite': 'onsite'}
JOB_TYPE = {'FullTime': 'full-time', 'PartTime': 'part-time', 'Contract': 'contract', 'Intern': 'intern',
            'Temporary': 'temporary'}
PERIOD = {'1 YEAR': 'year', '1 MONTH': 'month', '1 WEEK': 'week', '1 DAY': 'day', '1 HOUR': 'hour'}
# Everyday country names that are not ISO names (pycountry knows the ISO ones: "United States",
# "Germany", "Viet Nam"), and the country codes people write in text.
COUNTRY_ALIASES = {
    'us': 'US', 'usa': 'US', 'u s': 'US', 'u s a': 'US', 'united states of america': 'US', 'america': 'US',
    'uk': 'GB', 'u k': 'GB', 'england': 'GB', 'scotland': 'GB', 'wales': 'GB', 'northern ireland': 'GB',
    'great britain': 'GB', 'britain': 'GB', 'uae': 'AE', 'emirates': 'AE', 'south korea': 'KR', 'korea': 'KR',
    'russia': 'RU', 'vietnam': 'VN', 'czech republic': 'CZ', 'turkey': 'TR', 'taiwan': 'TW', 'iran': 'IR',
    'syria': 'SY', 'laos': 'LA', 'bolivia': 'BO', 'venezuela': 'VE', 'tanzania': 'TZ', 'moldova': 'MD',
    'holland': 'NL', 'the netherlands': 'NL', 'ivory coast': 'CI', 'macedonia': 'MK', 'brunei': 'BN',
}


def words(text: str | None) -> list[str]:
    return WORD.findall((text or '').casefold())


def fold(word: str) -> str:
    """engineers -> engineer, sales -> sale; ss endings (business) and short words stay."""
    return word[:-1] if len(word) > 3 and word.endswith('s') and not word.endswith('ss') else word


def index(text: str | None) -> set[str]:
    """The words of a title, folded, plus every two neighbouring words joined (front end -> frontend)."""
    ws = words(text)
    out = {fold(w) for w in ws}
    out.update(fold(a + b) for a, b in zip(ws, ws[1:]))
    return out


class Term:
    def __init__(self, text: str):
        self.text = text
        raw = words(text)
        self.tokens = [fold(w) for w in raw]
        self.joined = fold(''.join(raw)) if len(raw) > 1 else None
        self.phrase = ' '.join(self.tokens)

    def in_title(self, idx: set[str]) -> bool:
        return bool(self.tokens) and (all(t in idx for t in self.tokens) or (self.joined in idx))

    def in_text(self, folded_text: str, idx: set[str]) -> bool:
        """folded_text: ' '.join of the folded words, padded with spaces."""
        return bool(self.tokens) and (f' {self.phrase} ' in folded_text or (self.joined is not None and self.joined in idx))


def terms(texts: list[str]) -> list[Term]:
    return [t for t in (Term(x) for x in texts) if t.tokens]


def folded_text(text: str | None) -> tuple[str, set[str]]:
    ws = words(text)
    return ' ' + ' '.join(fold(w) for w in ws) + ' ', {fold(w) for w in ws}


def _country_lookup():
    try:
        import pycountry
        return pycountry.countries
    except ImportError:          # the tests and the actor install it; without it only the aliases work
        return None


_COUNTRIES = _country_lookup()


@lru_cache(maxsize=16384)
def country_code(text: str | None, allow_codes: bool) -> str | None:
    """'United States', 'USA', 'Deutschland'? -> 'US', None. Two- and three-letter codes are read only
    when allow_codes is set (an address field), never from free text."""
    key = ' '.join(words(text))
    if not key:
        return None
    if key in COUNTRY_ALIASES and (allow_codes or len(key) > 3 or key in ('us', 'usa', 'uk', 'uae')):
        return COUNTRY_ALIASES[key]
    if _COUNTRIES is None:
        return None
    if len(key) <= 3 and not allow_codes:
        return None
    try:
        return _COUNTRIES.lookup(text.strip()).alpha_2
    except (LookupError, AttributeError):
        return None


def is_country(text: str) -> bool:
    return country_code(text, allow_codes=False) is not None


def classify_place(text: str) -> tuple[str, frozenset[str]]:
    """A typed place -> ('world' | 'region' | 'country' | 'text', its countries). A region name wins over
    a country code ("EU"); anything else is a city or a word to find in the location."""
    toks = places.tokens(text)
    if places.world_query(toks):
        return 'world', frozenset()
    region = places.region_query(toks)
    if region is not None:
        return 'region', region
    code = country_code(text, allow_codes=True)
    return ('country', frozenset({code})) if code else ('text', frozenset())


@dataclass
class Area:
    """Where a job can be done: its location texts, countries, the regions it is posted for, whether a
    location says worldwide (and names no place), and whether one is just "Remote" with no address country."""
    texts: list[str]
    countries: set[str]
    regions: list[frozenset[str]]
    worldwide: bool
    open_remote: bool


class Place:
    def __init__(self, text: str):
        self.text = text
        self.words = ' '.join(words(text))
        self.kind, self.countries = classify_place(text)

    def covers(self, region: frozenset[str]) -> bool:
        """A job posted for a region is for this place when the region lies inside it ("Europe" for EMEA)
        or holds at least half of it ("EU" for DACH, "EMEA" for Kenya). One shared country is not enough:
        "EU" is not a Middle East job because of Cyprus."""
        shared = len(region & self.countries)
        return shared > 0 and (shared == len(region) or 2 * shared >= len(self.countries))

    def matches(self, area: Area) -> bool:
        if self.kind == 'world':
            return area.worldwide or area.open_remote
        if self.kind in ('region', 'country') and (
                area.worldwide or area.countries & self.countries or any(self.covers(r) for r in area.regions)):
            return True
        return bool(self.words) and any(f' {self.words} ' in f' {" ".join(words(t))} ' for t in area.texts)


def _address(entry: dict | None) -> dict:
    return ((entry or {}).get('address') or {}).get('postalAddress') or {}


def _location_parts(text: str | None) -> list[str]:
    return [p.strip() for p in re.split(r'[,()/|;]|\s[-–—]\s', text or '') if p.strip()]


def _part_codes(part: str) -> set[str]:
    """A country named by a location part: "Ireland", or each side of "US or Canada" / "UK & Europe" (a
    country whose name holds "and", such as Trinidad and Tobago, is read whole first)."""
    code = country_code(part, allow_codes=False)
    if code:
        return {code}
    sides = re.split(r'\s+(?:or|and)\s+|\s*[&+]\s*', part)
    return {c for c in (country_code(s, allow_codes=False) for s in sides) if c} if len(sides) > 1 else set()


def job_places(job: dict) -> tuple[list[str], set[str]]:
    """Every location text of a job (primary, secondary, address parts) and every country code."""
    entries = [job] + list(job.get('secondaryLocations') or [])
    texts, codes = [], set()
    for entry in entries:
        name = entry.get('location') or entry.get('locationName')
        addr = _address(entry)
        for t in (name, addr.get('addressLocality'), addr.get('addressRegion'), addr.get('addressCountry')):
            if t and t not in texts:
                texts.append(t)
        address_code = country_code(addr.get('addressCountry'), allow_codes=True)
        if address_code:
            codes.add(address_code)
        for part in _location_parts(name):
            # "Atlanta, Georgia" with a US address is the state: the one country name that is also a US state
            codes.update(c for c in _part_codes(part) if not (c == 'GE' and address_code == 'US'))
    return texts, codes


def _entry_regions(name: str) -> list[frozenset[str]]:
    """The regions one location names. Countries in brackets after a region say which part of it the job
    means: "Americas (USA or Canada)" is the US and Canada, not all of the Americas; "Remote (Canada, UK,
    EU)" names a region inside the brackets and keeps it."""
    inside = ' '.join(re.findall(r'\(([^()]*)\)', name))
    outside = re.sub(r'\([^()]*\)', ' ', name)
    out_regions = places.regions_in(places.tokens(outside), is_country)
    in_regions = places.regions_in(places.tokens(inside), is_country)
    in_codes = set().union(*(_part_codes(p) for p in _location_parts(inside))) if inside.strip() else set()
    if out_regions and in_codes and not in_regions and all(any(c in r for r in out_regions) for c in in_codes):
        return []
    return out_regions + in_regions


def job_area(job: dict) -> Area:
    texts, codes = job_places(job)
    regions, worldwide, open_remote = [], False, False
    home = country_code(_address(job).get('addressCountry'), allow_codes=True)
    for entry in [job] + list(job.get('secondaryLocations') or []):
        name = entry.get('location') or entry.get('locationName')
        if not name or not name.strip():
            continue
        kind = places.entry_kind(places.tokens(name))
        if kind == 'world':
            worldwide = True
        elif kind == 'remote':
            # plain "Remote" is open everywhere only when no address says where: "San Francisco" with a US
            # address and a second location "Remote" is most likely remote in the US
            open_remote = open_remote or not (home or country_code(_address(entry).get('addressCountry'), allow_codes=True))
        else:
            regions += _entry_regions(name)
    return Area(texts, codes, regions, worldwide, open_remote)


def work_type(job: dict) -> str | None:
    kind = WORK_TYPE.get(job.get('workplaceType') or '')
    if kind:
        return kind
    if job.get('isRemote') is True:
        return 'remote'
    names = [job.get('location') or job.get('locationName')] + [
        s.get('location') or s.get('locationName') for s in job.get('secondaryLocations') or []]
    return 'remote' if any('remote' in words(n) or places.entry_kind(places.tokens(n)) == 'world'
                           for n in names if n) else None


def job_type(job: dict) -> str | None:
    return JOB_TYPE.get(job.get('employmentType') or '')


class Filters:
    """The configuration's filters, compiled once."""

    def __init__(self, cfg):
        self.terms = terms(cfg.search_terms)
        self.excludes = terms(cfg.exclude_terms)
        self.places = [Place(p) for p in cfg.locations]
        self.work_types = set(cfg.work_types)
        self.job_types = set(cfg.job_types)
        self.within_days = cfg.posted_within_days
        self.search_descriptions = cfg.search_descriptions

    def title_ok(self, title: str | None, description: str | None = None) -> bool:
        idx = index(title)
        if any(t.in_title(idx) for t in self.excludes):
            return False
        if not self.terms or any(t.in_title(idx) for t in self.terms):
            return True
        if self.search_descriptions and description:
            text, didx = folded_text(description)
            return any(t.in_text(text, didx) for t in self.terms)
        return False

    def maybe(self, posting: dict) -> bool:
        """First pass on a board page's short job list (no dates, no addresses, no descriptions): False
        only when the job cannot match. Places are checked in the second pass, where the country is."""
        idx = index(posting.get('title'))
        if any(t.in_title(idx) for t in self.excludes):
            return False
        if self.terms and not self.search_descriptions and not any(t.in_title(idx) for t in self.terms):
            return False
        if self.job_types and job_type(posting) not in self.job_types:
            return False
        kind = work_type(posting)
        return not (self.work_types and kind is not None and kind not in self.work_types)

    def passes(self, job: dict, now: datetime) -> bool:
        """Second pass on the full job from the posting API."""
        if job.get('isListed') is False:
            return False
        if not self.title_ok(job.get('title'), job.get('descriptionPlain')):
            return False
        if self.job_types and job_type(job) not in self.job_types:
            return False
        if self.work_types and work_type(job) not in self.work_types:
            return False
        if self.places:
            area = job_area(job)
            if not any(p.matches(area) for p in self.places):
                return False
        if self.within_days is not None:
            posted = parse_time(job.get('publishedAt'))
            if posted is None or (now - posted).total_seconds() > self.within_days * 86400:
                return False
        return True


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def salary(job: dict) -> dict:
    """The pay Ashby publishes: summary text, and the salary component's numbers when there is one."""
    comp = job.get('compensation') or {}
    components = list(comp.get('summaryComponents') or [])
    for tier in comp.get('compensationTiers') or []:
        components += tier.get('components') or []
    pay = next((c for c in components if c.get('compensationType') == 'Salary'), None) or {}
    summary = (comp.get('compensationTierSummary') or comp.get('scrapeableCompensationSalarySummary')
               or job.get('compensationTierSummary'))
    return {
        'salary': summary.strip() if isinstance(summary, str) and summary.strip() else None,
        'salaryMin': pay.get('minValue'),
        'salaryMax': pay.get('maxValue'),
        'salaryCurrency': pay.get('currencyCode'),
        'salaryPeriod': PERIOD.get(pay.get('interval') or ''),
        'offersEquity': (any(str(c.get('compensationType') or '').startswith('Equity') for c in components)
                         if components else None),
    }


def dedupe_key(job: dict) -> tuple:
    """Same title at the same place on one board: kept once (the newest)."""
    return (' '.join(fold(w) for w in words(job.get('title'))),
            ' '.join(words(job.get('location') or job.get('locationName'))))


def job_row(org: dict, job: dict, checked_at: str, details: bool) -> dict:
    """One output row. org: the board's name, board name and website. details adds the description,
    the salary numbers and the address."""
    title = (job.get('title') or '').strip()
    others = [s.get('location') for s in job.get('secondaryLocations') or [] if s.get('location')]
    pay = salary(job)
    row = {
        'title': title,
        'company': org.get('name'),
        'location': job.get('location'),
        'otherLocations': others,
        'workType': work_type(job),
        'employmentType': job_type(job),
        'department': job.get('department') or None,
        'team': job.get('team') or None,
        'salary': pay['salary'],
        'postedAt': job.get('publishedAt'),
        'jobUrl': job.get('jobUrl'),
        'applyUrl': job.get('applyUrl'),
        'status': 'open',
        'companySlug': org.get('slug'),
        'companyWebsite': org.get('website'),
        'jobId': job.get('id'),
        'checkedAt': checked_at,
    }
    if details:
        addr = _address(job)
        country = addr.get('addressCountry')
        row.update({
            'description': job.get('descriptionPlain'),
            'descriptionHtml': job.get('descriptionHtml'),
            'salaryMin': pay['salaryMin'],
            'salaryMax': pay['salaryMax'],
            'salaryCurrency': pay['salaryCurrency'],
            'salaryPeriod': pay['salaryPeriod'],
            'offersEquity': pay['offersEquity'],
            'city': addr.get('addressLocality'),
            'region': addr.get('addressRegion'),
            'country': country,
            'countryCode': country_code(country, allow_codes=True),
        })
    return row


def link_row(slug: str, job_id: str, url: str, status: str, checked_at: str, org: dict | None = None) -> dict:
    """A checked job link that is no longer open (closed) or whose company has no Ashby board (not found)."""
    return {
        'title': None, 'company': (org or {}).get('name'), 'location': None, 'otherLocations': [],
        'workType': None, 'employmentType': None, 'department': None, 'team': None, 'salary': None,
        'postedAt': None, 'jobUrl': url, 'applyUrl': None, 'status': status,
        'companySlug': (org or {}).get('slug') or slug, 'companyWebsite': (org or {}).get('website'),
        'jobId': job_id, 'checkedAt': checked_at,
    }
