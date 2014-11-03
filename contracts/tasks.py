"""
Contains tasks for celery.
"""
from celery import shared_task, group
from celery.utils.log import get_task_logger

from contracts.crawler import StaticDataCrawler, EntitiesCrawler, \
    ContractsCrawler, TendersCrawler
from contracts import models
from contracts.analysis import analysis_manager

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def create_static_fixture():
    # check if we need to download static data
    if not models.ProcedureType.objects.exists():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()


@shared_task(ignore_result=True)
def create_categories_fixture():
    # check if we need to create categories
    if not models.Category.objects.exists():
        from contracts.tools.cpvs import build_categories
        build_categories()


@shared_task(ignore_result=True)
def create_fixture():
    group([create_static_fixture.s(), create_categories_fixture.s()])()


@shared_task(ignore_result=True)
def retrieve_new_entities():
    crawler = EntitiesCrawler()
    crawler.update()


@shared_task(ignore_result=True)
def retrieve_new_contracts():
    crawler = ContractsCrawler()
    crawler.update()


@shared_task(ignore_result=True)
def retrieve_new_tenders():
    crawler = TendersCrawler()
    crawler.update()


@shared_task(ignore_result=True)
def recompute_entities_data():
    for entity in models.Entity.objects.all():
        entity.compute_data()


@shared_task(ignore_result=True)
def recompute_categories_data():
    for category in models.Category.objects.all():
        category.compute_data()


@shared_task(ignore_result=True)
def recompute_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()


@shared_task(ignore_result=True)
def update():
    create_fixture()
    retrieve_new_contracts()
    group([recompute_entities_data.s(), recompute_categories_data.s()])()
    recompute_analysis()
