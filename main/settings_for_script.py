
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'publics',
        'USER': 'publics_read_only',
        'PASSWORD': r'read-only',
        'HOST': '5.153.9.51',
        'PORT': '5432',
    }
}

INSTALLED_APPS = (
    'contracts',
    'law',
    'deputies'
)

# Mandatory in Django, doesn't make a difference for our case.
SECRET_KEY = 'not-secret'
