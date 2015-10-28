"""
Settings file for the scheduler.

Imports everything from `settings.py`, and them overwrites some of the settings.
"""
from .settings import *

INSTALLED_APPS = (
    'deputies',
    'law',
    'contracts',
    'main',
)

# ignore requests logging
import logging
logging.getLogger("requests").setLevel(logging.WARNING)

# use DEBUG for pt_law_downloader so if any publication fails to download,
# we have a log of its number.
l = logging.getLogger('pt_law_downloader')
l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())
