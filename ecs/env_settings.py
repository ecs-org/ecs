import os
from urllib.parse import urlparse

if os.getenv('DATABASE_URL'):
    parsed = urlparse(os.getenv('DATABASE_URL'))
    DATABASES = {}
    DATABASES['default'] = {
        'NAME': url.path[1:] or '',
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname or '',
        'PORT': url.port or '5432',
        'ATOMIC_REQUESTS': True
    }

if os.getenv('MEMCACHED_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': os.getenv('MEMCACHED_URL').split('//')[1],
        }
    }

if os.getenv('REDIS_URL'):
    BROKER_URL = os.getenv('REDIS_URL')
    BROKER_TRANSPORT_OPTIONS = {
        'fanout_prefix': True,
        'fanout_patterns': True
    }
    CELERY_RESULT_BACKEND = BROKER_URL
    CELERY_ALWAYS_EAGER = False

# import and execute ECS_SETTINGS as python code
if os.getenv('ECS_SETTINGS'):
    exec(os.getenv('ECS_SETTINGS'))
