DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contracts',
        'USER': 'contracts',
        'PASSWORD': 'Colacola1',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'contracts',
    'deputies',
)

# Mandatory in Django, doesn't make a difference in our case.
SECRET_KEY = 'not-secret'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'unix:/home/littlepig/memcached.sock'
    }
}
