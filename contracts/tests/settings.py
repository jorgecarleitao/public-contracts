DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tests',
        'TEST_NAME': 'tests_test',
        'USER': 'postgres'
    },
}

INSTALLED_APPS = ('contracts',)

SECRET_KEY = 'no secret'

MIDDLEWARE_CLASSES = ()
