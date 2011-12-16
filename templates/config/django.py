# database settings
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '%(postgresql.username)s',
    'USER': '%(postgresql.username)s',
})

# rabbitmq/celery settings
BROKER_USER = '%(rabbitmq.username)s'
BROKER_PASSWORD = '%(rabbitmq.password)s'
BROKER_VHOST = '%(rabbitmq.username)s'
BROKER_BACKEND = ''
CELERY_ALWAYS_EAGER = False

# haystack settings
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/'

DEBUG = False
TEMPLATE_DEBUG = False

ECS_PDFCOP = '#'
ECS_PDFDECRYPT = '#'
PDFCOP_ENABLED = False

SECRET_KEY = '%(auth.SECRET_KEY)s'
REGISTRATION_SECRET = '%(auth.REGISTRATION_SECRET)s'
PASSWORD_RESET_SECRET = '%(auth.PASSWORD_RESET_SECRET)s'

FEEDBACK_CONFIG = {
    'create_trac_tickets': %(feedback.create_trac_tickets)s, 
    'store_in_db': %(feedback.store_in_db)s, 
    'RPC_CONFIG': {
        'username': '%(feedback.rpc.username)s', 
        'password': '%(feedback.rpc.password)s', 
        'proto': '%(feedback.rpc.proto)s', 
        'host': '%(feedback.rpc.host)s', 
        'urlpath': '%(feedback.rpc.path)s', 
    },
    'milestone': '%(feedback.milestone)s', 
    'component': '%(feedback.component)s',
    'ticketfieldnames': ['summary', 'description', 'location', 'absoluteurl', 'type', 'cc', 'ecsfeedback_creator', 'milestone', 'component']
}

BUGSHOT_CONFIG = {
    'bugshoturl': '%(bugshot.url)', 
    'milestone': '%(bugshot.milestone)',
}

MS_CLIENT = {
    "server": "%(mediaserver.client.server)s",
    "bucket": "%(mediaserver.client.bucket)s",
    "key_id": "%(mediaserver.client.key_id)s",
    "key_secret": "%(mediaserver.client.key_secret)s",
    "same_host_as_server": %(mediaserver.client.same_host_as_server)s,
}

STORAGE_ENCRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-encrypt", "gpg"),
    "encrypt_key": os.path.join(PROJECT_DIR, "..", "target", "ecs", "ecs_mediaserver.pub"),
    "encrypt_owner": '%(mediaserver.storage.encrypt_owner)s',
    "signing_key": os.path.join(PROJECT_DIR, "..", "target", "ecs", "ecs_authority.sec"),
    "signing_owner": '%(mediaserver.storage.signing_owner)s',
}

STORAGE_DECRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-decrypt", "gpg"),
    "decrypt_key": os.path.join(PROJECT_DIR, "..", "target", "mediaserver", "ecs_mediaserver.sec"),
    "decrypt_owner": "%(mediaserver.storage.decrypt_owner)s",
    "verify_key":  os.path.join(PROJECT_DIR, "..", "target", "mediaserver", "ecs_authority.pub"),
    "verify_owner": "%(mediaserver.storage.verify_owner)s",
}
