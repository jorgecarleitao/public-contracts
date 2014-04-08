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

if DEBUG:
    MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES

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
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
)

if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)
