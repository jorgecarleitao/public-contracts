import set_up
set_up.set_up_django_environment('settings_private')

from deputies.tools import schedule as deputies_schedule
from contracts.tools import schedule as contracts_schedule
from law.tools import schedule as law_schedule

try:
    law_schedule.update()
except:
    print("law_schedule failed")

try:
    contracts_schedule.update()
except:
    print("contracts_schedule failed")

try:
    deputies_schedule.update()
except:
    print("deputies_schedule failed")
