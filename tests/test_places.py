"""Regions, "worldwide" and plain "Remote", on location strings taken from live Ashby jobs (2026-10-08).

The failing run behind this file: a user searched remote software engineer jobs in Worldwide, Anywhere,
EMEA, Africa and Kenya and got none, while "Greece (Remote)" and a plain "Remote" job were open to them.

Run: python -m unittest discover -s tests -t .
"""
import unittest
from datetime import datetime, timezone

from src.inputs import parse_input
from src.rows import Filters, Place, classify_place, job_area

NOW = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)


def job(location, *others, country=None, other_countries=(), workplace='Remote'):
    addr = {'address': {'postalAddress': {'addressCountry': country}}} if country else {}
    return {'id': '1', 'title': 'Software Engineer', 'location': location, 'workplaceType': workplace,
            'publishedAt': NOW.isoformat(), 'isListed': True, **addr,
            'secondaryLocations': [{'location': o, **({'address': {'postalAddress': {'addressCountry': c}}} if c else {})}
                                   for o, c in zip(others, list(other_countries) + [None] * len(others))]}


def finds(place, j) -> bool:
    return Place(place).matches(job_area(j))


class TheFailingSearch(unittest.TestCase):
    def test_the_users_search_now_finds_the_open_jobs(self):
        raw = {'searchTerms': ['software engineer'], 'workType': ['remote'],
               'location': ['Worldwide', 'Anywhere', 'EMEA', 'Africa', 'Kenya']}
        f = Filters(parse_input(raw))
        self.assertTrue(f.passes(job('Greece (Remote)', country='Greece'), NOW))       # Infiterra
        self.assertTrue(f.passes(job('Remote'), NOW))                                   # Camunda: no address
        self.assertFalse(f.passes(job('Remote - Canada', country='Canada'), NOW))       # Marqeta
        self.assertFalse(f.passes(job('Remote (United States)', country='United States'), NOW))


class Regions(unittest.TestCase):
    def test_a_region_finds_its_countries_and_overlapping_regions(self):
        self.assertTrue(finds('EMEA', job('Greece (Remote)', country='Greece')))
        self.assertTrue(finds('EMEA', job('Remote - Europe')))
        self.assertTrue(finds('Europe', job('Remote – EMEA ')))
        self.assertTrue(finds('Kenya', job('Remote', 'EMEA')))
        self.assertTrue(finds('DACH', job('Remote - EU')))
        self.assertTrue(finds('LatAm', job('Bogota', country='Colombia')))
        self.assertTrue(finds('Africa', job('Cairo Office', country='Egypt')))
        self.assertTrue(finds('APAC', job('Remote - APAC ( Singapore )')))
        self.assertFalse(finds('Africa', job('Remote - Europe Only')))
        self.assertFalse(finds('EMEA', job('Remote (APAC)')))

    def test_one_shared_country_does_not_make_a_region_job(self):
        self.assertFalse(finds('Middle East', job('European Union')))                  # Cyprus is in both
        self.assertFalse(finds('North America', job('LatAm')))                         # Mexico is in both
        self.assertTrue(finds('Middle East', job('European Union', 'UAE')))

    def test_a_country_inside_brackets_narrows_the_region(self):
        self.assertTrue(finds('Canada', job('Americas (USA or Canada)')))
        self.assertFalse(finds('Brazil', job('Americas (USA or Canada)')))
        self.assertTrue(finds('Germany', job('Remote (Canada, UK, EU)')))
        self.assertTrue(finds('Canada', job('Remote (Canada, UK, EU)')))

    def test_a_region_word_inside_a_country_name_is_the_country(self):
        area = job_area(job('South Africa - JHB', country='South Africa'))
        self.assertEqual((area.countries, area.regions), ({'ZA'}, []))
        self.assertTrue(finds('Africa', job('South Africa - JHB', country='South Africa')))
        self.assertFalse(finds('Nigeria', job('South Africa - JHB', country='South Africa')))

    def test_the_us_state_georgia_is_not_the_country(self):
        atlanta = job('Atlanta, Georgia', country='United States', workplace='OnSite')
        self.assertFalse(finds('EMEA', atlanta))
        self.assertTrue(finds('Georgia', atlanta))                                    # still found by its words

    def test_typed_places_are_read_by_kind(self):
        self.assertEqual(classify_place('EU')[0], 'region')
        self.assertEqual(classify_place('Georgia')[0], 'country')
        self.assertEqual(classify_place('CA')[1], frozenset({'CA'}))
        self.assertEqual(classify_place('London')[0], 'text')
        self.assertEqual(len(classify_place('UK&I')[1]), 2)
        for text in ('Worldwide', 'Anywhere', 'global', 'Remote worldwide', 'any location'):
            self.assertEqual(classify_place(text)[0], 'world', text)


class Worldwide(unittest.TestCase):
    def test_marked_worldwide_or_just_remote_with_no_address(self):
        for location in ('Global', 'Worldwide', 'Remote (Global)', 'Remote – Anywhere', 'Remote(Anywhere in the world)'):
            self.assertTrue(finds('Worldwide', job(location)), location)
        self.assertTrue(finds('Worldwide', job('Remote ')))
        self.assertTrue(finds('Worldwide', job('Fully Remote')))

    def test_a_place_or_an_address_restricts_it(self):
        self.assertFalse(finds('Worldwide', job('Anywhere (USA)')))
        self.assertFalse(finds('Worldwide', job('Remote', country='United States')))
        self.assertFalse(finds('Worldwide', job('San Francisco', 'Remote', country='United States')))
        self.assertFalse(finds('Worldwide', job('McLean - 1660 International Dr (Tysons)', country='United States')))
        self.assertTrue(finds('United States', job('Anywhere (USA)')))

    def test_jobs_marked_worldwide_are_open_in_every_country(self):
        self.assertTrue(finds('Kenya', job('Remote (Global)')))
        self.assertTrue(finds('EMEA', job('Worldwide')))
        self.assertFalse(finds('Kenya', job('Remote')))                                # only "Worldwide" finds these
        self.assertFalse(finds('London', job('Worldwide')))                            # a city means that city


if __name__ == '__main__':
    unittest.main()
