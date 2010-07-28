# Django settings for ecs project.

import os.path, platform
PROJECT_DIR = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# Default is DEBUG, but eg. platform.node ecsdev.ep3.at user testecs overrides that
# (because we want 404 and 500 custom errors and log the error)
DEBUG = True
TEMPLATE_DEBUG = DEBUG


# database configuration defaults, may get overwritten in platform.node()=="ecsdev.ep3.at" and local_settings.py
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(PROJECT_DIR, 'ecs.db'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}


# mediaserver memcached(b) settings, RENDERSTORAGE_LIB can either be "memcache" or "mockcache" (and defaults to mockcache if empty)
# if set to mockcache, RENDERSTORAGE_HOST & PORT will be ignored
# warning mockcache data is only visible inside same program, so seperate runner will NOT see entries
RENDERSTORAGE_LIB  = 'mockcache'
RENDERSTORAGE_HOST = '127.0.0.1'
RENDERSTORAGE_PORT = 21201 # port of memcachedb


# celery configuration defaults
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'ecsuser'
BROKER_PASSWORD = 'ecspassword'
BROKER_VHOST = 'ecshost'
# per default carrot (celery's backend) will use ghettoq for its queueing, blank this (hopefully this should work) to use RabbitMQ
CARROT_BACKEND = "ghettoq.taproot.Database"
# Celery results
CELERY_RESULT_BACKEND = 'database'
#CELERY_RESULT_DBURI = 'sqlite://'+ os.path.join(PROJECT_DIR, 'celery.db')

CELERY_IMPORTS = (
    'ecs.core.tests.task_queue',
    'ecs.core.task_queue',
    'ecs.ecsmail.task_queue',
    'ecs.mediaserver.task_queue',
)

# From http://github.com/ask/django-celery#readme
# Special note for mod_wsgi users: If you're using mod_wsgi to deploy your Django application you need to include the following in your .wsgi module:
import os
os.environ["CELERY_LOADER"] = "django"
import djcelery
djcelery.setup_loader()


# lamson config
LAMSON_BOUNCES_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "bounces") # bounce queue 
LAMSON_UNDELIVERABLE_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "undeliverable") # undeliverable queue
LAMSON_TESTING_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "queue") # queue where lamson log delivers
LAMSON_RECEIVER_CONFIG = {'host': '0.0.0.0', 'port': 8823} # listen here 
LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': 8825} # relay to
LAMSON_HANDLERS = ['ecs.ecsmail.app.handlers.mailreceiver']
LAMSON_ROUTER_DEFAULTS = {'host': '.+'}
LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1']

# used both by django AND lamson
# lamson and django should be on the same machine
FROM_DOMAIN = 'example.net' # outgoing/incoming mail domain name (gets overriden on host ecsdev)
DEFAULT_FROM_EMAIL = 'noreply@%s' % (FROM_DOMAIN,) # unless we have a reply path, we send with this.
EMAIL_HOST = LAMSON_RELAY_CONFIG['host'] 
EMAIL_PORT = LAMSON_RELAY_CONFIG['port'] 
# FIXME: lamson currently only sends to email addresses listed in EMAIL_WHITELST
EMAIL_WHITELIST = {}
# FIXME: Agenda is send to whitelist instead of invited people
AGENDA_RECIPIENT_LIST = ('emulbreh@googlemail.com', 'felix@erkinger.at', 'natano@natano.net',)
BILLING_RECIPIENT_LIST = AGENDA_RECIPIENT_LIST


# fulltext search engine config
HAYSTACK_SITECONF = 'ecs.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_DIR, "whoosh_index")
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/' # example solr url

if platform.node() == "ecsdev.ep3.at":
    import getpass
    user = getpass.getuser()
    # use different settings if on host ecsdev.ep3.at depending username
    
    DBPWD_DICT = {}
 
    # django database
    if user in DBPWD_DICT:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': user,
            'USER': user,
            'PASSWORD': DBPWD_DICT[user],
            'HOST': '127.0.0.1',
            'PORT': '',
        }
        
    # Use RabbitMQ for celery (and carrot); rabbit mq users and db users are the same (also passwords)
    BROKER_USER = user
    if user in DBPWD_DICT:
        BROKER_PASSWORD = DBPWD_DICT[user]
    BROKER_VHOST = user
    CARROT_BACKEND = ""

    # on ecsdev we use memcachedb instead of mockcache
    RENDERSTORAGE_LIB  = 'memcache'
    RENDERSTORAGE_HOST = '127.0.0.1'
    RENDERSTORAGE_PORT = 21201 # port of memcachedb

    # lamson config different for shredder
    if user == "shredder":
        LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1', '78.46.72.188']
        LAMSON_RECEIVER_CONFIG = {'host': '78.46.72.188', 'port': 8833} # listen here 
        FROM_DOMAIN = "s.ecsdev.ep3.at"
    elif user == "testecs":
        LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1', '78.46.72.189']
        LAMSON_RECEIVER_CONFIG = {'host': '78.46.72.189', 'port': 8843} # listen here 
        FROM_DOMAIN = "test.ecsdev.ep3.at"

    DEFAULT_FROM_EMAIL = 'noreply@%s' % (FROM_DOMAIN,) # unless we have a reply path, we send with this.
    LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': 25} # our smartmx on ecsdev.ep3.at
    EMAIL_HOST = LAMSON_RELAY_CONFIG['host']
    EMAIL_PORT = LAMSON_RELAY_CONFIG['port']

    # fulltext search engine override (ecsdev uses solr instead of whoosh)
    HAYSTACK_SEARCH_ENGINE = "solr"
    HAYSTACK_SOLR_URL = "http://localhost:8099/solr"
    
    # testecs does not show django debug messages
    if user == "testecs":
        DEBUG = False
        TEMPLATE_DEBUG = False


# use different settings if local_settings.py exists
try:
    from local_settings import *
except ImportError:
    pass

try:
    import local_settings
    local_db = {}
    
    if hasattr(local_settings, 'DATABASE_ENGINE'):
        local_db['ENGINE'] = 'django.db.backends.%s' % local_settings.DATABASE_ENGINE

    for key in ('NAME', 'USER', 'PASSWORD', 'HOST', 'PORT'):
        if hasattr(local_settings, 'DATABASE_%s' % key):
            local_db[key] = getattr(local_settings, 'DATABASE_%s' % key)
    
    if hasattr(local_settings, 'local_db'):
        local_db = local_settings.local_db
    
    if local_db:
        DATABASES['default'] = local_db
    
except ImportError:
    pass


# get version of the Programm from version.py if exists (gets updated on deployment)
try:
    from version import *
except ImportError:
    ECS_VERSION = 'unknown'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Vienna'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-AT'

# this should be default, but to be sure
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ptn5xj+85fvd=d4u@i1-($z*otufbvlk%x1vflb&!5k94f$i3w'

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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ecs.utils.middleware.SignedCookiesMiddleware',
    'ecs.core.middleware.SingleLogin',    # deactivate previous user sessions on login
    'ecs.utils.forceauth.ForceAuth',
    'ecs.tracking.middleware.TrackingMiddleware',
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    #'djangodblog.middleware.DBLogMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'ecs.workflow.middleware.WorkflowMiddleware',
)   

# debug toolbar config:
# middleware on bottom:
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
# application anyware:
#    'debug_toolbar',
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
INTERNAL_IPS = ('127.0.0.1','78.46.72.166', '78.46.72.189', '78.46.72.188', '78.46.72.187')

ROOT_URLCONF = 'ecs.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django_extensions',

    'django.contrib.admin',
    'django.contrib.admindocs',

    'south',
    'django_nose',
    'djangodblog',
    'djcelery',
    'ghettoq', 
    # include ghettoq in installed apps if we use it as carrot backend, so we dont need any external brocker for testing
    #if CARROT_BACKEND == "ghettoq.taproot.Database":
    #    INSTALLED_APPS += ("ghettoq", ) 

    'ecs.utils.countries',
    'ecs.utils.hashauth',
    'compressor',
    'dbtemplates',
    'haystack',

    'ecs.core',
    'ecs.utils',
    'ecs.feedback',
    'ecs.docstash',
    'ecs.userswitcher',
    'ecs.pdfsigner',
    'ecs.pdfviewer',
    'ecs.mediaserver',
    'ecs.workflow',
    'ecs.tasks',
    'ecs.messages',
    'ecs.ecsmail',
    'ecs.dashboard',
    'ecs.bootstrap',
    'ecs.billing',
    'ecs.tracking',
    #'ecs.help',
)

# model that gets connected to contrib.auth model
AUTH_PROFILE_MODULE = 'core.UserProfile'

# django-db-log
# temporary for testing, catch 404 defaults to false
DBLOG_CATCH_404_ERRORS = True

# filestore is now in root dir (one below source)
FILESTORE = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-store"))

# use our ecs.utils.ecs_runner as default test runner
TEST_RUNNER = 'ecs.utils.ecs_runner.EcsRunner'
SOUTH_TESTS_MIGRATE = False

# FIXME: clarify which part of the program works with this setting
FIXTURE_DIRS = [os.path.join(PROJECT_DIR, "fixtures")]

# django_compressor settings
COMPRESS = True
COMPRESS_JS_FILTERS = []

#ECS_AUTO_PDF_BARCODE = True # default

# pdf-as settings
PDFAS_SERVICE = 'http://ecsdev.ep3.at:4780/pdf-as/'

SESSION_COOKIE_AGE = 1800                # logout after 30 minutes of inactivity
SESSION_SAVE_EVERY_REQUEST = True        # so, every "click" on the pages resets the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# FIXME: describe where and how this is used; remeber, settings.py needs documentation on every settings
ETHICS_COMMISSION_UUID = '23d805c6b5f14d8b9196a12005fd2961'
