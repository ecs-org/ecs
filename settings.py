# Django settings for ecs project.

import os, sys, platform, logging
from datetime import timedelta
from copy import deepcopy

# root dir of project
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) 

# standard django settings
##########################

# admins is used to send django 500, 404 and celery error messages per email, DEBUG needs to be false for this
MANAGERS = ADMINS = ()
# eg. this could be MANAGERS = ADMINS = (('Felix Erkinger', 'felix@erkinger.at'),)
SEND_BROKEN_LINK_EMAILS = True  # send 404 errors too, if DEBUG=False
MAIL_ADMINS = False

# Default is DEBUG, others may override it later
DEBUG = True

# database configuration defaults, may get overwritten in ecsdev_settings and local_settings
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'ecs',
}

# Local time zone for this installation. See http://en.wikipedia.org/wiki/List_of_tz_zones_by_name,
# although not all choices may be available on all operating systems.
TIME_ZONE = 'Europe/Vienna'

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

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# start of url matching
ROOT_URLCONF = 'ecs.urls'

# use nose for unit tests
TEST_RUNNER = 'django_nose.runner.NoseTestSuiteRunner'

# additional fixture search paths. implicitly used by every app the needs fixtures
FIXTURE_DIRS = [os.path.join(PROJECT_DIR, "fixtures")]

# cache backend, warning, this is seperate for each process, for production use memcache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

# model that gets connected to contrib.auth model
AUTH_PROFILE_MODULE = 'users.UserProfile'

# django.contrib.messages
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'

# Session Settings
SESSION_COOKIE_AGE = 28800               # logout after 8 hours of inactivity
SESSION_SAVE_EVERY_REQUEST = True        # so, every "click" on the pages resets the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   # session cookie expires at close of browser

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ptn5xj+85fvd=d4u@i1-($z*otufbvlk%x1vflb&!5k94f$i3w'

# By default dbtemplates adds the current site to the database template when
# created. The next line disables this behaviour.
#DBTEMPLATES_ADD_DEFAULT_SITE = False

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'dbtemplates.loader.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    'django.core.context_processors.csrf',
    "django.contrib.messages.context_processors.messages",
    "ecs.core.context_processors.ecs_settings",
)

MIDDLEWARE_CLASSES = (
    'ecs.utils.startup.StartupMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ecs.utils.middleware.ConsoleExceptionMiddleware',
    'ecs.utils.forceauth.ForceAuth',
    'ecs.utils.middleware.SignedCookiesMiddleware',
    'ecs.users.middleware.SingleLoginMiddleware',  # deactivate previous users sessions on login
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    'ecs.pki.middleware.ClientCertMiddleware',
    #'ecs.TestMiddleware',
    'ecs.tracking.middleware.TrackingMiddleware',
    'ecs.users.middleware.GlobalUserMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'ecs.tasks.middleware.RelatedTasksMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'ecs.utils.security.SecurityReviewMiddleware', # this middleware is not meant to be used in production
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django_extensions',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'south',
    'django_nose',
    'djcelery',
    'ecs.utils.countries',
    'compressor',
    'dbtemplates',
    'haystack',
    'reversion',

    'ecs.core',
    'ecs.checklists',
    'ecs.votes',
    'ecs.utils',
    'ecs.docstash',
    'ecs.userswitcher',
    'ecs.workflow',
    'ecs.tasks',
    'ecs.communication',
    'ecs.ecsmail',
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
)

# authenticate with email address
AUTHENTICATION_BACKENDS = ('ecs.users.backends.EmailAuthBackend',)


# ecs settings
##############

# used by ecs.utils.startup middleware: executes list on framework startup
STARTUP_CALLS = (
    'ecs.integration.startup.startup',
    'ecs.users.startup.startup',
)

# directory for generated config files
ECS_CONFIG_DIR = os.path.join(PROJECT_DIR, '..', '..', 'ecs-conf')

# used by ecs.pki
ECS_CA_ROOT = os.path.join(PROJECT_DIR, '..', '..', 'ecs-ca')

# ecs.utils.pdfutils wkhtmltopdf uses these options to steer pdf generation out of html files
WKHTMLTOPDF_OPTIONS = ['--zoom', '1.0', '--disable-smart-shrinking', '--dpi', '300'] # 

# whether ecs.tracking should store requests
ECS_TRACKING_ENABLED = False

# this is used by the EthicsCommission model to identify the system
ETHICS_COMMISSION_UUID = '23d805c6b5f14d8b9196a12005fd2961'

# users in these groups receive messages even when they are not related to studies
ECS_MEETING_AGENDA_RECEIVER_GROUPS = (u'Resident Board Member Group',)
ECS_MEETING_PROTOCOL_RECEIVER_GROUPS = (u'Meeting Protocol Receiver Group', u'Resident Board Member Group')
ECS_AMENDMENT_RECEIVER_GROUPS = (u'Amendment Receiver Group',)

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
LOGFILE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-log"))

# directory where to store zipped submission patientinformation and submission form pdfs
ECS_DOWNLOAD_CACHE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-cache"))
ECS_DOWNLOAD_CACHE_MAX_AGE = 10 #30 * 24 * 60 * 60 # 30 days

# ecs.help system export path
ECSHELP_ROOT = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-help"))

# Storage Vault settings
STORAGE_VAULT_DIR = os.path.join(PROJECT_DIR, '..', "..", 'ecs-storage-vault')
STORAGE_ENCRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-encrypt", "gpg"),
    "encrypt_key": os.path.join(PROJECT_DIR, "ecs_mediaserver.pub"),
    "encrypt_owner": "ecs_mediaserver",
    "signing_key": os.path.join(PROJECT_DIR, "ecs_authority.sec"),
    "signing_owner": "ecs_authority",
}
STORAGE_DECRYPT = {
    "gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-decrypt", "gpg"),
    "decrypt_key": os.path.join(PROJECT_DIR, "ecs_mediaserver.sec"),
    "decrypt_owner": "ecs_mediaserver",
    "verify_key":  os.path.join(PROJECT_DIR, "ecs_authority.pub"),
    "verify_owner": "ecs_authority",
}

# mail config, standard django values
EMAIL_HOST = 'localhost'; EMAIL_PORT = 25; EMAIL_HOST_USER = ""; EMAIL_HOST_PASSWORD = ""; EMAIL_USE_TLS = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEBUG_EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LIMITED_EMAIL_BACKEND = DEBUG_EMAIL_BACKEND     # used if ECSMAIL['filter_outgoing_smtp'] == True
# EMAIL_BACKEND will get overwritten on production setup (backends.smtp) and on runserver (backendss.console)

# ecsmail server settings
ECSMAIL_DEFAULT = {
    'log_dir':   LOGFILE_DIR,
    'postmaster': 'root@system.local', # the email address of the ecs user where emails from local machine to postmaster will get send
    # THIS MUST BE A VALID ecs user name !
    'listen': '0.0.0.0', 
    'port': 8823,
    'handlers': ['ecs.communication.mailreceiver'],
    'undeliverable_queue_dir': os.path.join(PROJECT_DIR, "..", "..", "ecs-mail", "undeliverable"),
    'trusted_sources': ['127.0.0.1'],
    'authoritative_domain': 'localhost',
    'filter_outgoing_smtp': False,
    # if True, only devliver_to_receipient(nofilter=True) will get send through settings.EMAIL_BACKEND, 
    # all other will be send to LIMITED_EMAIL_BACKEND if defined else DEBUG_EMAIL_BACKEND  
    # this is used only for ecs.users.views. register and request_password_reset 
}
ECSMAIL = deepcopy(ECSMAIL_DEFAULT)

# absolute URL prefix w/out trailing slash
ABSOLUTE_URL_PREFIX = "http://localhost:8000"


# if USE_TEXTBOXLIST is True then multiselect widgets will use mootools TEXBOXLIST
# set USE_TEXTBOXLIST to false (eg. in local_settings.py) e.g. for gui testing
USE_TEXTBOXLIST = True


# thirdparty settings
######################

# ### celery ### configuration defaults, uses memory transport and always eager
# production environments should:
#   set BROKER_USER, PASSWORD, VHOST 
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'ecsuser'
BROKER_PASSWORD = 'ecspassword'
BROKER_VHOST = 'ecshost'
CELERY_IMPORTS = (
    'ecs.core.tests.tasks',
    'ecs.meetings.tasks',
    'ecs.ecsmail.tasks',
    'ecs.communication.tasks',
    'ecs.integration.tasks',
    'ecs.help.tasks',
)
# try to propagate exceptions back to caller
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
# dont use queueing backend but consume it right away
CELERY_ALWAYS_EAGER = True


# ### haystack ### fulltext search engine
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(PROJECT_DIR, "..", "..", "ecs-whoosh"),

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


# settings override 
###################
#these are local fixes, they default to a sane value if unset

#ECS_USERSWITCHER = True/False
# default to True, Userswitcher will be shown so user can switch to testusers quickly 
 
#ECS_DEBUGTOOLBAR = True/False defaults to False if empty
# loads support for django-debug-toolbar

#ECS_WORDING = True/False defaults to False if empty
# activates django-rosetta 


# use ecsdev settings if on node ecsdev.ep3.at
if platform.node() == "ecsdev.ep3.at":
    from ecsdev_settings import *

# use different settings if local_settings.py exists
try: 
    from local_settings import *
except ImportError:
    pass

# load config from ecs-config/django.py
_config_file = os.path.join(ECS_CONFIG_DIR, 'django.py')
if os.path.exists(_config_file):
    execfile(_config_file)

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

# get version of the Programm from version.py if exists (gets updated on deployment)
try:
    from version import *
except ImportError:
    ECS_VERSION = 'unknown'

# user switcher
if 'ECS_USERSWITCHER' not in locals():
    ECS_USERSWITCHER = True

if not ECS_USERSWITCHER:
    MIDDLEWARE_CLASSES = tuple(item for item in MIDDLEWARE_CLASSES if item != 'ecs.userswitcher.middleware.UserSwitcherMiddleware')

# django rosetta activation
if 'ECS_WORDING' in locals() and ECS_WORDING:
    INSTALLED_APPS +=('rosetta',) # anywhere

# django-debug-toolbar activation
if 'ECS_DEBUGTOOLBAR' in locals() and ECS_DEBUGTOOLBAR:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',) # at bottom
    INSTALLED_APPS +=('debug_toolbar',) # anywhere
    DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False, 'MEDIA_URL': '/__debug__/m/',}
    INTERNAL_IPS = ('127.0.0.1','78.46.72.166', '78.46.72.189', '78.46.72.188', '78.46.72.187')

# hack some settings for test and runserver    
if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True
    ECS_REQUIRE_CLIENT_CERTS = False
    ECS_MANDATORY_CLIENT_CERTS = False
    INSTALLED_APPS += ('ecs.workflow.tests',)

if 'runserver' in sys.argv:
    EMAIL_BACKEND = DEBUG_EMAIL_BACKEND
    
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
    )

import djcelery
djcelery.setup_loader()
