import datetime
import logging


from law.analysis import analysis_manager
from law.crawler import save_document

from pt_law_downloader import get_documents


def bootstrap_database():
    logging.getLogger('django').setLevel(logging.INFO)
    logging.getLogger('pt_law_downloader').setLevel(logging.INFO)
    for year in range(1975, datetime.datetime.now().date().year + 1):
        for document in get_documents('I', year):
            save_document(document)


def update_database(from_year=datetime.datetime.now().date().year,
                    to_year=datetime.datetime.now().date().year):
    for year in range(from_year, to_year + 1):
        for document in get_documents('I', year):
            save_document(document)


def update_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()


def update():
    update_database()
    update_analysis()
