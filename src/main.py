"""
Ashby Jobs Search - every open job on every company's Ashby board (jobs.ashbyhq.com), searched live at
run time by title, place, work type, job type and posting date, newest first.

- Companies: src/companies.tsv, every board found in the Wayback Machine index of jobs.ashbyhq.com, Hacker
  News hiring posts and public job lists, each checked live (scripts/refresh_companies.py). The
  companies input searches other boards too.
- Pass 1: every board page, read for its short job list (src/ashby.py). A board goes to pass 2 only
  when one of its jobs can match (Filters.maybe).
- Pass 2: the public posting API of those boards: posting dates, addresses, pay, descriptions. Jobs
  that pass every filter are kept once per title and place (the newest), then the newest maxJobs of
  all boards are delivered. Only that many are held in memory (a heap), descriptions compressed.
- Job links mode (jobUrls): each link is looked up on its board's live API: open, closed, or not found.
- Charging: one event per delivered row, "job" for a row without details and for a closed or not-found
  link, "job-details" for a row with details. The SDK delivers only the rows the spending limit can pay
  for. No start fee. No input stops a run: unreadable fields fall back to their defaults with a note.
- The status message can never fail the run: SDK 3.x raises on some run origins after storing it.
"""
import asyncio
import heapq
import itertools
import json
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

from apify import Actor

from . import ashby
from .inputs import Config, parse_input
from .rows import Filters, dedupe_key, job_row, link_row, parse_time

LINK_EVENT = 'job'                 # these two must equal the event keys of the pricing in .actor/store.json
DETAILS_EVENT = 'job-details'
BOARD_CONCURRENCY = 32             # pass 1; 24 in parallel read 7,566 boards with no 429 (2026-09-30)
JOBS_CONCURRENCY = 16              # pass 2 answers are ten times larger
RUN_SAFETY_MARGIN_S = 30           # stop reading boards this close to the run's time limit and deliver
PROGRESS_EVERY_S = 5
PUSH_CHUNK = 500
COMPANIES_FILE = Path(__file__).with_name('companies.tsv')
OLDEST = datetime.min.replace(tzinfo=timezone.utc)
STOP_REASONS = {
    'limit': 'your spending limit for this run was reached. Raise the limit to get the rest.',
    'time': 'the run was about to reach its time limit, so the boards read so far were used. '
            'Raise the run timeout to read every board.',
}


async def safe_status(message: str) -> None:
    """Set the run's status message without ever failing the run (see the module docstring)."""
    try:
        await Actor.set_status_message(message[:500])
    except Exception as exc:  # noqa: BLE001
        Actor.log.debug(f'status message stored but not confirmed by the SDK: {exc}')


def seconds_left_in_run() -> float | None:
    """Seconds until the platform stops this run, or None when not on the platform."""
    config = getattr(Actor, 'configuration', None) or getattr(Actor, 'config', None)
    timeout_at = getattr(config, 'timeout_at', None) if config else None
    if not timeout_at:
        return None
    return (timeout_at - datetime.now(timezone.utc)).total_seconds()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def plural(n: int, word: str) -> str:
    return f'{n:,} {word}' + ('' if n == 1 else 's')


def load_companies() -> tuple[list[tuple[str, str]], str | None]:
    """companies.tsv -> ([(board, name)], the date of the list)."""
    companies, updated = [], None
    for line in COMPANIES_FILE.read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            if 'updated' in line:
                updated = line.split('updated', 1)[1].strip().split(' ')[0].strip(',')
            continue
        slug, _, name = line.partition('\t')
        if slug.strip():
            companies.append((slug.strip(), name.strip()))
    return companies, updated


def name_index(companies: list[tuple[str, str]]) -> dict[str, str]:
    """Company names and board names, lower case and squeezed, -> board name."""
    names = {}
    for slug, name in companies:
        for key in (name.lower(), ''.join(ch for ch in name.lower() if ch.isalnum()), slug.lower()):
            if key:
                names.setdefault(key, slug)
    return names


class Delivery:
    """Pushes rows charged per event and notices the spending limit."""

    def __init__(self):
        self.cm = Actor.get_charging_manager()
        self.ppe = self.cm.get_pricing_info().is_pay_per_event
        self.rows = 0
        self.limit = False

    def can_pay(self, event: str) -> bool:
        if self.ppe and not self.limit:
            left = self.cm.calculate_max_event_charge_count_within_limit(event)
            self.limit = left is not None and left < 1
        return not self.limit

    async def push(self, rows: list[dict], event: str) -> int:
        """Returns how many rows were delivered: the SDK drops the rows the limit cannot pay for."""
        if not rows:
            return 0
        result = await Actor.push_data(rows, charged_event_name=event)
        done = result.charged_count if self.ppe else len(rows)
        if self.ppe and (result.event_charge_limit_reached or done < len(rows)):
            self.limit = True
        self.rows += done
        return done


class Run:
    def __init__(self, cfg: Config, companies: list[tuple[str, str]], updated: str | None, delivery: Delivery):
        self.cfg, self.companies, self.updated, self.delivery = cfg, companies, updated, delivery
        self.started = time.monotonic()
        self.checked_at = now_iso()
        self.stop: str | None = None
        self.phase = ''
        self.boards_total = self.boards_read = self.boards_matched = self.pass2_read = 0
        self.jobs_listed = self.matching = self.duplicates = self.demo = self.companies_matched = 0
        self.boards_missing: list[str] = []
        self.board_errors: list[dict] = []
        self.links = {'open': 0, 'closed': 0, 'notFound': 0, 'couldNotCheck': 0}
        self.mode = 'check' if cfg.job_urls else 'search'

    # ---------- shared helpers ----------

    def out_of_time(self) -> bool:
        left = seconds_left_in_run()
        if left is not None and left < RUN_SAFETY_MARGIN_S:
            self.stop = self.stop or 'time'
            return True
        return False

    def progress_line(self) -> str:
        if self.phase == 'boards':
            return (f'Pass 1 of 2: read {self.boards_read:,} of {self.boards_total:,} Ashby boards, '
                    f'{plural(self.boards_matched, "board")} with a job that can match.')
        if self.phase == 'jobs':
            return (f'Pass 2 of 2: read the full job lists of {self.pass2_read:,} of '
                    f'{self.boards_matched:,} boards, {plural(self.matching, "matching job")} so far.')
        if self.phase == 'links':
            done = sum(self.links.values())
            return f'Checked {done:,} of {len(self.cfg.job_urls):,} job links.'
        return 'Working.'

    async def progress_loop(self) -> None:
        while True:
            await asyncio.sleep(PROGRESS_EVERY_S)
            await safe_status(self.progress_line())

    async def run_all(self, coros) -> None:
        progress = asyncio.create_task(self.progress_loop())
        try:
            await asyncio.gather(*coros)
        finally:
            progress.cancel()

    def board_error(self, slug: str, exc: Exception) -> None:
        self.board_errors.append({'board': slug, 'error': str(exc)[:200]})

    # ---------- search ----------

    async def search(self) -> None:
        cfg = self.cfg
        filters = Filters(cfg)
        now = datetime.now(timezone.utc)
        boards = cfg.companies or [slug for slug, _ in self.companies]
        self.boards_total = len(boards)
        matched: list[dict] = []
        heap: list = []                     # (posted, order, org, job): the newest maxJobs so far
        kept: list = []                     # every match when maxJobs is empty
        texts: dict[str, bytes] = {}        # job id -> compressed description, with details on
        order = itertools.count()

        async with ashby.client() as http:
            sem = asyncio.Semaphore(BOARD_CONCURRENCY)

            async def first(slug: str) -> None:
                async with sem:
                    if self.out_of_time():
                        return
                    try:
                        board = await ashby.fetch_board(http, slug)
                    except ashby.BoardError as exc:
                        self.board_error(slug, exc)
                        return
                    finally:
                        self.boards_read += 1
                    if board is None:
                        self.boards_missing.append(slug)
                        return
                    org = board['org']
                    org['slug'] = org['slug'] or slug
                    if org['demo']:
                        self.demo += 1
                        return
                    self.jobs_listed += len(board['postings'])
                    if any(filters.maybe(p) for p in board['postings']):
                        matched.append(org)
                        self.boards_matched += 1

            self.phase = 'boards'
            await self.run_all([first(s) for s in boards])

            sem2 = asyncio.Semaphore(JOBS_CONCURRENCY)

            def keep(posted: datetime, org: dict, job: dict) -> None:
                if cfg.include_details:
                    texts[job['id']] = zlib.compress(json.dumps(
                        [job.get('descriptionPlain'), job.get('descriptionHtml')]).encode('utf-8'))
                job.pop('descriptionPlain', None)
                job.pop('descriptionHtml', None)
                item = (posted, next(order), org, job)
                if cfg.max_jobs is None:
                    kept.append(item)
                    return
                if cfg.max_jobs == 0:
                    return
                if len(heap) < cfg.max_jobs:
                    heapq.heappush(heap, item)
                    return
                dropped = heapq.heappushpop(heap, item)
                texts.pop(dropped[3]['id'], None)

            async def second(org: dict) -> None:
                async with sem2:
                    if self.out_of_time():
                        return
                    try:
                        jobs = await ashby.fetch_jobs(http, org['slug'])
                    except ashby.BoardError as exc:
                        self.board_error(org['slug'], exc)
                        return
                    finally:
                        self.pass2_read += 1
                    best: dict[tuple, tuple] = {}
                    for job in jobs or []:
                        if not job.get('id') or not filters.passes(job, now):
                            continue
                        posted = parse_time(job.get('publishedAt')) or OLDEST
                        key = dedupe_key(job)
                        if key in best:
                            self.duplicates += 1
                            if posted <= best[key][0]:
                                continue
                        best[key] = (posted, job)
                    self.matching += len(best)
                    self.companies_matched += 1 if best else 0
                    for posted, job in best.values():
                        keep(posted, org, job)

            self.phase = 'jobs'
            await self.run_all([second(o) for o in matched])

        chosen = sorted(kept if cfg.max_jobs is None else heap, key=lambda item: (item[0], item[1]), reverse=True)
        self.phase = 'saving'
        event = DETAILS_EVENT if cfg.include_details else LINK_EVENT
        for i in range(0, len(chosen), PUSH_CHUNK):
            if not self.delivery.can_pay(event):
                self.stop = 'limit'
                break
            rows = []
            for posted, _, org, job in chosen[i:i + PUSH_CHUNK]:
                if cfg.include_details:
                    blob = texts.pop(job['id'], None)
                    if blob:
                        job['descriptionPlain'], job['descriptionHtml'] = json.loads(zlib.decompress(blob))
                rows.append(job_row(org, job, self.checked_at, cfg.include_details))
            await self.delivery.push(rows, event)
            if self.delivery.limit:
                self.stop = 'limit'
                break

    # ---------- job links ----------

    async def check_links(self) -> None:
        cfg = self.cfg
        by_board: dict[str, tuple[str, list]] = {}
        for slug, job_id, url in cfg.job_urls:
            by_board.setdefault(slug.lower(), (slug, []))[1].append(job_id)
        found: dict[str, tuple] = {}     # job id -> (status, org, job)
        sem = asyncio.Semaphore(JOBS_CONCURRENCY)

        async with ashby.client() as http:
            async def one(slug: str, job_ids: list[str]) -> None:
                async with sem:
                    try:
                        board = await ashby.fetch_board(http, slug)
                        jobs = await ashby.fetch_jobs(http, slug) if board else None
                    except ashby.BoardError as exc:
                        self.board_error(slug, exc)
                        for job_id in job_ids:
                            found[job_id] = ('error', None, None)
                        return
                    if board is None:
                        self.boards_missing.append(slug)
                        for job_id in job_ids:
                            found[job_id] = ('not found', None, None)
                        return
                    org = board['org']
                    org['slug'] = org['slug'] or slug
                    listed = {str(j.get('id', '')).lower(): j for j in jobs or [] if j.get('isListed') is not False}
                    for job_id in job_ids:
                        job = listed.get(job_id)
                        found[job_id] = ('open', org, job) if job else ('closed', org, None)

            self.phase = 'links'
            await self.run_all([one(slug, ids) for slug, ids in by_board.values()])

        batch, batch_event = [], None
        for slug, job_id, url in cfg.job_urls:
            status, org, job = found.get(job_id, ('error', None, None))
            if status == 'error':
                self.links['couldNotCheck'] += 1
                continue
            self.links['notFound' if status == 'not found' else status] += 1
            if status == 'open':
                row, event = job_row(org, job, self.checked_at, cfg.include_details), \
                    (DETAILS_EVENT if cfg.include_details else LINK_EVENT)
            else:
                row, event = link_row(slug, job_id, url, status, self.checked_at, org), LINK_EVENT
            if batch and event != batch_event:
                if not await self.deliver(batch, batch_event):
                    return
                batch = []
            batch.append(row)
            batch_event = event
        if batch:
            await self.deliver(batch, batch_event)

    async def deliver(self, rows: list[dict], event: str) -> bool:
        if not self.delivery.can_pay(event):
            self.stop = 'limit'
            return False
        await self.delivery.push(rows, event)
        if self.delivery.limit:
            self.stop = 'limit'
            return False
        return True

    # ---------- summary ----------

    def ran(self) -> bool:
        if self.mode == 'check':
            return sum(self.links.values()) > self.links['couldNotCheck']
        return self.boards_read > len(self.board_errors)

    def message(self) -> str:
        cfg, seconds = self.cfg, round(time.monotonic() - self.started)
        if self.mode == 'check':
            links = self.links
            text = (f'Checked {plural(sum(links.values()) - links["couldNotCheck"], "job link")} in {seconds} s: '
                    f'{links["open"]:,} open, {links["closed"]:,} closed, {links["notFound"]:,} on no Ashby board.')
            if links['couldNotCheck']:
                text += f' {plural(links["couldNotCheck"], "link")} could not be checked (Ashby did not answer).'
        elif not self.ran():
            first = self.board_errors[0]['error'] if self.board_errors else 'no board could be read'
            text = f'No Ashby board could be read: {first}.'
        else:
            where = plural(self.boards_read, 'Ashby board')
            if self.delivery.rows:
                newest = ('' if cfg.max_jobs is None or self.matching <= self.delivery.rows
                          else f', saved the {self.delivery.rows:,} newest')
                text = (f'Found {plural(self.matching, "matching job")} at {plural(self.companies_matched, "company")} '
                        f'on {where}{newest} in {seconds} s.')
                if cfg.max_jobs is None or self.matching <= self.delivery.rows:
                    text = (f'Found and saved {plural(self.delivery.rows, "matching job")} at '
                            f'{plural(self.companies_matched, "company")} on {where} in {seconds} s.')
            elif self.matching and cfg.max_jobs == 0:
                text = f'Found {plural(self.matching, "matching job")} on {where} in {seconds} s (maxJobs is 0).'
            else:
                text = (f'No open job matched on {where} in {seconds} s. Try fewer words, another place '
                        f'or a longer period.')
        if self.stop:
            text += f' Stopped early: {STOP_REASONS[self.stop]}'
        if cfg.companies and self.boards_missing:
            text += f' No Ashby board for: {", ".join(self.boards_missing[:5])}.'
        if cfg.skipped:
            text += f' Skipped {plural(len(cfg.skipped), "entry")}: {cfg.skipped[0][1]}'
        return text.replace('entrys', 'entries').replace('companys', 'companies')

    def output(self, status: str) -> dict:
        cfg = self.cfg
        return {
            'status': status,
            'message': self.message(),
            'mode': self.mode,
            'jobsSaved': self.delivery.rows,
            'matchingJobs': self.matching if self.mode == 'search' else None,
            'boardsSearched': self.boards_total if self.mode == 'search' else None,
            'boardsRead': self.boards_read if self.mode == 'search' else None,
            'boardsWithAMatch': self.boards_matched if self.mode == 'search' else None,
            'companiesWithMatches': self.companies_matched if self.mode == 'search' else None,
            'jobsOnBoards': self.jobs_listed if self.mode == 'search' else None,
            'duplicatesLeftOut': self.duplicates,
            'links': self.links if self.mode == 'check' else None,
            'boardsNotFound': self.boards_missing[:100] if (cfg.companies or self.mode == 'check') else [],
            'boardsWithErrors': self.board_errors[:100],
            'notes': cfg.notes,
            'skipped': [{'input': text, 'reason': why} for text, why in cfg.skipped],
            'settings': {
                'searchTerms': cfg.search_terms, 'excludeTerms': cfg.exclude_terms, 'location': cfg.locations,
                'workType': cfg.work_types, 'employmentType': cfg.job_types,
                'postedWithinDays': cfg.posted_within_days, 'maxJobs': cfg.max_jobs,
                'includeDetails': cfg.include_details, 'searchDescriptions': cfg.search_descriptions,
                'companies': cfg.companies,
            },
            'companyList': {'boards': len(self.companies), 'updated': self.updated},
            'finishedAt': now_iso() if status != 'running' else None,
        }

    async def write_output(self, final: bool) -> None:
        status = ('partial' if self.stop else 'done') if self.ran() else 'failed'
        try:
            await Actor.set_value('OUTPUT', self.output(status if final else 'running'))
        except Exception as exc:  # noqa: BLE001
            Actor.log.warning(f'Could not write the OUTPUT record: {exc}')


async def main() -> None:
    async with Actor:
        raw = await Actor.get_input() or {}
        companies, updated = load_companies()
        cfg = parse_input(raw, name_index(companies))   # never raises: unreadable fields fall back with a note
        delivery = Delivery()
        Actor.log.info(
            f'Ashby Jobs Search: {"checking " + plural(len(cfg.job_urls), "job link") if cfg.job_urls else "searching"}'
            f' | terms={cfg.search_terms or "any"} exclude={cfg.exclude_terms or "none"} location={cfg.locations or "any"}'
            f' workType={cfg.work_types or "any"} employmentType={cfg.job_types or "any"}'
            f' postedWithinDays={cfg.posted_within_days or "any"} maxJobs={cfg.max_jobs if cfg.max_jobs is not None else "all"}'
            f' details={cfg.include_details} searchDescriptions={cfg.search_descriptions}'
            f' companies={len(cfg.companies) or f"all {len(companies):,}"} payPerEvent={delivery.ppe}')
        for note in cfg.notes:
            Actor.log.warning(note)
        for text, why in cfg.skipped:
            Actor.log.warning(f'Skipped "{text}": {why}')
        run = Run(cfg, companies, updated, delivery)
        await run.write_output(final=False)
        first_event = DETAILS_EVENT if cfg.include_details and not cfg.job_urls else LINK_EVENT
        if not delivery.can_pay(first_event):
            message = ('The maximum cost of this run is too low for one job, so nothing was searched and nothing '
                       'was charged. Raise the maximum cost per run and start again.')
            await Actor.set_value('OUTPUT', {'status': 'done', 'message': message, 'jobsSaved': 0})
            await safe_status(message)
            return
        if cfg.job_urls:
            await run.check_links()
        else:
            await run.search()
        message = run.message()
        Actor.log.info(message)
        await run.write_output(final=True)
        if run.ran():
            await safe_status(message)
        else:
            await Actor.fail(status_message=message[:500])


if __name__ == '__main__':
    asyncio.run(main())
