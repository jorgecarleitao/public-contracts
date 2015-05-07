"""
Settings file for the scheduler. Requires a `settings_live` with private
information of the server.

Imports everything from `settings.py`, and them overwrites some of the settings.
"""
from .settings import *
from . import settings_live

INSTALLED_APPS = (
    'deputies',
    'law',
    'contracts',
    'main',
    'django_rq',
)

# django_rq related
RQ_QUEUES = settings_live.RQ_QUEUES

# ignore requests logging
import logging
logging.getLogger("requests").setLevel(logging.WARNING)

# use DEBUG for pt_law_downloader so if any publication fails to download,
# we have a log of its number.
l = logging.getLogger('pt_law_downloader')
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
