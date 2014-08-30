import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from . import set_up

set_up.set_up_django_environment('main.settings_for_schedule')

from deputies.tools import schedule as deputies_schedule
from contracts.tools import schedule as contracts_schedule
from law.tools import schedule as law_schedule

try:
    contracts_schedule.update()
except Exception:
    logger.exception("contracts_schedule failed")

try:
    law_schedule.update()
except Exception:
    logger.exception("law_schedule failed")

#try:
#    deputies_schedule.update()
#except:
#    print("deputies_schedule failed")
#    raise
