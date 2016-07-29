from babel import Locale
from pycountry import countries

CORE_FACETS = {
    'company_name': 'Company',
    'filing_type': 'Filing Type',
    'sector': 'Industry Sectors',
    #'filing_date': 'Filing Date',
    #'file_size': 'File Size',


    # 'extension': 'File extension',
    #'mime_type': 'Content type',
    'languages': 'Languages',
    'countries': 'Countries',
    #'keywords': 'Keywords',
    #'author': 'Document author',
    #'emails': 'E-Mail addresses',
    #'domains': 'Internet domains',
    #'dates': 'Dates',

}

SOURCE_CATEGORIES = {
    'news': 'News reports',
    'leak': 'Leaks',
    'gazette': 'Gazette notices',
    'court': 'Court cases',
    'company': 'Company records',
    'scrape': 'Scrapes',
    'procurement': 'Procurement',
    'grey': 'Grey Literature'
}

COUNTRY_NAMES = {
    'zz': 'Global',
    'xk': 'Kosovo'
}

for country in countries:
    COUNTRY_NAMES[country.alpha2.lower()] = country.name


LANGUAGE_NAMES = dict(Locale('en').languages.items())
LANGUAGE_NAMES = {k: v for k, v in LANGUAGE_NAMES.items() if len(k) == 2}
