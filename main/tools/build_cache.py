"""
Script used to rebuild all the cache.
"""
from . import set_up

set_up.set_up_django_environment('main.settings_for_schedule')


import contracts.tools.schedule
import law.tools.schedule
import deputies.tools.schedule


contracts.tools.schedule.update_cache()
law.tools.schedule.update_cache()
deputies.tools.schedule.update_cache()
