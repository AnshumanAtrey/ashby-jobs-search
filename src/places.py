"""
Regions and "worldwide", for places as people type them and as companies write them on Ashby.

A region stands for a set of countries: EMEA, Europe, the EU, LatAm, APAC, Africa, DACH, the Nordics and
the rest of the groupings below. "Worldwide" (also global, anywhere, international) is its own kind of
place. Read on 8,498 live jobs from 553 boards (2026-10-08): a region word sits in about 1 location in 30
("LatAm", "Remote - EMEA", "Americas (USA or Canada)"), plain "Remote" in 1 in 20, and "Worldwide",
"Global" or "Anywhere" in 1 in 400.

Regions come from the UN M49 standard (unstats.un.org/unsd/methodology/m49), taken on 2026-10-08 from
github.com/lukes/ISO-3166-Countries-with-Regional-Codes; M49 leaves out Taiwan, added here to Eastern Asia.
The business groupings job posts use (EMEA, APAC, the EU, LatAm) are built from those regions.

Pure module: no Apify or network import.
"""
import re

TOKEN = re.compile(r'[^\W_]+')
SKIP = {'and', 'the'}          # "Central & South America" and "UK&I" read like the names below

_UN = {
    'AFRICA': ('AO BF BI BJ BW CD CF CG CI CM CV DJ DZ EG EH ER ET GA GH GM GN GQ GW IO KE KM LR LS LY MA MG ML '
               'MR MU MW MZ NA NE NG RE RW SC SD SH SL SN SO SS ST SZ TD TF TG TN TZ UG YT ZA ZM ZW'),
    'AMERICAS': ('AG AI AR AW BB BL BM BO BQ BR BS BV BZ CA CL CO CR CU CW DM DO EC FK GD GF GL GP GS GT GY HN HT '
                 'JM KN KY LC MF MQ MS MX NI PA PE PM PR PY SR SV SX TC TT US UY VC VE VG VI'),
    'ASIA': ('AE AF AM AZ BD BH BN BT CN CY GE HK ID IL IN IQ IR JO JP KG KH KP KR KW KZ LA LB LK MM MN MO MV '
             'MY NP OM PH PK PS QA SA SG SY TH TJ TL TM TR TW UZ VN YE'),
    'EUROPE': ('AD AL AT AX BA BE BG BY CH CZ DE DK EE ES FI FO FR GB GG GI GR HR HU IE IM IS IT JE LI LT LU LV '
               'MC MD ME MK MT NL NO PL PT RO RS RU SE SI SJ SK SM UA VA'),
    'OCEANIA': 'AS AU CC CK CX FJ FM GU HM KI MH MP NC NF NR NU NZ PF PG PN PW SB TK TO TV UM VU WF WS',
    'NORTHERN_AFRICA': 'DZ EG EH LY MA SD TN',
    'SUB_SAHARAN_AFRICA': ('AO BF BI BJ BW CD CF CG CI CM CV DJ ER ET GA GH GM GN GQ GW IO KE KM LR LS MG ML MR MU MW '
                           'MZ NA NE NG RE RW SC SH SL SN SO SS ST SZ TD TF TG TZ UG YT ZA ZM ZW'),
    'EASTERN_AFRICA': 'BI DJ ER ET IO KE KM MG MU MW MZ RE RW SC SO SS TF TZ UG YT ZM ZW',
    'MIDDLE_AFRICA': 'AO CD CF CG CM GA GQ ST TD',
    'SOUTHERN_AFRICA': 'BW LS NA SZ ZA',
    'WESTERN_AFRICA': 'BF BJ CI CV GH GM GN GW LR ML MR NE NG SH SL SN TG',
    'LATIN_AMERICA': ('AG AI AR AW BB BL BO BQ BR BS BV BZ CL CO CR CU CW DM DO EC FK GD GF GP GS GT GY HN HT JM KN '
                      'KY LC MF MQ MS MX NI PA PE PR PY SR SV SX TC TT UY VC VE VG VI'),
    'NORTHERN_AMERICA': 'BM CA GL PM US',
    'CARIBBEAN': 'AG AI AW BB BL BQ BS CU CW DM DO GD GP HT JM KN KY LC MF MQ MS PR SX TC TT VC VG VI',
    'CENTRAL_AMERICA': 'BZ CR GT HN MX NI PA SV',
    'SOUTH_AMERICA': 'AR BO BR BV CL CO EC FK GF GS GY PE PY SR UY VE',
    'CENTRAL_ASIA': 'KG KZ TJ TM UZ',
    'EASTERN_ASIA': 'CN HK JP KP KR MN MO TW',
    'SOUTH_EASTERN_ASIA': 'BN ID KH LA MM MY PH SG TH TL VN',
    'SOUTHERN_ASIA': 'AF BD BT IN IR LK MV NP PK',
    'WESTERN_ASIA': 'AE AM AZ BH CY GE IL IQ JO KW LB OM PS QA SA SY TR YE',
    'EASTERN_EUROPE': 'BG BY CZ HU MD PL RO RU SK UA',
    'NORTHERN_EUROPE': 'AX DK EE FI FO GB GG IE IM IS JE LT LV NO SE SJ',
    'SOUTHERN_EUROPE': 'AD AL BA ES GI GR HR IT ME MK MT PT RS SI SM VA',
    'WESTERN_EUROPE': 'AT BE CH DE FR LI LU MC NL',
}
UN = {name: frozenset(codes.split()) for name, codes in _UN.items()}
EU = frozenset('AT BE BG CY CZ DE DK EE ES FI FR GR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK'.split())
MIDDLE_EAST = (UN['WESTERN_ASIA'] - {'AM', 'AZ', 'GE'}) | {'EG'}
BALTICS = frozenset({'EE', 'LV', 'LT'})
REGIONS: dict[str, frozenset[str]] = {}      # a name, as key() reads it -> its countries


def key(text: str) -> str:
    """'Central & South America' -> 'central south america', the form REGIONS is keyed by."""
    return ' '.join(t for t in TOKEN.findall((text or '').casefold()) if t not in SKIP)


def _region(codes, *names: str) -> None:
    for name in names:
        REGIONS[key(name)] = frozenset(codes)


_region(UN['EUROPE'] | UN['AFRICA'] | UN['WESTERN_ASIA'], 'EMEA', 'Europe, Middle East and Africa')
_region(UN['EUROPE'], 'Europe', 'European')
_region(EU, 'EU', 'European Union')
_region(EU | {'IS', 'LI', 'NO'}, 'EEA', 'European Economic Area')
_region(UN['WESTERN_EUROPE'], 'Western Europe')
_region(UN['EASTERN_EUROPE'], 'Eastern Europe')
_region(UN['NORTHERN_EUROPE'], 'Northern Europe')
_region(UN['SOUTHERN_EUROPE'], 'Southern Europe')
_region({'AT', 'CH', 'CZ', 'DE', 'HU', 'LI', 'PL', 'SI', 'SK'}, 'Central Europe')
_region(UN['EASTERN_EUROPE'] | BALTICS | {'AL', 'BA', 'HR', 'ME', 'MK', 'RS', 'SI'}, 'CEE', 'Central and Eastern Europe')
_region({'DE', 'AT', 'CH'}, 'DACH')
_region({'DK', 'FI', 'IS', 'NO', 'SE', 'FO', 'AX', 'GL'}, 'Nordics', 'Nordic', 'Nordic countries')
_region({'DK', 'NO', 'SE'}, 'Scandinavia')
_region({'BE', 'NL', 'LU'}, 'Benelux')
_region(BALTICS, 'Baltics', 'Baltic states')
_region({'GB', 'IE'}, 'UK&I', 'UKI', 'UK and Ireland')
_region({'ES', 'PT'}, 'Iberia')
_region(MIDDLE_EAST, 'Middle East', 'Mid-East', 'Mideast')
_region(MIDDLE_EAST | UN['NORTHERN_AFRICA'], 'MENA')
_region({'AE', 'BH', 'KW', 'OM', 'QA', 'SA'}, 'GCC', 'Gulf region', 'Gulf countries')    # not "Gulf": Gulf Breeze, FL
_region(UN['AFRICA'], 'Africa')
_region(UN['SUB_SAHARAN_AFRICA'], 'Sub-Saharan Africa', 'Subsaharan Africa')
_region(UN['NORTHERN_AFRICA'], 'North Africa', 'Northern Africa')
_region(UN['EASTERN_AFRICA'], 'East Africa', 'Eastern Africa')
_region(UN['WESTERN_AFRICA'], 'West Africa', 'Western Africa')
_region(UN['MIDDLE_AFRICA'], 'Central Africa', 'Middle Africa')
_region(UN['SOUTHERN_AFRICA'], 'Southern Africa')
_region(UN['LATIN_AMERICA'], 'LatAm', 'Latin America', 'Latin America and the Caribbean')
_region(UN['SOUTH_AMERICA'], 'South America')
_region(UN['CENTRAL_AMERICA'], 'Central America')
_region(UN['CENTRAL_AMERICA'] | UN['SOUTH_AMERICA'], 'Central and South America')
_region(UN['CARIBBEAN'], 'Caribbean')
_region(UN['NORTHERN_AMERICA'] | {'MX'}, 'North America')
_region(UN['AMERICAS'], 'Americas', 'AMER')
_region(UN['EASTERN_ASIA'] | UN['SOUTH_EASTERN_ASIA'] | UN['SOUTHERN_ASIA'] | UN['CENTRAL_ASIA'] | UN['OCEANIA'],
        'APAC', 'Asia Pacific', 'Asia-Pacific', 'APJ')
_region(UN['ASIA'], 'Asia')
_region(UN['SOUTH_EASTERN_ASIA'], 'Southeast Asia', 'South East Asia', 'South-East Asia', 'SE Asia')
_region(UN['SOUTHERN_ASIA'], 'South Asia', 'Southern Asia')
_region(UN['EASTERN_ASIA'], 'East Asia', 'Eastern Asia')
_region(UN['CENTRAL_ASIA'], 'Central Asia')
_region(UN['OCEANIA'], 'Oceania')
_region({'AU', 'NZ'}, 'ANZ', 'Australia and New Zealand', 'Australasia')
LONGEST = max(len(name.split()) for name in REGIONS)

WORLD = {'worldwide', 'global', 'globally', 'anywhere', 'everywhere', 'international', 'internationally', 'world',
         'earth'}
REMOTE = {'remote', 'remotely', 'wfh', 'distributed', 'virtual', 'home'}
FILLER = REMOTE | {'fully', 'full', '100', 'work', 'working', 'from', 'only', 'first', 'friendly', 'based', 'in',
                   'any', 'all', 'location', 'locations', 'country', 'countries', 'of', 'a', 'or', 'wide', 'time',
                   'zone', 'zones', 'timezone', 'timezones', 'team', 'role', 'position', 'opportunity', 'region',
                   'regions', 'open', 'to'}


def tokens(text: str | None) -> list[str]:
    return key(text).split()


def entry_kind(toks: list[str]) -> str | None:
    """One job location: 'world' when it says only worldwide, global or anywhere ("Remote (Anywhere in the
    world)"), 'remote' when it says only remote ("Remote", "Fully Remote"), None when it names a place.
    "Anywhere (USA)" names a place, and so does a street ("1660 International Dr")."""
    if any(t not in FILLER and t not in WORLD for t in toks):
        return None
    if any(t in WORLD for t in toks):
        return 'world'
    return 'remote' if not toks or any(t in REMOTE for t in toks) else None


def world_query(toks: list[str]) -> bool:
    """A typed place that means worldwide: Worldwide, Global, Anywhere, Remote worldwide, any location."""
    return entry_kind(toks) == 'world' or (bool(toks) and all(t in FILLER for t in toks)
                                          and ' '.join(toks) in ('any location', 'all locations', 'any country',
                                                                 'all countries'))


def region_query(toks: list[str]) -> frozenset[str] | None:
    """A typed place that is a region: 'EMEA', 'Remote EMEA', 'DACH region', 'Europe only'."""
    core = [t for t in toks if t not in REMOTE and t not in ('region', 'regions', 'only', 'countries', 'based')]
    return REGIONS.get(' '.join(core)) if core else None


def regions_in(toks: list[str], is_country) -> list[frozenset[str]]:
    """Every region named in one location's words, longest name first. A region word inside a country's
    name is not a region: 'South Africa' is ZA, not Africa (is_country reads a few words as a country)."""
    found, i = [], 0
    while i < len(toks):
        for n in range(min(LONGEST, len(toks) - i), 0, -1):
            codes = REGIONS.get(' '.join(toks[i:i + n]))
            if codes is None:
                continue
            if any(is_country(' '.join(toks[a:b])) for a, b in ((i - 1, i + n), (i - 2, i + n), (i, i + n + 1))
                   if a >= 0 and b <= len(toks)):
                continue
            found.append(codes)
            i += n
            break
        else:
            i += 1
    return found
