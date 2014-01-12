"""
Module run every day by a cron job to update database
and cache.
"""
## setup the Django with its private settings for server.
import set_up
set_up.set_up_django_environment('settings_private')

from contracts.crawler import crawler
from contracts import models
from contracts.analysis import AnalysisManager

# retrieve latest entities and contracts.
crawler.update_entities()
crawler.update_contracts()

# update entities earnings and expenses
for entity in models.Entity.objects.all():
    entity.compute_data()

# update analysis
for analysis in AnalysisManager.values():
    analysis.update()
