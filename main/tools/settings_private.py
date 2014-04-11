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
    'deputies',
    'law',
    'contracts'
)

# Mandatory in Django, doesn't make a difference in our case.
SECRET_KEY = 'not-secret'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/home/littlepig/memcached.sock'
    }
}
