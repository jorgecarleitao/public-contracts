"""
Settings file for the scheduler. Requires a ``settings_local`` with private
information about the database and cache.
"""
from . import settings_local
from . import domain

INSTALLED_APPS = (
    'deputies',
    'law',
    'contracts',
    'main'
)

DATABASES = settings_local.DATABASES

SECRET_KEY = settings_local.SECRET_KEY

CACHES = settings_local.CACHES

ADMINS = settings_local.ADMINS

if hasattr(settings_local, 'EMAIL_HOST'):
    EMAIL_HOST = settings_local.EMAIL_HOST
    EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
    SERVER_EMAIL = settings_local.SERVER_EMAIL
    EMAIL_SUBJECT_PREFIX = '[%s] ' % domain.SITE_DOMAIN


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        # DEBUG to console.
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # errors to admins
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# ignore requests logging
import logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

# for celery
if hasattr(settings_local, 'BROKER_URL'):
    BROKER_URL = settings_local.BROKER_URL
