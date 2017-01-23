from babel import Locale
from pycountry import countries

CORE_FACETS = {
    'company_name': 'Company',
    'filing_type': 'Filing Type',
    #'sector': 'Industry Sectors',
    #'industry': 'Industry',
    #'filing_date': 'Filing Date',
    'file_size': 'File Size',


    # 'extension': 'File extension',
    #'mime_type': 'Content type',
    #'languages': 'Languages',
    #'countries': 'Countries',
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
    # pycountry 16.10.23 renamed alpha2 to alpha_2
    # work with any version -- see https://pypi.python.org/pypi/pycountry
    if hasattr(country, 'alpha_2'):
        COUNTRY_NAMES[country.alpha_2.lower()] = country.name
    else:
        COUNTRY_NAMES[country.alpha2.lower()] = country.name


LANGUAGE_NAMES = dict(Locale('en').languages.items())
LANGUAGE_NAMES = {k: v for k, v in LANGUAGE_NAMES.items() if len(k) == 2}
