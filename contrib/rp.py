'''
import script for resourceprojects json
'''
import click
import requests
import retrying
import pycountry

@retrying.retry(stop_max_attempt_number=10)
def projects_from_rp(url):
    json = requests.get(url).json()
    for obj in json['data']:
        companies = u','.join(x['company_name'] for x in obj['companies'])
        project_name = obj['proj_name']
        project_id = obj['proj_id']
        # XXX theoretically there could be multiple countriews
        # but it seems not to happen in practice
        # XXX we also have ['country']['iso2']
        # it might be better to work out a search-friendly name ourselves
        country = obj['proj_country'][0]['country']['name']
        print(u', '.join(u'"%s"' % x for x in [project_id, project_name, country, companies]).encode('utf-8'))        

@click.command()
def importjson_bycountry():
    iso2s = [x.alpha2 for x in pycountry.countries]
    for iso2 in iso2s:
        url = 'http://resourceprojects.org/api/projects/%s/1000/0' % iso2
        projects_from_rp(url)

@click.command()
def importjson():
    limit = 50
    total_projects = 3000
    for offset in range(0,total_projects,limit):
        url = 'http://resourceprojects.org/api/projects/%s/%s' % (limit, offset)
        projects_from_rp(url)
    pass

if __name__ == '__main__':
    importjson()

    
