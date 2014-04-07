
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contratos',
        'USER': 'contratos',
        'PASSWORD': 'contratos',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'law',
)

# Mandatory in Django, doesn't make a difference for our case.
SECRET_KEY = 'not-secret'
