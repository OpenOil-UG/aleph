import logging

from aleph.core import celery
from aleph.ext import get_crawlers
from aleph.crawlers.crawler import DocumentCrawler, Crawler # noqa
from aleph.crawlers.web import WebCrawler  # noqa

log = logging.getLogger(__name__)


def get_exposed_crawlers():
    """Return all crawlers which can be run automatically via the web UI."""
    for name, clazz in get_crawlers().items():
        if not issubclass(clazz, DocumentCrawler):
            continue
        if clazz.SOURCE_ID is None:
            continue
        yield clazz()


@celery.task()
def execute_crawler(crawler_id, incremental=False, param=None):
    for cls in get_exposed_crawlers():
        if cls.get_id() != crawler_id:
            continue
        # XXX clean up/document param infrastructure
        params = {'param': param} if param else {}
        cls.execute(incremental=incremental, **params)


@celery.task()
def execute_scheduled():
    for cls in get_exposed_crawlers():
        if cls.SCHEDULE is None:
            continue
        crawler_id = cls.get_id()
        if cls.SCHEDULE.check_due(crawler_id):
            log.info("Crawler is due: %s", crawler_id)
            execute_crawler.delay(crawler_id, incremental=True)
