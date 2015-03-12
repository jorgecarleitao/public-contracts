import django_rq
from django_rq import job

import contracts.tasks
import law.tasks


@job
def update():
    #django_rq.enqueue(law.tasks.update)
    django_rq.enqueue(contracts.tasks.update)
