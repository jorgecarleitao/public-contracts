"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    from main.tools import set_up
    set_up.set_up_django_environment('main.settings_for_schedule')

from contracts.crawler import DynamicDataCrawler, StaticDataCrawler
from contracts import models
from contracts.analysis import analysis_manager


def update():
    # check if we need to retrieve static data
    if not models.ProcedureType.objects.exists():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()

    # check if we need to create categories
    if not models.Category.objects.exists():
        from contracts.tools.cpvs import build_categories
        build_categories()

    # retrieve latest dynamic data.
    crawler = DynamicDataCrawler()
    crawler.update_all()

    # update entities cached data
    for entity in models.Entity.objects.all():
        entity.compute_data()

    # update categories cached data
    for category in models.Category.objects.all():
        category.compute_data()

    update_cache()


def update_cache():
    # update analysis
    for analysis in list(analysis_manager.values()):
        analysis.update()


if __name__ == "__main__":
    update()
