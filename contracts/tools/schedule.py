"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    from . import set_up
    set_up.set_up_django_environment('tools.settings_private')

from contracts.crawler import DynamicDataCrawler, StaticDataCrawler
from contracts import models
from contracts.analysis import analysis_manager


def update():
    # check if we need to update static data
    if not models.ProcedureType.objects.exists():
        c = StaticDataCrawler()
        c.retrieve_and_save_all()

    if not models.Category.objects.exists():
        from contracts.tools.cpvs import build_categories
        build_categories()

    # retrieve latest dynamic data.
    crawler = DynamicDataCrawler()
    affected_entities = crawler.update_all()

if __name__ == "__main__":
    update()
