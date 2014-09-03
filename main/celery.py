import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings_for_schedule')

app = Celery('main')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# PATH=PATH:/home/littlepig/webapps/publics/erlang/bin;
# ./rabbitmq_server-3.3.5/sbin/rabbitmq-server -detached;
# ./rabbitmq_server-3.3.5/sbin/rabbitmqctl set_vm_memory_high_watermark 0.016 [32 MB/ 2 GB]
# ./rabbitmq_server-3.3.5/sbin/rabbitmq-server status
