'''
Support for resourceprojects inclusion of aleph search results.

NB this page should interact with the db only through the API
'''

from flask import Blueprint, request, render_template, Response, abort
import lxml.html
import requests
import unicodecsv as csv
import langid


API_KEY = 'oo_u1gvq1vzrckpomv5r' # key for daniel+resourceprojects@openoil.net
BASE_URL = 'https://aleph.openoil.net/'
CSV_URL = 'https://docs.google.com/spreadsheets/d/1nYDM9PXiNLV5SkUeR4vS-MVfIbFEIKNBzsRzTN-kPoY/export?format=csv&amp;usp=sharing'

RESULTS_TO_SHOW=3

RULE_COLUMNS = {
    # name of rule, column in spreadsheet
    'strip_inner_text' : 9,
    'quotes': 10,
    'query_country': 11,
    'query_company': 12,
    }
RULE_COLUMNS = {
    # name of rule, column in spreadsheet
    'strip_inner_text' : 8,
    'quotes': 9,
    'query_country': 10,
    'query_company': 11,
    }

blueprint = Blueprint('clients', __name__)

@blueprint.route('/clients/resourceprojects/', methods=['GET'])
def frame():
    project_name = request.args.get('project_name', 'nothing supplied')
    project_query = _query_from_project(project_name)
    jsondata = _api_request(project_query) # XXX this should be done async
    topmatches = postfilter_results(jsondata, project_name)

    return Response(render_template("resourceprojects.html", results=topmatches, query=project_query)) # XXX this template should live somewhere else

def make_query(metadata):
    q = metadata['search_name']
    if metadata['strip_inner_text']:
        for word in (' mine', ' concession', ' project'):
            if q.endswith(word):
                word = word[:-len(word)]
    if metadata['quotes']:
        q = '"%s"' % q
    if metadata['query_country']:
        q = q + ' ' + metadata['country']
    # currently non-functional, since we don't have company info to hand
    #if metadata['query_company']:
    #    q = q + ' ' + metadata['company']
    return q

def _query_from_project(project_name):
    allprojects = _dl_csv()
    project_name = project_name.lower()
    if project_name not in allprojects:
        print('did not find name in project list')
        print(allprojects)
        return project_name # fall back to just the string
    metadata = allprojects[project_name]
    query = make_query(metadata)
    return query

def notjunk(result):
    # XXX: should detect if this lacks english words
    text = ' '.join(result['extract'])
    classed = langid.classify(text)
    return (
        classed[0] == 'en'
        and classed[1] > 0.95
        )

def notrepetition(candidate, accepted):
    for extract in candidate['extract']:
        for existing in accepted:
            if extract in existing['extract']:
                return False
    return True

def containsname(result, project_name):
    print(project_name)
    for e in result['extract_textonly']:
        if project_name.lower() in e.lower():
            return True
    return False

def postfilter_results(jsondata, project_name):
    r = jsondata['results']
    accepted = []
    for result in r:
        result['extract_textonly'] = []
        for e in result['extract']:
            result['extract_textonly'].append(lxml.html.fromstring(e).text_content())
        
        print('exclusions are %s %s %s' % (
            notjunk(result),
            notrepetition(result, accepted),
            containsname(result, project_name),
            ))
        if (
            True # notjunk(result)
            and notrepetition(result, accepted)
            and containsname(result, project_name)
        ):
            accepted.append(result)
        if len(accepted) >= RESULTS_TO_SHOW:
            break
    return accepted

def _api_request(query):
    params = {
        'apikey': API_KEY,
        'q': query,
        'limit': 40,
        'sort': 'newest_filed',
        }
    url = '%s/aleph_api/1/query' % BASE_URL
    result = requests.get(url, params=params)
    return result.json()

def _sheet_for_project(project_name):
    pass

def _dl_csv(refresh=False):
    if refresh or not hasattr(_dl_csv, 'projects'):
        print('getting fresh')
        response = requests.get(CSV_URL)
        response_text = requests.utils.get_unicode_from_response(response).encode('ascii', 'ignore')
        csvfile = csv.reader(response_text.splitlines(), encoding='utf-8')
        projects = {}
        # skip header rows
        csvfile.next()
        csvfile.next()
        for row in csvfile:
            metadata = {
                'name': row[0],
                'search_name': row[7] or row[0], # replacement name
                'country': row[2],
                }
            for rulename, col in RULE_COLUMNS.items():
                metadata[rulename] = row[col] == 'y'
            projects[row[0].lower()] = metadata
        _dl_csv.projects = projects
    else:
        print('getting from cache')
    return _dl_csv.projects

