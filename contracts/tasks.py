from contracts.crawler import StaticDataCrawler, EntitiesCrawler, \
    ContractsCrawler, TendersCrawler
from contracts import models
from contracts.analysis import analysis_manager


def create_static_fixture():
    # check if we need to download static data
    if not models.ProcedureType.objects.exists():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()


def create_categories_fixture():
    # check if we need to create categories
    if not models.Category.objects.exists():
        from contracts.tools.cpvs import build_categories
        build_categories()


def create_fixture():
    create_static_fixture()
    create_categories_fixture()


def retrieve_new_entities():
    crawler = EntitiesCrawler()
    crawler.update()


def retrieve_new_contracts():
    crawler = ContractsCrawler()
    crawler.update()


def retrieve_new_tenders():
    crawler = TendersCrawler()
    crawler.update()


def recompute_entities_data():
    for entity in models.Entity.objects.all():
        entity.compute_data()


def recompute_categories_data():
    for category in models.Category.objects.all():
        category.compute_data()


def recompute_analysis():
    for analysis in list(analysis_manager.values()):
        analysis.update()
