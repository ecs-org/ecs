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
DATABASES['sqlite'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(PROJECT_DIR, 'ecs.db'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}
DATABASES['default'] = DATABASES['sqlite']


# celery configuration defaults
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'ecsuser'
BROKER_PASSWORD = 'ecspassword'
BROKER_VHOST = 'ecshost'
# per default carrot (celery's backend) will use ghettoq for its queueing, blank this (hopefully this should work) to use RabbitMQ
CARROT_BACKEND = "ghettoq.taproot.Database"
CELERY_RESULT_BACKEND = 'database'
CELERY_IMPORTS = (
    'ecs.core.tests.task_queue',
    'ecs.core.task_queue',
)

DEFAULT_FROM_DOMAIN = 'ecsdev.ep3.at'

if platform.node() == "ecsdev.ep3.at" and user in DBPWD_DICT:
    import getpass
    user = getpass.getuser()
    # use different settings if on host ecsdev.ep3.at depending username
    DBPWD_DICT = {}

    for u in DBPWD_DICT:
        DATABASES[u] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': u,
            'USER': u,
            'PASSWORD': DBPWD_DICT[u],
            'HOST': '127.0.0.1',
            'PORT': '',
        }

    # Use Postgresql as Django Database; Database User=current user, password like in dict
    DATABASES['default'] = DATABASES[user]
    DEFAULT_FROM_EMAIL = 'noreply@%s' % (DEFAULT_FROM_DOMAIN,)
    
    # Use RabbitMQ for celery (and carrot); rabbit mq users and db users are the same (also passwords)
    BROKER_USER = user
    BROKER_PASSWORD = DBPWD_DICT[user]
    BROKER_VHOST = user
    CARROT_BACKEND = ""
    
    if user == "testecs":
        DEBUG = False
        TEMPLATE_DEBUG = False

EMAIL_HOST = 'localhost'
EMAIL_PORT = 8823

# use another different settings if local_settings.py exists
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
        DATABASES['default'] = DATABASES['local'] = local_db
    
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth"
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ecs.utils.forceauth.ForceAuth',
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
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
    'celery',
    'ecs.utils.countries',
    'compressor',

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
    'ecs.dashboard',
    'ecs.bootstrap',
)

AUTH_PROFILE_MODULE = 'core.UserProfile'

# include ghettoq in installed apps if we use it as carrot backend, so we dont need any external brocker for testing
if CARROT_BACKEND == "ghettoq.taproot.Database":
    INSTALLED_APPS += ("ghettoq", ) 

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

# memcached(b) settings
MEMCACHED_HOST = '127.0.0.1'
MEMCACHED_PORT = 11211

MEMCACHEDB_HOST = '127.0.0.1'
MEMCACHEDB_PORT = 21201

# pdf-as settings
PDFAS_SERVICE = 'http://ecsdev.ep3.at:4780/pdf-as/'
