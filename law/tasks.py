import datetime
import logging

from celery import shared_task
from celery.utils.log import get_task_logger

from law.analysis import analysis_manager
from law.crawler import save_document

from pt_law_downloader import get_documents


logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def bootstrap_database():
    logging.getLogger('django').setLevel(logging.INFO)
    logging.getLogger('pt_law_downloader').setLevel(logging.INFO)
    for year in range(1975, datetime.datetime.now().date().year + 1):
        for document in get_documents('I', year):
            save_document(document)


@shared_task(ignore_result=True)
def update_database():
    year = datetime.datetime.now().date().year
    for year in range(year - 1, year + 1):
        for document in get_documents('I', year):
            save_document(document)


@shared_task(ignore_result=True)
def update_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()


@shared_task(ignore_result=True)
def update():
    update_database()
    update_analysis()
