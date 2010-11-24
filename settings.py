# Django settings for ecs project.

import os.path, platform, sys
from django.core.exceptions import ImproperlyConfigured
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
TEMPLATE_DEBUG = DEBUG

# database configuration defaults, may get overwritten in ecsdev_settings and local_settings
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(PROJECT_DIR, 'ecs.db'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}

# Local time zone for this installation. See http://en.wikipedia.org/wiki/List_of_tz_zones_by_name,
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your system time zone.
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

# declare supported languages for i18n. English is the internal project language.
# We do not want to expose our internal denglish to the end-user, so disable english
# in the settings
LANGUAGES = (
    #('en', gettext('English')),
    ('de', gettext('German')),
)

#this should be default, but to be sure (charset related)
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

# default site id, some thirdparty libraries expect it to be set
SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# start of url matching
ROOT_URLCONF = 'ecs.urls'

# use our ecs.utils.ecs_runner as default test runner 
TEST_RUNNER = 'ecs.utils.ecs_runner.EcsRunner'

# additional fixture search paths. implicitly used by every app the needs fixtures
FIXTURE_DIRS = [os.path.join(PROJECT_DIR, "fixtures")]

# model that gets connected to contrib.auth model
AUTH_PROFILE_MODULE = 'users.UserProfile'

# django.contrib.messages
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'

# Session Settings
SESSION_COOKIE_AGE = 2700                # logout after 45 minutes of inactivity
SESSION_SAVE_EVERY_REQUEST = True        # so, every "click" on the pages resets the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   # session cookie expires at close of browser

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ptn5xj+85fvd=d4u@i1-($z*otufbvlk%x1vflb&!5k94f$i3w'

# dbtemplates adds the current site (settings.SITE_ID) to the database template when it is created by default. You can disable this feature by setting DBTEMPLATES_ADD_DEFAULT_SITE to False.
#DBTEMPLATES_ADD_DEFAULT_SITE = False

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'dbtemplates.loader.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "ecs.core.context_processors.ecs_settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ecs.utils.forceauth.ForceAuth',
    'ecs.utils.middleware.SignedCookiesMiddleware',
    'ecs.users.middleware.SingleLoginMiddleware',  # deactivate previous users sessions on login
    'ecs.tracking.middleware.TrackingMiddleware',
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    'ecs.users.middleware.GlobalUserMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'ghettoq', 

    'ecs.utils.countries',
    'compressor',
    'dbtemplates',
    'haystack',

    'paging',
    'indexer',
    'sentry',
    'sentry.client',

    'ecs.core',
    'ecs.utils',
    'ecs.feedback',
    'ecs.docstash',
    'ecs.userswitcher',
    'ecs.pdfviewer',
    'ecs.mediaserver',
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
    'ecs.audit',
    'ecs.notifications',
    'ecs.authorization',
    'ecs.integration',
    'ecs.fastlane',
    'ecs.boilerplate',
)



# ecs settings
##############

# this is used by the EthicsCommission model to identify the system
ETHICS_COMMISSION_UUID = '23d805c6b5f14d8b9196a12005fd2961'

# authorization
AUTHORIZATION_CONFIG = 'ecs.auth_conf'

# registration/login settings
DEFAULT_USER_GROUPS = ('Presenter',)
REGISTRATION_SECRET = '!brihi7#cxrd^twvj$r=398mdp4neo$xa-rm7b!8w1jfa@7zu_'
PASSWORD_RESET_SECRET = 'j2obdvrb-hm$$x949k*f5gk_2$1x%2etxhd!$+*^qs8$4ra3=a'
LOGIN_REDIRECT_URL = '/dashboard/'

# PDF Signing settings, use port 4780 per default (as stated in source:/signing/readme.txt)
PDFAS_SERVICE = 'http://localhost:4780/pdf-as/'


# directory where to store logfiles, used by every daemon and apache
LOGFILE_DIR = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-log"))


# incoming filestore of user uploaded documents 
INCOMING_FILESTORE = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-incoming"))


# Storage Vault settings
STORAGE_VAULT = 'ecs.utils.storagevault.LocalFileStorageVault'
STORAGE_VAULT_OPTIONS = {'LocalFileStorageVault.rootdir':
     os.path.join(PROJECT_DIR, '..', "..", 'ecs-storage-vault'), 'authid': 'blu', 'authkey': 'bla'}
STORAGE_ENCRYPT = {"gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-encrypt", "gpg"),
                   "key": os.path.join(PROJECT_DIR, "..", "sys", "encryptkey.asc"),
                   "owner": "mediaserver",
                   }
STORAGE_DECRYPT = {"gpghome" : os.path.join(PROJECT_DIR, "..", "..", "ecs-decrypt", "gpg"),
                   "key": os.path.join(PROJECT_DIR, "..", "sys", "decryptkey.asc"),
                   "owner": "mediaserver",
                   }
# Mediaserver Shared Settings
MS_SHARED = {"url_expiration_sec": 6*60*60, "tiles": [1, 3, 5], "resolutions": [800, 768],
             "aspect_ratio": 1.41428, "dpi": 96, "depth": 8}

# Mediaserver Client Access (things needed to access a mediaserver, needed for both Server and Client)
MS_CLIENT = {"server": "http://localhost:8000", "bucket": "/mediaserver/",
    # key_id: 20 char long, key_secret: 31 chars, A-Za-z0-9
    "key_id": "b2SpFfUvfD44LUzHDu7w", "key_secret": "SksXrbHMQyTBAKdb9NNeqOFu8TSwxXN" }
               
# Mediaserver Server Config (things needed for a mediaserver to serve)
MS_SERVER = {
    "doc_diskcache": os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-doccache")),
    "doc_diskcache_maxsize" : 2**34,
    "render_diskcache":  os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-rendercache")),
    "render_diskcache_maxsize": 2**33,
    "render_memcache_lib": "mockcache",     # if set to mockcache, HOST & PORT will be ignored
    "render_memcache_host": "127.0.0.1",    # host= localhost, 
    "render_memcache_port": 11211,          # standardport of memcache, not used for mockcache
    "render_memcache_maxsize": 2**29,
    # WARNING: mockcache data is only visible inside same program, so seperate runner will *NOT* see entries
    }


# mail config, standard django values
EMAIL_HOST = 'localhost'; EMAIL_PORT = 25; EMAIL_HOST_USER = ""; EMAIL_HOST_PASSWORD = ""; EMAIL_USE_TLS = False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
# EMAIL_BACKEND will get overwritten on production setup (backends.smtp) and on runserver (backendss.console)

# ecsmail server settings
ECSMAIL_DEFAULT = {
    'queue_dir': os.path.join(PROJECT_DIR, "..", "..", "ecs-mail"),
    'log_dir':   LOGFILE_DIR,
    'postmaster': 'root', # ecs user where emails from local machine to postmaster will get send, THIS MUST BE A VALID ecs user name !
    'listen': '0.0.0.0', 
    'port': 8823,
    'handlers': ['ecs.communication.mailreceiver'],
    'trusted_sources': ['127.0.0.1'],
    'authoritative_domain': 'localhost',
    }
ECSMAIL = deepcopy(ECSMAIL_DEFAULT)

# FIXME: we currently only sends to email addresses listed in EMAIL_WHITELST (FMD2)
EMAIL_WHITELIST = {}
# FIXME: Agenda, Billing is send to whitelist instead of invited people (FMD2)
AGENDA_RECIPIENT_LIST = ('emulbreh@googlemail.com', 'felix@erkinger.at', 'natano@natano.net', 'amir@viel-zu.org',)
BILLING_RECIPIENT_LIST = AGENDA_RECIPIENT_LIST
DIFF_REVIEW_LIST = ('root',)


# enable the audit trail
ENABLE_AUDIT_TRAIL = True
if 'syncdb' in sys.argv or 'migrate' in sys.argv or 'test' in sys.argv:
    # there is no user root at this time, so we cant create a audit log
    ENABLE_AUDIT_TRAIL = False

AUDIT_TRAIL_IGNORED_MODELS = (  # changes on these models are not logged
    'django.contrib.sessions.models.Session',
    'django.contrib.contenttypes.models.ContentType',
    'django.contrib.sites.models.Site',
    'django.contrib.admin.models.LogEntry',
    
    'south.models.*',
    'djcelery.models.*',
    'ghettoq.models.*',
    
    'ecs.utils.countries.models.*',
    'ecs.tracking.models.*',
    'ecs.workflow.models.*',
    'ecs.docstash.models.*',
    'ecs.pdfviewer.models.*',
    'ecs.feedback.models.*',
    'ecs.users.models.UserSettings',
)


# ecs.feedback tracrpc settings
FEEDBACK_CONFIG = {}
# thirdparty settings
######################

# ### South ### dont migrate in testing, this needs to be in main settings.py it doesnt work if set in utils/ecs_runner.py
SOUTH_TESTS_MIGRATE = False


# ### celery ### configuration defaults, uses local loopback via qhettoq and always eager
# production environments should clear CARROT_BACKEND (sets to default of rabbitmq), set BROKER_USER, PASSWORD, VHOST 
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'ecsuser'
BROKER_PASSWORD = 'ecspassword'
BROKER_VHOST = 'ecshost'
CARROT_BACKEND = "ghettoq.taproot.Database"
CELERY_IMPORTS = (
    'ecs.core.task_queue',
    'ecs.core.tests.tasks',
    'ecs.meetings.tasks',
    'ecs.documents.tasks',
    'ecs.mediaserver.tasks', # TODO: this should be switchable in case we only want to be a mediaserver or coreapp (FMD2)
    'ecs.ecsmail.tasks',
    'ecs.workflow.tasks',
    'ecs.communication.tasks',
    'ecs.integration.tasks',
)                 
# try to propagate exceptions back to caller
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
# dont use queueing backend but consume it right away
CELERY_ALWAYS_EAGER = True


# ### haystack ### fulltext search engine
HAYSTACK_SITECONF = 'ecs.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_DIR, "whoosh_index")
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/' # example solr url, is only used if HAYSTACK_SEARCH_ENGINE = 'solr'


# ### django_compressor ### 
COMPRESS = True
COMPRESS_JS_FILTERS = []


# ### django-sentry ###
SENTRY_TESTING = True # log exceptions when DEBUG=True

USE_TEXTBOXLIST = True

# settings override 
###################

#these are local fixes, they default to a sane value if unset
#ECS_GHOSTSCRIPT = "absolute path to ghostscript executable" # defaults to which('gs') if empty 
# needs to be overriden in local_settings for eg. windows
#ECS_GNUPG = "absolute path to gpg executable" # defaults to which('gpg') if empty
# needs to be overriden in local_settings for eg. windows 


# use ecsdev settings if on node ecsdev.ep3.at
if platform.node() == "ecsdev.ep3.at":
    from ecsdev_settings import *


# use different settings if local_settings.py exists
try: 
    from local_settings import *
except ImportError:
    pass

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

# get version of the Programm from version.py if exists (gets updated on deployment)
try:
    from version import *
except ImportError:
    ECS_VERSION = 'unknown'

# debug toolbar config:
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',) # at bottom
# INSTALLED_APPS +=('debug_toolbar',) # anywhere
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
INTERNAL_IPS = ('127.0.0.1','78.46.72.166', '78.46.72.189', '78.46.72.188', '78.46.72.187')
   
# hack some settings for test and runserver    
if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True
elif 'runserver' in sys.argv:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

import djcelery
djcelery.setup_loader()

