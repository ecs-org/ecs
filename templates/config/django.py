DEBUG = %(debug.enable)s

# database settings
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '%(postgresql.database)s',
    'USER': '%(postgresql.username)s',
    'HOST': 'localhost',
    'PASSWORD': '%(postgresql.password)s',
    'PORT': '6432', # use pgbouncer for connection with postgres
    'ATOMIC_REQUESTS': True,
})


# rabbitmq/celery settings
BROKER_URL = 'amqp://%(rabbitmq.username)s:%(rabbitmq.password)s@localhost:5672/%(rabbitmq.username)s'
CELERY_ALWAYS_EAGER = False

# haystack settings
HAYSTACK_CONNECTIONS['default']['ENGINE'] = '%(haystack.search_engine)s'

# multiprocess safe cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    },
}

# ecsmail settings
ECSMAIL['authoritative_domain'] = '%(host)s'
if %(debug.filter_smtp)s:
    ECSMAIL['filter_outgoing_smtp'] = True

import sys
if not any(word in sys.argv for word in set(['test', 'runserver'])):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


#PDFAS_SERVICE = 'http://%(host)s:4780/pdf-as/'
PDFAS_SERVICE = 'https://%(host)s/pdf-as-web/'

ABSOLUTE_URL_PREFIX = "https://%(host)s"

ECS_REQUIRE_CLIENT_CERTS = not %(debug.no_client_certs_for_internal)s
ECS_MANDATORY_CLIENT_CERTS = %(debug.always_need_certs)s

ECS_USERSWITCHER = %(debug.userswitcher)s
ECS_LOGO_BORDER_COLOR = '%(debug.logo_border_color)s'

SECRET_KEY = '%(auth.SECRET_KEY)s'
REGISTRATION_SECRET = '%(auth.REGISTRATION_SECRET)s'
PASSWORD_RESET_SECRET = '%(auth.PASSWORD_RESET_SECRET)s'

STORAGE_VAULT_DIR = '%(storagevault.options.localfilestorage_root)s'
STORAGE_ENCRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "ecs-encrypt", "gpg"),
    "encrypt_key": os.path.join(PROJECT_DIR, "..", "ecs-conf", "ecs_mediaserver.pub"),
    "encrypt_owner": '%(documents.storage.encrypt_owner)s',
    "signing_key": os.path.join(PROJECT_DIR, "..", "ecs-conf", "ecs_authority.sec"),
    "signing_owner": '%(documents.storage.signing_owner)s',
}

STORAGE_DECRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "ecs-decrypt", "gpg"),
    "decrypt_key": os.path.join(PROJECT_DIR, "..", "ecs-conf", "ecs_mediaserver.sec"),
    "decrypt_owner": "%(documents.storage.decrypt_owner)s",
    "verify_key":  os.path.join(PROJECT_DIR, "..", "ecs-conf", "ecs_authority.pub"),
    "verify_owner": "%(documents.storage.verify_owner)s",
}

ALLOWED_HOSTS = ['%(hostname)s']
