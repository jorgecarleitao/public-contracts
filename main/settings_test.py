from main.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tests',
        'TEST_NAME': 'tests_test',
        'USER': 'postgres'
    },
}

# ignore requests logging
import logging
logging.getLogger("requests").setLevel(logging.WARNING)
