# Django settings for ecs project.

import os, sys, platform, logging
from datetime import timedelta

# root dir of project
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# standard django settings
##########################

# admins is used to send django 500, 404 and celery error messages per email, DEBUG needs to be false for this
MANAGERS = ADMINS = ()
MAIL_ADMINS = False

# Default is DEBUG, others may override it later
DEBUG = True

# database configuration defaults, may get overwritten in local_settings
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'ecs',
    'ATOMIC_REQUESTS': True,
}

# Local time zone for this installation. See http://en.wikipedia.org/wiki/List_of_tz_zones_by_name,
# although not all choices may be available on all operating systems.
TIME_ZONE = 'Europe/Vienna'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-AT'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# workaround: we can not use the django gettext function in the settings
# because it depends on the settings.
gettext = lambda s: s

# path where django searches for *.mo files
LOCALE_PATHS = (os.path.join(PROJECT_DIR, "locale"),)

# declare supported languages for i18n. English is the internal project language.
# We do not want to expose our internal denglish to the end-user, so disable english
# in the settings
LANGUAGES = (
    #('en', gettext('English')),
    ('de', gettext('German')),
)

# default site id, some thirdparty libraries expect it to be set
SITE_ID = 1

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# start of url matching
ROOT_URLCONF = 'ecs.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ecs.wsgi.application'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# additional fixture search paths. implicitly used by every app the needs fixtures
FIXTURE_DIRS = [os.path.join(PROJECT_DIR, "fixtures")]

# cache backend, warning, this is seperate for each process, for production use memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

# django.contrib.messages
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'

# Session Settings
SESSION_COOKIE_AGE = 28800               # logout after 8 hours of inactivity
SESSION_SAVE_EVERY_REQUEST = True        # so, every "click" on the pages resets the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   # session cookie expires at close of browser

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ptn5xj+85fvd=d4u@i1-($z*otufbvlk%x1vflb&!5k94f$i3w'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                'django.template.context_processors.csrf',
                "django.contrib.messages.context_processors.messages",
                "ecs.core.context_processors.ecs_settings",
            ]
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'ecs.utils.forceauth.ForceAuth',
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    'ecs.pki.middleware.ClientCertMiddleware',
    #'ecs.TestMiddleware',
    'ecs.tracking.middleware.TrackingMiddleware',
    'ecs.users.middleware.GlobalUserMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'ecs.tasks.middleware.RelatedTasksMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'compressor',
    'haystack',
    'reversion',
    'django_countries',
    'raven.contrib.django.raven_compat',
    'widget_tweaks',

    'ecs.core',
    'ecs.checklists',
    'ecs.votes',
    'ecs.utils',
    'ecs.docstash',
    'ecs.userswitcher',
    'ecs.workflow',
    'ecs.tasks',
    'ecs.communication',
    'ecs.dashboard',
    'ecs.bootstrap',
    'ecs.billing',
    'ecs.tracking',
    'ecs.help',
    'ecs.users',
    'ecs.documents',
    'ecs.meetings',
    'ecs.notifications',
    'ecs.authorization',
    'ecs.integration',
    'ecs.boilerplate',
    'ecs.scratchpad',
    'ecs.pki',
    'ecs.statistics',
    'ecs.tags',
)

# authenticate with email address
AUTHENTICATION_BACKENDS = ('ecs.users.backends.EmailAuthBackend',)

# Force Django to always use real files, not an InMemoryUploadedFile.
# The document processing pipeline depends on the file objects having
# a fileno().
FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django': {
            'level': 'NOTSET',
        },
        'django.db.backends': {
            # All SQL queries are logged with level DEBUG. Settings the logger
            # level to INFO prevents those messages from being propagated to
            # the root logger.
            'level': 'INFO',
        },
    },
}


# ecs settings
##############

# used by ecs.pki
ECS_CA_ROOT = os.path.join(PROJECT_DIR, '..', 'ecs-ca')

# ecs.utils.pdfutils wkhtmltopdf uses these options to steer pdf generation out of html files
WKHTMLTOPDF_OPTIONS = ['--zoom', '1.0', '--disable-smart-shrinking', '--dpi', '300'] #

# whether ecs.tracking should store requests
ECS_TRACKING_ENABLED = False

# this is used by the EthicsCommission model to identify the system
ETHICS_COMMISSION_UUID = '23d805c6b5f14d8b9196a12005fd2961'

# users in these groups receive messages even when they are not related to studies
ECS_MEETING_AGENDA_RECEIVER_GROUPS = ('Resident Board Member',)
ECS_MEETING_PROTOCOL_RECEIVER_GROUPS = ('Meeting Protocol Receiver', 'Resident Board Member')

ECS_AMG_MPG_VOTE_RECEIVERS = ('BASG.EKVoten@ages.at',)

ECS_MEETING_GRACE_PERIOD = timedelta(days=5)

# authorization
AUTHORIZATION_CONFIG = 'ecs.auth_conf'

# registration/login settings
REGISTRATION_SECRET = '!brihi7#cxrd^twvj$r=398mdp4neo$xa-rm7b!8w1jfa@7zu_'
PASSWORD_RESET_SECRET = 'j2obdvrb-hm$$x949k*f5gk_2$1x%2etxhd!$+*^qs8$4ra3=a'
LOGIN_REDIRECT_URL = '/dashboard/'

# PDF Signing settings,
# PDF_AS_SERVICE can either be undefined, or empty string, or string beginning with "mock:" to mock ecs.signature
# for real pdf-as usage use http://localhost:4780/ per default
# deployment should use something like 'https://hostname/pdf-as'
#PDFAS_SERVICE = 'http://localhost:4780/pdf-as/'
PDFAS_SERVICE = 'mock:'


# directory where to store logfiles, used by every daemon and apache
LOGFILE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "ecs-log"))

# directory where to store zipped submission patientinformation and submission form pdfs
ECS_DOWNLOAD_CACHE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "ecs-cache"))
ECS_DOWNLOAD_CACHE_MAX_AGE = 10 #30 * 24 * 60 * 60 # 30 days

# ecs.help system export path
ECSHELP_ROOT = os.path.realpath(os.path.join(PROJECT_DIR, "..", "ecs-help"))

# Storage Vault settings
STORAGE_VAULT = {
    'dir': os.path.join(PROJECT_DIR, '..', 'ecs-storage-vault'),
    'gpghome' : os.path.join(PROJECT_DIR, '..', 'ecs-gpg'),
    'encrypt_key': os.path.join(PROJECT_DIR, 'conf', 'storagevault_encrypt.pub'),
    'signing_key': os.path.join(PROJECT_DIR, 'conf', 'storagevault_sign.sec'),
    'decrypt_key': os.path.join(PROJECT_DIR, 'conf', 'storagevault_encrypt.sec'),
    'verify_key':  os.path.join(PROJECT_DIR, 'conf', 'storagevault_sign.pub'),
    'encryption_uid': 'ecs_mediaserver',
    'signature_uid': 'ecs_authority',
}

# domain to use
AUTHORITATIVE_DOMAIN= "localhost"

# absolute URL prefix w/out trailing slash
ABSOLUTE_URL_PREFIX = "http://"+ AUTHORITATIVE_DOMAIN+ ":8000"

# mail config, standard django values
EMAIL_HOST = 'localhost'; EMAIL_PORT = 25; EMAIL_HOST_USER = ""; EMAIL_HOST_PASSWORD = ""; EMAIL_USE_TLS = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEBUG_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LIMITED_EMAIL_BACKEND = DEBUG_EMAIL_BACKEND # used if ECSMAIL['filter_outgoing_smtp'] == True
# EMAIL_BACKEND will get overwritten on production setup (backends.smtp) and on runserver (backendss.console)

# ecsmail server settings
ECSMAIL = {
    'addr': ('127.0.0.1', 8823),
    'undeliverable_maildir': os.path.join(PROJECT_DIR, '..', 'ecs-undeliverable-mail'),
    'authoritative_domain': AUTHORITATIVE_DOMAIN,
    'filter_outgoing_smtp': False,
    # if True, only devliver_to_receipient(nofilter=True) will get send through settings.EMAIL_BACKEND,
    # all other will be send to LIMITED_EMAIL_BACKEND if defined else DEBUG_EMAIL_BACKEND
    # this is used only for ecs.users.views. register and request_password_reset
}


# thirdparty settings
######################

# ### celery ### configuration defaults, uses memory transport and always eager
# production environments should:
#   set BROKER_USER, PASSWORD, VHOST
BROKER_URL = 'amqp://ecsuser:ecspassword@localhost:5672/ecshost'

CELERY_IMPORTS = (
    'ecs.communication.tasks',
    'ecs.core.tests.test_tasks',
    'ecs.documents.tasks',
    'ecs.help.tasks',
    'ecs.integration.tasks',
    'ecs.meetings.tasks',
)
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = (CELERY_TASK_SERIALIZER,)
# try to propagate exceptions back to caller
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
# dont use queueing backend but consume it right away
CELERY_ALWAYS_EAGER = True


# ### haystack ### fulltext search engine
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(PROJECT_DIR, "..", "ecs-whoosh"),

        # example solr url, is only used if
        # ENGINE == 'haystack.backends.solr_backend.SolrEngine'
        'URL': 'http://localhost:8983/solr/',
    },
}


# ### django_compressor ###
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    (
        'text/x-scss',
        'pyscss -I {} -o {{outfile}} {{infile}}'.format(
            os.path.join(PROJECT_DIR, 'static', 'css'))
    ),
)

COMPRESS_DEBUG_TOGGLE = 'showmethesource' if DEBUG else 'foo'
COMPRESS_OFFLINE = False if DEBUG else True

# settings override
###################
#these are local fixes, they default to a sane value if unset

#ECS_USERSWITCHER_ENABLED = True/False
# default to True, Userswitcher will be shown so user can switch to testusers quickly

#ECS_DEBUGTOOLBAR = True/False defaults to False if empty
# loads support for django-debug-toolbar

#ECS_WORDING = True/False defaults to False if empty
# activates django-rosetta

# overwrite settings from local_settings.py if it exists
try:
    from ecs.local_settings import *
except ImportError:
    pass

# overwrite settings from environment if they exist
try:
    from ecs.env_settings import *
except ImportError:
    pass

# try to get ECS_VERSION, ECS_GIT_REV from version.py
if not all([k in locals() for k in ['ECS_VERSION', 'ECS_GIT_REV', 'ECS_GIT_BRANCH']]):
    try:
        from ecs.version import ECS_VERSION, ECS_GIT_REV, ECS_GIT_BRANCH
    except ImportError:
        ECS_VERSION = 'unknown'
        ECS_GIT_BRANCH = 'unknown'
        ECS_GIT_REV = 'badbadbadbadbadbadbadbadbadbadbadbadbad0'

# apply local overrides
local_overrides = [x[:(len('_OVERRIDE') * -1)] for x in locals().copy() if x.endswith('_OVERRIDE')]
for override in local_overrides:
    val = locals()[override]
    val_override = locals()['%s_OVERRIDE' % override]
    if hasattr(val, 'update'):
        val.update(val_override)
    else:
        val += val_override

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'noreply@%s' % (ECSMAIL['authoritative_domain'])

# TODO: get this from bootstrap_settings.py
DEFAULT_REPLY_TO   = 'ethik-kom@meduniwien.ac.at'

# https
if 'SECURE_PROXY_SSL' in locals() and SECURE_PROXY_SSL:
  CSRF_COOKIE_SECURE= True
  SESSION_COOKIE_SECURE = True
  SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# sentry/raven
if 'SENTRY_DSN' in locals():
    import raven
    from raven.transport.threaded_requests import ThreadedRequestsHTTPTransport
    # if no threading support: from raven.transport.requests import RequestsHTTPTransport
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
        'release': ECS_GIT_REV,
        'transport': ThreadedRequestsHTTPTransport,
        'site': AUTHORITATIVE_DOMAIN,
    }
    SENTRY_CLIENT = 'ecs.utils.ravenutils.DjangoClient'

# user switcher
if 'ECS_USERSWITCHER_ENABLED' not in locals():
    ECS_USERSWITCHER_ENABLED = True

if not ECS_USERSWITCHER_ENABLED:
    MIDDLEWARE_CLASSES = tuple(item for item in MIDDLEWARE_CLASSES if item != 'ecs.userswitcher.middleware.UserSwitcherMiddleware')

# django rosetta activation
if 'ECS_WORDING' in locals() and ECS_WORDING:
    INSTALLED_APPS +=('rosetta',) # anywhere

# django-debug-toolbar activation
if 'ECS_DEBUGTOOLBAR' in locals() and ECS_DEBUGTOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)
    INTERNAL_IPS = ('127.0.0.1',)

# hack some settings for test and runserver
if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True
    ECS_REQUIRE_CLIENT_CERTS = False
    INSTALLED_APPS += ('ecs.workflow.tests',)

if 'runserver' in sys.argv:
    EMAIL_BACKEND = DEBUG_EMAIL_BACKEND

    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )
