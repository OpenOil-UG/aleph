'''
Update sources on a schedule
'''
import schedule
import time, datetime
from aleph.crawlers import crawl_source
from aleph.core import es, es_index
from aleph.contrib.openoil.alerts import check_alerts



def _crawler(sourcename):
    def _inner():
        crawl_source.delay(sourcename, ignore_tags=False)
        #return schedule.CancelJob
    return _inner

def schedule_updates():

    # EDGAR
    schedule.every(1).days.at("04:30").do(_crawler('sec-edgar'))

    schedule.every(1).days.at("01:00").do(_crawler('openoil-internal-documents'))
    # SEDAR
    # Sedar website stops updating at 11pm ET, i.e. 0500 CET
    # We start our scrape just after, at 0511 CET, and allow 3 hours for it to
    # upload
    schedule.every(1).days.at("08:00").do(_crawler('sedar-partial-content'))

    #schedule.every(1).days.at("16:00").do(check_alerts)

    #schedule.run_all()
    
    while(1):
        schedule.run_pending()
        time.sleep(1)
    
