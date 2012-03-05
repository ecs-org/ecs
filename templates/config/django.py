DEBUG = %(debug.enable)s
TEMPLATE_DEBUG = %(debug.template)s

# database settings
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '%(postgresql.database)s',
    'USER': '%(postgresql.username)s',
})

# rabbitmq/celery settings
BROKER_USER = '%(rabbitmq.username)s'
BROKER_PASSWORD = '%(rabbitmq.password)s'
BROKER_VHOST = '%(rabbitmq.username)s'
BROKER_BACKEND = ''
CELERY_ALWAYS_EAGER = False

# haystack settings
HAYSTACK_SEARCH_ENGINE = '%(haystack.search_engine)s'

# ecsmail settings
ECSMAIL['authoritative_domain'] = '%(host)s'
ECSMAIL['trusted_sources'] = ['127.0.0.1', '%(ip)s']
if %(debug.filter_smtp)s:
    ECSMAIL['filter_outgoing_smtp'] = True

import sys
if not any(word in sys.argv for word in set(['test', 'runserver','runconcurrentserver',])):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


PDFAS_SERVICE = 'http://%(host)s:4780/pdf-as/'
#PDFAS_SERVICE = 'https://%(host)s/pdf-as/'

ABSOLUTE_URL_PREFIX = "https://%(host)s"

ECS_REQUIRE_CLIENT_CERTS = not %(debug.no_client_certs_for_internal)s
ECS_MANDATORY_CLIENT_CERTS = %(debug.always_need_certs)s

ECS_USERSWITCHER = %(debug.userswitcher)s
ECS_DEVELOPER_TAB = %(debug.developer_tab)s
ECS_LOGO_BORDER_COLOR = '%(debug.logo_border_color)s'

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
    'bugshoturl': '%(bugshot.url)s', 
    'milestone': '%(bugshot.milestone)s',
}

MS_CLIENT = {
    "server": "%(mediaserver.client.server)s",
    "bucket": "%(mediaserver.client.bucket)s",
    "key_id": "%(mediaserver.client.key_id)s",
    "key_secret": "%(mediaserver.client.key_secret)s",
    "same_host_as_server": %(mediaserver.client.same_host_as_server)s,
}

STORAGE_VAULT = '%(storagevault.implementation)s'
STORAGE_VAULT_OPTIONS = {
    'LocalFileStorageVault.rootdir': '%(storagevault.options.localfilestorage_root)s',
    }

STORAGE_ENCRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-encrypt", "gpg"),
    "encrypt_key": os.path.join(PROJECT_DIR, "..", "..", "ecs-conf", "ecs_mediaserver.pub"),
    "encrypt_owner": '%(mediaserver.storage.encrypt_owner)s',
    "signing_key": os.path.join(PROJECT_DIR, "..", "..", "ecs-conf", "ecs_authority.sec"),
    "signing_owner": '%(mediaserver.storage.signing_owner)s',
}

STORAGE_DECRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-decrypt", "gpg"),
    "decrypt_key": os.path.join(PROJECT_DIR, "..", "..", "ecs-conf", "ecs_mediaserver.sec"),
    "decrypt_owner": "%(mediaserver.storage.decrypt_owner)s",
    "verify_key":  os.path.join(PROJECT_DIR, "..", "..", "ecs-conf", "ecs_authority.pub"),
    "verify_owner": "%(mediaserver.storage.verify_owner)s",
}
