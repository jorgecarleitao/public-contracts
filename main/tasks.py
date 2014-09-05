from celery import shared_task, group

import contracts.tasks
import law.tasks


@shared_task(ignore_result=True)
def update():
    group([law.tasks.update.s(),
           contracts.tasks.update.s()])()
