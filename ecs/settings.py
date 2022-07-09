# Django settings for ecs project.

import os, sys, platform, logging
from datetime import timedelta
from urllib.parse import urlparse

# root dir of project
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# standard django settings
##########################

# Default is DEBUG, others may override it later
DEBUG = True

# database configuration defaults, may get overwritten in local_settings
DATABASES = {}
if os.getenv('DATABASE_URL'):
    url = urlparse(os.getenv('DATABASE_URL'))
    DATABASES['default'] = {
        'NAME': url.path[1:] or '',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': url.username,
        'PASSWORD': url.password,
        'HOST': url.hostname or '',
        'PORT': url.port or '5432',
        'ATOMIC_REQUESTS': True
    }
else:
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
if os.getenv('MEMCACHED_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
            'LOCATION': os.getenv('MEMCACHED_URL').split('//')[1],
        }
    }
else:
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

    'compressor',
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
# if set to true:  users of internal groups need a client certificate to logon
# ECS_REQUIRE_CLIENT_CERTS = false  # default

# this is used by the EthicsCommission model to identify the system
ETHICS_COMMISSION_UUID = 'ecececececececececececececececec'

# users in these groups receive messages even when they are not related to studies
ECS_MEETING_AGENDA_RECEIVER_GROUPS = (
    'Resident Board Member', 'Omniscient Board Member',
)
ECS_MEETING_PROTOCOL_RECEIVER_GROUPS = (
    'Meeting Protocol Receiver', 'Resident Board Member',
    'Omniscient Board Member',
)

ECS_AMG_MPG_VOTE_RECEIVERS = ('BASG.EKVoten@ages.at',)

ECS_MEETING_GRACE_PERIOD = timedelta(days=5)

# authorization
AUTHORIZATION_CONFIG = 'ecs.auth_conf'

# registration/login settings
REGISTRATION_SECRET = '!brihi7#cxrd^twvj$r=398mdp4neo$xa-rm7b!8w1jfa@7zu_'
PASSWORD_RESET_SECRET = 'j2obdvrb-hm$$x949k*f5gk_2$1x%2etxhd!$+*^qs8$4ra3=a'
LOGIN_REDIRECT_URL = '/dashboard/'

# PDF Signing will use fake signing if PDFAS_SERVICE is "mock:"
# deployment should use 'https://hostname/pdf-as-web/'
PDFAS_SERVICE = 'mock:'

# directory where to store zipped submission patientinformation and submission form pdfs
ECS_DOWNLOAD_CACHE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "ecs-cache"))
ECS_DOWNLOAD_CACHE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days

# Storage Vault settings
STORAGE_VAULT = {
    'dir': os.path.join(PROJECT_DIR, '..', 'ecs-storage-vault'),
    'gpghome' : os.path.join(PROJECT_DIR, '..', 'ecs-gpg'),
    'encryption_uid': 'ecs_mediaserver',
    'signature_uid': 'ecs_authority',
}

# domain to use
DOMAIN= "localhost"

# absolute URL prefix w/out trailing slash
ABSOLUTE_URL_PREFIX = "http://"+ DOMAIN+ ":8000"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND_UNFILTERED = 'django.core.mail.backends.console.EmailBackend'
EMAIL_UNFILTERED_DOMAINS = ()  # = ('example.com', )
EMAIL_UNFILTERED_INDIVIDUALS = ()  # = ('ada@example.org', 'tom@example.com')

# EMAIL_BACKEND_UNFILTERED will be used for
#  User registration & invitation, password reset, send client certificate,
#  and all mails to domains in EMAIL_UNFILTERED_DOMAINS and user
#  listed in EMAIL_UNFILTERED_INDIVIDUALS

if os.getenv('SMTP_URL'):
    url = urlparse(os.getenv('SMTP_URL'))
    EMAIL_HOST = url.hostname
    EMAIL_PORT = url.port or 25
    EMAIL_HOST_USER = url.username or ''
    EMAIL_HOST_PASSWORD = url.password or ''

SMTPD_CONFIG = {
    'listen_addr': ('127.0.0.1', 8025),
    'domain': DOMAIN,
    'store_exceptions': False,
}


# thirdparty settings
######################

# ### celery ### default uses memory transport and always eager

CELERY_IMPORTS = (
    'ecs.communication.tasks',
    'ecs.core.tasks',
    'ecs.core.tests.test_tasks',
    'ecs.documents.tasks',
    'ecs.integration.tasks',
    'ecs.meetings.tasks',
    'ecs.tasks.tasks',
    'ecs.users.tasks',
    'ecs.votes.tasks',
)
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = (CELERY_TASK_SERIALIZER,)
# try to propagate exceptions back to caller
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

if os.getenv('REDIS_URL'):
    BROKER_URL = os.getenv('REDIS_URL')
    BROKER_TRANSPORT_OPTIONS = {
        'fanout_prefix': True,
        'fanout_patterns': True
    }
    CELERY_RESULT_BACKEND = BROKER_URL
    CELERY_ALWAYS_EAGER = False
else:
    # dont use queueing backend but consume it right away
    CELERY_ALWAYS_EAGER = True


# ### django_compressor ###
COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    (
        'text/x-scss',
        'pyscss -I {} -o {{outfile}} {{infile}}'.format(
            os.path.join(STATIC_ROOT, 'css'))
    ),
)


# settings override
###################
#these are local fixes, they default to a sane value if unset

#ECS_USERSWITCHER_ENABLED = True/False
# default to True, Userswitcher will be shown so user can switch to testusers quickly
if os.getenv('ECS_USERSWITCHER_ENABLED'):
    ECS_USERSWITCHER_ENABLED = os.getenv('ECS_USERSWITCHER_ENABLED','').lower() == 'true'

#ECS_DEBUGTOOLBAR = True/False defaults to False if empty
# loads support for django-debug-toolbar

#ECS_WORDING = True/False defaults to False if empty
# activates django-rosetta

# import and execute ECS_SETTINGS from environment as python code if they exist
if os.getenv('ECS_SETTINGS'):
    exec(os.getenv('ECS_SETTINGS'))

# overwrite settings from local_settings.py if it exists
try:
    from ecs.local_settings import *
except ImportError:
    pass

# try to get ECS_VERSION, ECS_GIT_REV from version.py
if not all([k in locals() for k in ['ECS_VERSION', 'ECS_GIT_REV', 'ECS_GIT_BRANCH']]):
    try:
        from ecs.version import ECS_VERSION, ECS_GIT_REV, ECS_GIT_BRANCH, ECS_CHANGED
    except ImportError:
        ECS_VERSION = 'unknown'
        ECS_GIT_BRANCH = 'unknown'
        ECS_GIT_REV = 'badbadbadbadbadbadbadbadbadbadbadbadbad0'
        ECS_CHANGED = 'unknown'

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'noreply@{}'.format(DOMAIN)

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
        'site': DOMAIN,
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
    INSTALLED_APPS += ('ecs.workflow.tests',)

if 'runserver' in sys.argv:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )
