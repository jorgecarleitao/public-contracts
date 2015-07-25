from main.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tests',
        'TEST_NAME': 'tests_test',
        'USER': 'postgres'
    },
}

LANGUAGE_CODE = 'en'

# ignore all logging
import logging
logging.disable(logging.CRITICAL)
