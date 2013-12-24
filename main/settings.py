# e.g. SITE_DOMAIN = u'www.example.com'
from domain import SITE_DOMAIN
# This file has a set of private settings dependent on the particular host.
import settings_local

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if hasattr(settings_local, 'ADMINS'):
    ADMINS = settings_local.ADMINS
    MANAGERS = ADMINS

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
USE_L10N = False
USE_TZ = True
LOCALE_PATHS = (site_directory + '/locale',)

MEDIA_ROOT = os.path.join(main_directory, 'media')

MEDIA_URL = '/media/'
if LIVE:
    MEDIA_URL = 'http://%s/media/' % SITE_DOMAIN

STATIC_ROOT = os.path.join(main_directory, 'static')
if LIVE:
    STATIC_ROOT = settings_local.STATIC_ROOT

STATICFILES_DIRS = (
    os.path.join(site_directory, 'docs/build'),
)

STATIC_URL = '/static/'
if LIVE:
    STATIC_URL = 'http://%s/static/' % SITE_DOMAIN


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'treebeard',  # for model in trees
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if hasattr(settings_local, 'DEFAULT_FROM_EMAIL'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
    EMAIL_HOST = settings_local.EMAIL_HOST
    EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
    EMAIL_PORT = settings_local.EMAIL_PORT
    SERVER_EMAIL = settings_local.SERVER_EMAIL
