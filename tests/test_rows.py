"""Matching and rows, on jobs shaped like Ashby's posting API answer (ramp, 2026-09-30).

Run: python -m unittest discover -s tests -t .
"""
import unittest
from datetime import datetime, timedelta, timezone

from src.ashby import parse_board
from src.inputs import parse_input
from src.rows import Filters, Term, country_code, dedupe_key, index, job_places, job_row, salary, work_type

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)
RAMP = {'name': 'Ramp', 'slug': 'ramp', 'website': 'https://ramp.com'}


def job(**over) -> dict:
    base = {
        'id': '34413f8d-26bf-4bbc-8ade-eb309a0e2245', 'title': ' Security Engineer, Cloud',
        'department': 'Engineering', 'team': 'Backend', 'employmentType': 'FullTime',
        'location': 'New York, NY (HQ)',
        'secondaryLocations': [
            {'location': 'Remote (Canada)', 'address': {'postalAddress': {'addressCountry': 'Canada'}}},
            {'location': 'Miami, FL', 'address': {'postalAddress': {'addressRegion': 'Florida', 'addressCountry': 'USA',
                                                                    'addressLocality': 'Miami'}}}],
        'publishedAt': (NOW - timedelta(days=2)).isoformat(), 'isListed': True, 'isRemote': True,
        'workplaceType': 'Hybrid',
        'address': {'postalAddress': {'addressRegion': 'NY', 'addressCountry': 'USA', 'addressLocality': 'New York City'}},
        'jobUrl': 'https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245',
        'applyUrl': 'https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245/application',
        'descriptionHtml': '<p>We build finance automation with Python and Kubernetes.</p>',
        'descriptionPlain': 'We build finance automation with Python and Kubernetes.',
        'compensation': {
            'compensationTierSummary': '$211.4K – $290.6K • Offers Equity',
            'summaryComponents': [
                {'compensationType': 'EquityPercentage', 'interval': 'NONE', 'currencyCode': None, 'minValue': None, 'maxValue': None},
                {'compensationType': 'Salary', 'interval': '1 YEAR', 'currencyCode': 'USD', 'minValue': 211400, 'maxValue': 290600}]},
    }
    base.update(over)
    return base


def filters(**raw) -> Filters:
    return Filters(parse_input(raw))


class TitleWords(unittest.TestCase):
    def test_joined_and_split_words_match_each_other(self):
        for title in ('Senior Frontend Engineer', 'Front-End Engineer', 'Front End Developer'):
            for term in ('frontend', 'front end', 'front-end'):
                self.assertTrue(Term(term).in_title(index(title)), (term, title))

    def test_a_word_inside_another_word_does_not_match(self):
        self.assertFalse(Term('java').in_title(index('JavaScript Engineer')))
        self.assertTrue(Term('java').in_title(index('Java Engineer')))

    def test_plurals_and_signs(self):
        self.assertTrue(Term('engineers').in_title(index('Software Engineer')))
        self.assertTrue(Term('c++').in_title(index('C++ Developer')))
        self.assertFalse(Term('c++').in_title(index('C Developer')))

    def test_every_word_of_the_term_is_needed(self):
        self.assertTrue(Term('security engineer').in_title(index(' Security Engineer, Cloud')))
        self.assertFalse(Term('data engineer').in_title(index(' Security Engineer, Cloud')))


class Countries(unittest.TestCase):
    def test_names_and_codes(self):
        for text in ('United States', 'USA', 'US', 'u.s.a.'):
            self.assertEqual(country_code(text, True), 'US', text)
        self.assertEqual(country_code('UK', True), 'GB')
        self.assertEqual(country_code('India', False), 'IN')

    def test_a_state_in_free_text_is_not_a_country(self):
        self.assertIsNone(country_code('CA', False))
        self.assertEqual(country_code('CA', True), 'CA')

    def test_job_places_hold_every_country(self):
        texts, codes = job_places(job())
        self.assertEqual(codes, {'US', 'CA'})
        self.assertIn('Miami', texts)


class Filtering(unittest.TestCase):
    def test_title_place_work_type_and_date(self):
        self.assertTrue(filters(searchTerms=['security engineer'], location=['United States'],
                                workType=['hybrid'], postedWithin='7 days').passes(job(), NOW))
        self.assertTrue(filters(location=['Canada']).passes(job(), NOW))
        self.assertTrue(filters(location=['Miami']).passes(job(), NOW))
        self.assertFalse(filters(location=['Germany']).passes(job(), NOW))
        self.assertFalse(filters(workType=['remote']).passes(job(), NOW))
        self.assertFalse(filters(postedWithin='24 hours').passes(job(), NOW))

    def test_excluded_words_and_unlisted_jobs(self):
        self.assertFalse(filters(excludeTerms=['cloud']).passes(job(), NOW))
        self.assertFalse(filters().passes(job(isListed=False), NOW))

    def test_descriptions_only_when_asked(self):
        self.assertFalse(filters(searchTerms=['kubernetes']).passes(job(), NOW))
        self.assertTrue(filters(searchTerms=['kubernetes'], searchDescriptions=True).passes(job(), NOW))

    def test_first_pass_keeps_jobs_that_can_match(self):
        short = {'title': 'Security Engineer', 'locationName': 'New York', 'workplaceType': None,
                 'employmentType': 'FullTime', 'secondaryLocations': []}
        self.assertTrue(filters(searchTerms=['security'], workType=['remote']).maybe(short))
        self.assertFalse(filters(searchTerms=['designer']).maybe(short))
        self.assertFalse(filters(employmentType=['intern']).maybe(short))


class Rows(unittest.TestCase):
    def test_work_type_falls_back_to_the_location(self):
        self.assertEqual(work_type(job()), 'hybrid')
        self.assertEqual(work_type(job(workplaceType=None, isRemote=None, location='Remote (US)')), 'remote')
        self.assertIsNone(work_type(job(workplaceType=None, isRemote=None, secondaryLocations=[])))

    def test_salary_numbers(self):
        pay = salary(job())
        self.assertEqual((pay['salaryMin'], pay['salaryMax'], pay['salaryCurrency'], pay['salaryPeriod']),
                         (211400, 290600, 'USD', 'year'))
        self.assertTrue(pay['offersEquity'])
        self.assertIsNone(salary(job(compensation=None))['salary'])

    def test_link_row_and_details_row(self):
        row = job_row(RAMP, job(), '2026-09-30T12:00:00+00:00', details=False)
        self.assertEqual((row['title'], row['company'], row['workType'], row['employmentType'], row['status']),
                         ('Security Engineer, Cloud', 'Ramp', 'hybrid', 'full-time', 'open'))
        self.assertEqual(row['otherLocations'], ['Remote (Canada)', 'Miami, FL'])
        self.assertNotIn('description', row)
        full = job_row(RAMP, job(), '2026-09-30T12:00:00+00:00', details=True)
        self.assertEqual((full['city'], full['countryCode'], full['salaryPeriod']), ('New York City', 'US', 'year'))
        self.assertIn('Kubernetes', full['description'])

    def test_same_title_and_place_is_one_job(self):
        self.assertEqual(dedupe_key(job()), dedupe_key(job(id='other', title='Security  Engineer - Cloud')))
        self.assertNotEqual(dedupe_key(job()), dedupe_key(job(location='London')))


class BoardPage(unittest.TestCase):
    def test_reads_the_embedded_data(self):
        html = ('<script>window.__appData = {"organization": {"name": "Ramp ", "hostedJobsPageSlug": "ramp", '
                '"publicWebsite": "https://ramp.com", "isDemoOrg": false}, "jobBoard": {"jobPostings": '
                '[{"id": "1", "title": "Engineer"}]}};\n // more script</script>')
        board = parse_board(html)
        self.assertEqual((board['org']['name'], board['org']['slug'], len(board['postings'])), ('Ramp', 'ramp', 1))

    def test_unknown_board_has_no_company(self):
        self.assertIsNone(parse_board('<script>window.__appData = {"organization": null, "jobBoard": null};</script>'))


if __name__ == '__main__':
    unittest.main()
