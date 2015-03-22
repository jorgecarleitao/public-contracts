
# for testing postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sphinx_example',
        'TEST_NAME': 'sphinx_example_test',
        'USER': 'sphinx_example',
        'PASSWORD': 'test'
    },
}

INSTALLED_APPS = ('law',)

SECRET_KEY = 'no secret'

MIDDLEWARE_CLASSES = ()
