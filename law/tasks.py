import datetime
import logging

from django_rq import job

from law.analysis import analysis_manager
from law.crawler import save_document

from pt_law_downloader import get_documents


@job
def bootstrap_database():
    logging.getLogger('django').setLevel(logging.INFO)
    logging.getLogger('pt_law_downloader').setLevel(logging.INFO)
    for year in range(1975, datetime.datetime.now().date().year + 1):
        for document in get_documents('I', year):
            save_document(document)


@job
def update_database():
    year = datetime.datetime.now().date().year
    for year in range(year - 1, year + 1):
        for document in get_documents('I', year):
            save_document(document)


@job
def update_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()


@job
def update():
    update_database()
    update_analysis()
