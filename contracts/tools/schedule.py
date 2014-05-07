"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
if __name__ == "__main__":
    from . import set_up
    set_up.set_up_django_environment('tools.settings_private')

from contracts.crawler import crawler
from contracts import models
from contracts.analysis import AnalysisManager


def update():
    # retrieve latest data.
    affected_entities = crawler.update_all()

    # update entities cached data
    for entity in affected_entities:
        entity.compute_data()

    # update categories cached data
    for category in models.Category.objects.all():
        category.compute_data()

    # update analysis
    for analysis in list(AnalysisManager.values()):
        analysis.update()

if __name__ == "__main__":
    update()
