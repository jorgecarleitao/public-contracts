# e.g. SITE_DOMAIN = 'www.example.com'
from .domain import SITE_DOMAIN
# This file has a set of private settings dependent on the particular host.
from . import settings_local

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if hasattr(settings_local, 'ADMINS'):
    ADMINS = settings_local.ADMINS
    MANAGERS = ADMINS


if hasattr(settings_local, 'EMAIL_HOST'):
    EMAIL_HOST = settings_local.EMAIL_HOST
    EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
    SERVER_EMAIL = settings_local.SERVER_EMAIL
    EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_DOMAIN


import socket

if socket.gethostname() == settings_local.HOST_NAME:
    LIVE = True
    DEBUG = False
    TEMPLATE_DEBUG = False
else:
    LIVE = False

import os.path

main_directory = os.path.abspath(os.path.dirname(__file__))
site_directory = os.path.abspath(os.path.dirname(main_directory))

TIME_ZONE = 'Europe/Lisbon'
LANGUAGE_CODE = 'pt'

LANGUAGES = (('en', 'English'),
             ('pt', 'Portuguese'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contracts',
        'USER': 'public_contracts',
        'PASSWORD': 'read-only',
        'HOST': '5.153.9.51',
        'PORT': '3306',
    }
}
if LIVE and hasattr(settings_local, 'DATABASES'):
    DATABASES = settings_local.DATABASES

# to make tests run faster
import sys
if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

ALLOWED_HOSTS = ['*']
SECRET_KEY = settings_local.SECRET_KEY

USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = (site_directory + '/locale',)

STATIC_ROOT = os.path.join(main_directory, 'static')
if LIVE:
    STATIC_ROOT = settings_local.STATIC_ROOT

STATIC_URL = '/static/'
if LIVE:
    STATIC_URL = 'http://%s/static/' % SITE_DOMAIN


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.locale.LocaleMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}
if LIVE and hasattr(settings_local, 'CACHES'):
    CACHES = settings_local.CACHES

TIMEOUT = 60*60*24

ROOT_URLCONF = 'main.urls'
WSGI_APPLICATION = 'main.apache.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "django.core.context_processors.request",
                               "main.context_processors.site",)

INSTALLED_APPS = (
    'main',
    'contracts',
    'deputies',
    'law',
    'treebeard',  # for model in trees
    'sphinxql',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES


INDEXES = {
    'PATH': os.path.join(site_directory, '_index'),
    'sphinx_path': site_directory,
    'index_params': {
        'charset_table':
        'U+00C0..U+00C3->U+00E0..U+00E3, U+00E0..U+00E3, '  # Á..Â -> á..â
        'U+00EA, U+00CA->U+00EA, '  #Ê -> ê
        'U+00E9, U+00C9->U+00E9, '  #É -> é
        'U+00ED, U+00CD->U+00ED, '  #Í -> í
        'U+00F2..U+00F5, U+00D2..U+00D5->U+00F2..U+00F5, '  #Ó -> ó
        'U+00FA, U+00DA->U+00FA, '  #Ú -> ú
        'U+00E7, U+00C7->U+00E7, '  #Ç -> ç
        '0..9, A..Z->a..z, _, a..z'
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        # If in debug, DEBUG to console
        'debug_console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # If no debug, INFO to console.
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        # If no debug, errors to admins
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # This is the "catch all" logger
        '': {
            'handlers': ['debug_console', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# for celery
if hasattr(settings_local, 'BROKER_URL'):
    BROKER_URL = settings_local.BROKER_URL
