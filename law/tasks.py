from celery import shared_task, group
from celery.utils.log import get_task_logger

from law.analysis import analysis_manager
from law.crawler import FirstSeriesCrawler, Populator

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def update_documents():
    import datetime
    current_year = datetime.datetime.now().date().year
    for year in range(current_year - 1, current_year + 1):
        crawler = FirstSeriesCrawler()
        crawler.get_documents(year)
        del crawler

    p = Populator()
    p.populate_all(current_year - 1)


@shared_task(ignore_result=True)
def update_analysis():
    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()


@shared_task(ignore_result=True)
def update():
    update_documents()
    update_analysis()
