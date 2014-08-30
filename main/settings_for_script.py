
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

INSTALLED_APPS = (
    'contracts',
    'law',
    'deputies'
)

# Mandatory in Django, doesn't make a difference for our case.
SECRET_KEY = 'not-secret'
