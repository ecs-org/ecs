import os
import dj_database_url

def str2bool(text):
    if isinstance(text, bool):
        return text
    else:
        text = text.upper()
        return text in ['TRUE', 'YES']

def str2int(value):
    if isinstance(value, int):
        return value
    else:
        return int(value)

if os.getenv('DATABASE_URL'):
    DATABASES = {}
    DATABASES['default'] = dj_database_url.config()
    DATABASES['default']['ATOMIC_REQUESTS'] = True

if os.getenv('MEMCACHED_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': os.getenv('MEMCACHED_URL').split('//')[1],
        }
    }

if os.getenv('DEBUG'):
    DEBUG = str2bool(os.getenv('DEBUG'))

if os.getenv('ECS_LOGO_BORDER_COLOR'):
    ECS_LOGO_BORDER_COLOR = os.getenv('ECS_LOGO_BORDER_COLOR')

if os.getenv('ABSOLUTE_URL_PREFIX'):
    ABSOLUTE_URL_PREFIX = os.getenv('ABSOLUTE_URL_PREFIX')

ECSMAIL_OVERRIDE = {}
if os.getenv('ECS_AUTHORITATIVE_DOMAIN'):
    ECSMAIL_OVERRIDE['authoritative_domain']= \
        os.getenv('ECS_AUTHORITATIVE_DOMAIN')

if os.getenv('ECS_FILTER_OUTGOING_MAIL'):
    ECSMAIL_OVERRIDE['filter_outgoing_smtp']= \
        str2bool(os.getenv('ECS_FILTER_OUTGOING_MAIL'))

if os.getenv('EMAIL_BACKEND'):
    EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
    DEBUG_EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')

if os.getenv('LIMITED_EMAIL_BACKEND'):
    LIMITED_EMAIL_BACKEND = os.getenv('LIMITED_EMAIL_BACKEND')

if os.getenv('EMAIL_HOST'):
    EMAIL_HOST = os.getenv('EMAIL_HOST')

if os.getenv('EMAIL_PORT'):
    EMAIL_PORT = str2int(os.getenv('EMAIL_PORT'))

if os.getenv('EMAIL_HOST_USER'):
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')

if os.getenv('EMAIL_HOST_PASSWORD'):
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

if os.getenv('EMAIL_USE_TLS'):
    EMAIL_USE_TLS = str2bool(os.getenv('EMAIL_USE_TLS'))

if os.getenv('EMAIL_USE_SSL'):
    EMAIL_USE_SSL = str2bool(os.getenv('EMAIL_USE_SSL'))

if os.getenv('EMAIL_TIMEOUT'):
    EMAIL_TIMEOUT = str2int(os.getenv('EMAIL_TIMEOUT'))

if os.getenv('EMAIL_SSL_KEYFILE'):
    EMAIL_SSL_KEYFILE = os.getenv('EMAIL_SSL_KEYFILE')

if os.getenv('EMAIL_SSL_CERTFILE'):
    EMAIL_SSL_CERTFILE = os.getenv('EMAIL_SSL_CERTFILE')
