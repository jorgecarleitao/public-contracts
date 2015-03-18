import django_rq
from django_rq import job

import contracts.tasks
import law.tasks
import deputies.tasks


@job
def update():
    django_rq.enqueue(law.tasks.update)
    django_rq.enqueue(contracts.tasks.update)
    django_rq.enqueue(deputies.tasks.recompute_analysis)
