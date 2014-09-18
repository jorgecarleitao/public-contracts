"""
Contains tasks for celery.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

from deputies import crawler as c
from deputies.tools import populator as p
from deputies.analysis import analysis_manager

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def update_deputies():
    # check if we need to download static data
    crawler = c.DeputiesCrawler()
    populator = p.DeputiesDBPopulator()

    for entry in crawler.get_new_deputies():
        deputy = populator.populate_deputy(entry)
        deputy.update()


@shared_task(ignore_result=True)
def recompute_analysis():
    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()


@shared_task(ignore_result=True)
def update():
    update_deputies()
    recompute_analysis()
