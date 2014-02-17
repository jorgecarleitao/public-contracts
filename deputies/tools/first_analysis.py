import set_up
set_up.set_up_django_environment('settings')

from datetime import timedelta, date
from deputies import models

for deputy in models.Deputy.objects.all():
    total_time = timedelta(0)
    for mandate in deputy.mandate_set.all():

        if mandate.date_end is None:
            mandate.date_end = date.today()

        total_time += mandate.date_end - mandate.date_begin

    if total_time:
        print deputy.id, total_time.days
