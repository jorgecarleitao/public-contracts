"""
Settings file for the scheduler. Requires a `settings_live` with private
information of the server.
"""
from . import settings_live
from . import domain

INSTALLED_APPS = (
    'deputies',
    'law',
    'contracts',
    'main',
    'django_rq',
)


DATABASES = settings_live.DATABASES

RQ_QUEUES = settings_live.RQ_QUEUES

SECRET_KEY = settings_live.SECRET_KEY

CACHES = settings_live.CACHES

ADMINS = settings_live.ADMINS

TIME_ZONE = 'Europe/Lisbon'

if hasattr(settings_live, 'EMAIL_HOST'):
    EMAIL_HOST = settings_live.EMAIL_HOST
    EMAIL_HOST_USER = settings_live.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings_live.EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = settings_live.DEFAULT_FROM_EMAIL
    SERVER_EMAIL = settings_live.SERVER_EMAIL
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
        # INFO to console.
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
logging.getLogger("requests").setLevel(logging.WARNING)
