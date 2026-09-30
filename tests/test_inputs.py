"""Input reading: defaults, what people paste, soft fixes and the plain error messages.

Run: python -m unittest discover -s tests -t .
"""
import unittest

from src.inputs import DEFAULT_MAX_JOBS, InputError, parse_input, read_company, read_job_url, read_search_term

NAMES = {'ramp': 'ramp', 'openai': 'openai', 'blackpoint cyber': 'Blackpoint Cyber', 'blackpointcyber': 'Blackpoint Cyber'}
JOB = 'https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245'


def parse(raw: dict):
    return parse_input(raw, NAMES)


class Defaults(unittest.TestCase):
    def test_empty_form_searches_everything(self):
        cfg = parse({})
        self.assertEqual((cfg.search_terms, cfg.locations, cfg.work_types, cfg.job_types), ([], [], [], []))
        self.assertEqual((cfg.posted_within_days, cfg.max_jobs, cfg.include_details), (None, DEFAULT_MAX_JOBS, False))
        self.assertEqual((cfg.companies, cfg.job_urls, cfg.notes, cfg.skipped), ([], [], [], []))

    def test_example_input(self):
        cfg = parse({'searchTerms': ['software engineer'], 'postedWithin': '7 days', 'maxJobs': 20})
        self.assertEqual(cfg.search_terms, ['software engineer'])
        self.assertEqual((cfg.posted_within_days, cfg.max_jobs), (7.0, 20))


class SearchTerms(unittest.TestCase):
    def test_commas_split_and_duplicates_go(self):
        self.assertEqual(parse({'searchTerms': 'frontend, Frontend; designer'}).search_terms, ['frontend', 'designer'])

    def test_google_dork_reads_as_the_keyword(self):
        term, note, board = read_search_term('site:jobs.ashbyhq.com intext:"frontend"')
        self.assertEqual((term, board), ('frontend', None))
        self.assertIn('Google dork', note)

    def test_dork_with_one_board_limits_the_company(self):
        cfg = parse({'searchTerms': ['site:jobs.ashbyhq.com/ramp intitle:engineer']})
        self.assertEqual((cfg.search_terms, cfg.companies), (['engineer'], ['ramp']))

    def test_dork_without_words_is_skipped_with_a_reason(self):
        cfg = parse({'searchTerms': ['site:jobs.ashbyhq.com']})
        self.assertEqual(cfg.search_terms, [])
        self.assertIn('no keyword', cfg.skipped[0][1])

    def test_board_link_in_the_search_box_searches_that_company(self):
        cfg = parse({'searchTerms': ['https://jobs.ashbyhq.com/openai', 'researcher']})
        self.assertEqual((cfg.companies, cfg.search_terms), (['openai'], ['researcher']))

    def test_job_link_in_the_search_box_is_checked(self):
        cfg = parse({'searchTerms': [JOB]})
        self.assertEqual(cfg.job_urls[0][:2], ('ramp', '34413f8d-26bf-4bbc-8ade-eb309a0e2245'))


class Places(unittest.TestCase):
    def test_remote_typed_as_a_place_becomes_the_work_type(self):
        cfg = parse({'location': 'Remote, United States'})
        self.assertEqual((cfg.locations, cfg.work_types), (['United States'], ['remote']))
        self.assertIn('remote work type', cfg.notes[0])

    def test_offline_means_onsite(self):
        cfg = parse({'workType': ['offline']})
        self.assertEqual(cfg.work_types, ['onsite'])

    def test_every_work_type_is_the_same_as_none(self):
        self.assertEqual(parse({'workType': ['remote', 'hybrid', 'onsite']}).work_types, [])

    def test_unknown_work_type_fails_before_charging(self):
        with self.assertRaises(InputError):
            parse({'workType': ['underwater']})

    def test_job_type_words(self):
        self.assertEqual(parse({'employmentType': 'internship, Full time'}).job_types, ['intern', 'full-time'])


class Periods(unittest.TestCase):
    def test_periods_people_type(self):
        cases = {'24 hours': 1.0, '24h': 1.0, 'today': 1.0, '48h': 2.0, '3 days': 3.0, '7 days': 7.0,
                 'last 7 days': 7.0, 'week': 7.0, '2 weeks': 14.0, 'month': 30.0, '30': 30.0, 3: 3.0}
        for text, days in cases.items():
            self.assertAlmostEqual(parse({'postedWithin': text}).posted_within_days, days, msg=str(text))

    def test_any_time(self):
        for text in (None, '', 'any time', 'Any', 0):
            self.assertIsNone(parse({'postedWithin': text}).posted_within_days, text)

    def test_unreadable_period_keeps_every_date_with_a_note(self):
        cfg = parse({'postedWithin': 'soonish'})
        self.assertIsNone(cfg.posted_within_days)
        self.assertIn('soonish', cfg.notes[0])


class Numbers(unittest.TestCase):
    def test_max_jobs(self):
        self.assertEqual(parse({'maxJobs': '250'}).max_jobs, 250)
        self.assertIsNone(parse({'maxJobs': 0}).max_jobs)
        self.assertIsNone(parse({'maxJobs': 'all'}).max_jobs)
        self.assertEqual(parse({'maxJobs': 'lots'}).max_jobs, DEFAULT_MAX_JOBS)


class Companies(unittest.TestCase):
    def test_board_name_link_and_company_name(self):
        self.assertEqual(read_company('https://jobs.ashbyhq.com/ramp/jobs', NAMES)[0], 'ramp')
        self.assertEqual(read_company('Blackpoint Cyber', NAMES)[0], 'Blackpoint Cyber')
        self.assertEqual(read_company('https://jobs.ashbyhq.com/Blackpoint%20Cyber', NAMES)[0], 'Blackpoint Cyber')

    def test_unknown_name_is_tried_as_typed(self):
        self.assertEqual(read_company('Some New Co', NAMES)[0], 'Some New Co')

    def test_other_sites_are_refused(self):
        slug, why = read_company('https://boards.greenhouse.io/airbnb', NAMES)
        self.assertIsNone(slug)
        self.assertIn('jobs.ashbyhq.com', why)

    def test_no_readable_company_fails(self):
        with self.assertRaises(InputError):
            parse({'companies': ['https://example.com/careers']})


class JobLinks(unittest.TestCase):
    def test_job_page_application_page_and_tracking(self):
        for url in (JOB, JOB + '/application', JOB + '?utm_source=x', 'jobs.ashbyhq.com/ramp/34413F8D-26BF-4BBC-8ADE-EB309A0E2245'):
            self.assertEqual(read_job_url(url)[0], ('ramp', '34413f8d-26bf-4bbc-8ade-eb309a0e2245'), url)

    def test_board_link_is_not_a_job_link(self):
        self.assertIsNone(read_job_url('https://jobs.ashbyhq.com/ramp')[0])

    def test_links_switch_the_run_to_checking(self):
        cfg = parse({'jobUrls': [JOB, JOB], 'searchTerms': ['engineer']})
        self.assertEqual(len(cfg.job_urls), 1)
        self.assertIn('does not search', cfg.notes[-1])

    def test_no_readable_link_fails(self):
        with self.assertRaises(InputError):
            parse({'jobUrls': ['https://example.com/job/1']})


if __name__ == '__main__':
    unittest.main()
