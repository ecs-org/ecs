# Django settings for ecs project.

# root dir of project
import os.path, platform, sys
PROJECT_DIR = os.path.dirname(__file__)

# admins is used to send django 500, 404 and celery errror messages per email, DEBUG needs to be false for this
ADMINS = (
    ('Felix Erkinger', 'felix@erkinger.at'),
    )
MANAGERS = ADMINS = ()
SEND_BROKEN_LINK_EMAILS = True  # send 404 errors too, if DEBUG=False
MAIL_ADMINS = False

# Default is DEBUG, but eg. platform.node ecsdev.ep3.at user testecs overrides that
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# dont migrate in testing, this needs to be in main settings.py it doesnt work if set in utils/ecs_runner.py
SOUTH_TESTS_MIGRATE = False


# database configuration defaults, may get overwritten in platform.node()=="ecsdev.ep3.at" and local_settings.py
DATABASES = {}
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.path.join(PROJECT_DIR, 'ecs.db'),
    'USER': '',
    'PASSWORD': '',
    'HOST': '',
    'PORT': '',
}

# incoming filestore is now in root dir (one below source)
INCOMING_FILESTORE = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-incoming"))



# StorageVault settings
STORAGE_VAULT = 'ecs.utils.storagevault.LocalFileStorageVault'
STORAGE_VAULT_OPTIONS = {'LocalFileStorageVault.rootdir': os.path.join(PROJECT_DIR, '..', "..", 'ecs-storage-vault'), 'authid': 'blu', 'authkey': 'bla'}


# Mediaserver settings
#TODO Migrate mediaserver settings to a separate config file
MEDIASERVER_KEYOWNER="43BA0B84B8C6007858854B84F122070D7FB78045"
MEDIASERVER_HOST="localhost"
MEDIASERVER_PORT=8000

DOC_DISKCACHE = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-doccache"))
DOC_DISKCACHE_MAXSIZE = 2**34

RENDER_DISKCACHE = os.path.realpath(os.path.join(PROJECT_DIR, "..", "..", "ecs-rendercache"))
RENDER_DISKCACHE_MAXSIZE = 2**33

# RENDER_MEMCACHE_LIB: if set to mockcache, HOST & PORT will be ignored
# WARNING: mockcache data is only visible inside same program, so seperate runner will *NOT* see entries
RENDER_MEMCACHE_LIB  = 'mockcache'
RENDER_MEMCACHE_HOST = '127.0.0.1' # host= localhost, not used for mockcache
RENDER_MEMCACHE_PORT = 11211 # standardport of memcache, not used for mockcache
RENDER_MEMCACHE_MAXSIZE = 2**29

# Storagevault connector settings
S3_SECRET_KEYS = { "UnitTestKey": "imhappytobeatestkey", "LocalFileStorageVault": "imhappytobeasecretkey"}
S3_DEFAULT_KEY = "LocalFileStorageVault"
S3_DEFAULT_EXPIRATION_SEC = 5*60

# celery configuration defaults, uses local loopback via qhettoq and always eager
# production environments should clear CARROT_BACKEND (sets to default of rabbitmq), BROKER_USER, PASSWORD, VHOST 
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'ecsuser'
BROKER_PASSWORD = 'ecspassword'
BROKER_VHOST = 'ecshost'
# per default carrot (celery's backend) will use ghettoq for its queueing, 
# blank this (hopefully this should work) to use RabbitMQ
CARROT_BACKEND = "ghettoq.taproot.Database"
CELERY_IMPORTS = (
    'ecs.core.tests.task_queue',
    'ecs.meetings.task_queue',
    'ecs.documents.task_queue',
    'ecs.ecsmail.task_queue',
    'ecs.mediaserver.task_queue',
)
# try to propagate exceptions back to caller
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
# dont use queueing backend but consume it right away
CELERY_ALWAYS_EAGER = True


# lamson config, 
# defaults to send outgoing django mail directly to dummy smartmx (ecsmail log) and store results in maildir (ecsmail/run/queue)
# for production override LAMSON_SEND_THROUGH_RECEIVER, RECEIVER_CONFIG, RELAY_CONFIG, FROM_DOMAIN, DEFAULT_FROM_EMAIL, EMAIL_HOST, EMAIL_PORT
LAMSON_BOUNCES_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "bounces") # bounce queue 
LAMSON_UNDELIVERABLE_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "undeliverable") # undeliverable queue
LAMSON_TESTING_QUEUE = os.path.join(PROJECT_DIR, "ecsmail", "run", "queue") # queue where lamson log delivers
LAMSON_RECEIVER_CONFIG = {'listen': '0.0.0.0', 'host': '127.0.0.1', 'port': 8823} # listen here 
LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': 8825}
LAMSON_HANDLERS = ['ecs.ecsmail.app.handlers.mailreceiver']
LAMSON_ROUTER_DEFAULTS = {'host': '.+'}
LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1']
LAMSON_SEND_THROUGH_RECEIVER = False ; # this is set to True on production systems where mail should actually been routed
# used both by django AND lamson, XXX lamson and django should be on the same machine
FROM_DOMAIN = 'example.net' # outgoing/incoming mail domain name (gets overriden on host ecsdev)
DEFAULT_FROM_EMAIL = 'noreply@%s' % (FROM_DOMAIN,) # unless we have a reply path, we send with this.
if LAMSON_SEND_THROUGH_RECEIVER:
    EMAIL_HOST = LAMSON_RECEIVER_CONFIG['host'] 
    EMAIL_PORT = LAMSON_RECEIVER_CONFIG['port'] 
else:
    EMAIL_HOST = '127.0.0.1' # LAMSON_RELAY_CONFIG['host'] 
    EMAIL_PORT = 4789 #LAMSON_RELAY_CONFIG['port'] 
    
# enable the audit trail
ENABLE_AUDIT_TRAIL = True
if 'syncdb' in sys.argv or 'migrate' in sys.argv or 'test' in sys.argv:
    # there is no user root at this time, so we cant create a audit log
    ENABLE_AUDIT_TRAIL=False

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
)

if 'test' in sys.argv or 'runserver' in sys.argv:
    import random
    if not os.path.exists('ecsmail.lock'):
        _port = random.randint(30000, 60000)
        LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': _port} # smartmx dummy
        EMAIL_HOST = LAMSON_RELAY_CONFIG['host']
        EMAIL_PORT = LAMSON_RELAY_CONFIG['port']
        print "through receiver: ", LAMSON_SEND_THROUGH_RECEIVER, _port
        
# FIXME: lamson currently only sends to email addresses listed in EMAIL_WHITELST
EMAIL_WHITELIST = {}
# FIXME: Agenda, Billing is send to whitelist instead of invited people
AGENDA_RECIPIENT_LIST = ('emulbreh@googlemail.com', 'felix@erkinger.at', 'natano@natano.net',)
BILLING_RECIPIENT_LIST = AGENDA_RECIPIENT_LIST
DIFF_REVIEW_LIST = ('root',)


# fulltext search engine config
HAYSTACK_SITECONF = 'ecs.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_DIR, "whoosh_index")
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/' # example solr url, is only used if HAYSTACK_SEARCH_ENGINE = 'solr'


#XXX: these are local fixes, they default to a sane value if unset
#ECS_AUTO_PDF_BARCODE = True # default to true, skips pdftk stamping if set to false
#ECS_GHOSTSCRIPT = "absolute path to ghostscript executable" # defaults to which('gs) if empty (needs to be overriden in local_settings for eg. windows

if platform.node() == "ecsdev.ep3.at":
    # use different settings if on host ecsdev.ep3.at depending username
    import getpass
    user = getpass.getuser()
    
    DBPWD_DICT = {}
 
    # django database
    if user in DBPWD_DICT:
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': user, 'USER': user, 'PASSWORD': DBPWD_DICT[user],
            'HOST': '127.0.0.1', 'PORT': '',
        }
        
    # Use RabbitMQ for celery (and carrot); rabbit mq users and db users are the same (also passwords)
    if user in DBPWD_DICT:
        BROKER_USER = user
        BROKER_PASSWORD = DBPWD_DICT[user]
        BROKER_VHOST = user
        CARROT_BACKEND = ""
        # use queueing 
        CELERY_ALWAYS_EAGER = False
        
    # on ecsdev we use memcache instead of mockcache
    RENDER_MEMCACHE_LIB  = 'memcache'
    RENDER_MEMCACHE_HOST = '127.0.0.1' # host= localhost, not used for mockcache
    RENDER_MEMCACHE_PORT = 11211

    # lamson config different for shredder
    if user == "shredder":
        LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1', '78.46.72.188']
        LAMSON_RECEIVER_CONFIG = {'host': '0.0.0.0', 'port': 8833} # listen here 
        FROM_DOMAIN = "s.ecsdev.ep3.at"
        LAMSON_SEND_THROUGH_RECEIVER = True
    elif user == "testecs":
        LAMSON_ALLOWED_RELAY_HOSTS = ['127.0.0.1', '78.46.72.189']
        LAMSON_RECEIVER_CONFIG = {'host': '0.0.0.0', 'port': 8843} # listen here 
        FROM_DOMAIN = "test.ecsdev.ep3.at"
        LAMSON_SEND_THROUGH_RECEIVER = True

    DEFAULT_FROM_EMAIL = 'noreply@%s' % (FROM_DOMAIN,) # unless we have a reply path, we send with this.
    LAMSON_RELAY_CONFIG = {'host': '127.0.0.1', 'port': 25} # our smartmx on ecsdev.ep3.at
    EMAIL_HOST = LAMSON_RECEIVER_CONFIG['host']
    EMAIL_PORT = LAMSON_RECEIVER_CONFIG['port']
    
    if user == "testecs":
        # fulltext search engine override (testecs uses solr instead of whoosh)
        HAYSTACK_SEARCH_ENGINE = "solr"
        HAYSTACK_SOLR_URL = "http://localhost:8099/solr"
        
        # testecs does not show django debug messages
        DEBUG = False
        TEMPLATE_DEBUG = False
        CELERY_SEND_TASK_ERROR_EMAILS = True # send errors of tasks via email to admins


# use different settings if local_settings.py exists
try: 
    from local_settings import *
except ImportError:
    pass

# use different database engine settings if local_settings.py exists
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

#TODO: this should be default, but to be sure (charset related)
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"

# default site id
SITE_ID = 1

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

#TODO: what does this setting do
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
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'reversion.middleware.RevisionMiddleware',
    'ecs.utils.middleware.SignedCookiesMiddleware',
    'ecs.users.middleware.SingleLogin',    # deactivate previous users sessions on login
    'ecs.utils.forceauth.ForceAuth',
    'ecs.tracking.middleware.TrackingMiddleware',
    'ecs.userswitcher.middleware.UserSwitcherMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'ecs.workflow.middleware.WorkflowMiddleware',
    'ecs.users.middleware.GlobalUserMiddleware',
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
    #'reversion',   # clashes with south if data migrations are done

    'ecs.utils.countries',
    'ecs.utils.hashauth',
    'compressor',
    'dbtemplates',
    'haystack',

    'paging',
    'indexer',
    'sentry.client',

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
)


# start of url matching
ROOT_URLCONF = 'ecs.urls'

# debug toolbar config:
# middleware on bottom, app anywhere
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',) # at bottom
# INSTALLED_APPS +=('debug_toolbar',) # anywhere
DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
INTERNAL_IPS = ('127.0.0.1','78.46.72.166', '78.46.72.189', '78.46.72.188', '78.46.72.187')

# model that gets connected to contrib.auth model
AUTH_PROFILE_MODULE = 'users.UserProfile'

# use our ecs.utils.ecs_runner as default test runner (sets a few settings related to testing and calls standard runner)
TEST_RUNNER = 'ecs.utils.ecs_runner.EcsRunner'

# FIXME: clarify which part of the program works with this setting
FIXTURE_DIRS = [os.path.join(PROJECT_DIR, "fixtures")]

# django_compressor settings
COMPRESS = True
COMPRESS_JS_FILTERS = []

# pdf-as settings
PDFAS_SERVICE = 'http://ecsdev.ep3.at:4780/pdf-as/'

SESSION_COOKIE_AGE = 2700                # logout after 45 minutes of inactivity
SESSION_SAVE_EVERY_REQUEST = True        # so, every "click" on the pages resets the expiry time
SESSION_EXPIRE_AT_BROWSER_CLOSE = True   # session cookie expires at close of browser

# this is used by the EthicsCommission model to identiry the system
ETHICS_COMMISSION_UUID = '23d805c6b5f14d8b9196a12005fd2961'

DEFAULT_USER_GROUPS = ('Presenter',)
REGISTRATION_SECRET = '!brihi7#cxrd^twvj$r=398mdp4neo$xa-rm7b!8w1jfa@7zu_'
PASSWORD_RESET_SECRET = 'j2obdvrb-hm$$x949k*f5gk_2$1x%2etxhd!$+*^qs8$4ra3=a'
LOGIN_REDIRECT_URL = '/dashboard/'

# authorization
AUTHORIZATION_CONFIG = 'ecs.auth_conf'

# django.contrib.messages
MESSAGE_STORE = 'django.contrib.messages.storage.session.SessionStorage'

# django-sentry
SENTRY_TESTING = True # log exceptions even when DEBUG=False
SENTRY_KEY = 'okdzo74fungotd9t89ec1ffi0f56bmvwlgd'
SENTRY_REMOTE_URL = "http://127.0.0.1:8090/store/"
SENTRY_REMOTE_TIMEOUT = 3

if 'test' in sys.argv or 'runserver' in sys.argv:
    import subprocess, atexit
    if not os.path.exists('ecsmail.lock'):
        with open('ecsmail.lock', 'w'):
            # xxx: sys.executable should work in most environments (if you want python, you probably get python with it)
            cmd = [os.path.normpath(sys.executable), sys.argv[0], 'ecsmail', 'log', str(_port)] 
            # let the log server listen on smartmx dummy
            print ' '.join(cmd)
            ecsmail = subprocess.Popen(cmd)
            def cleanup():
                ecsmail.terminate()
                os.remove('ecsmail.lock')
            atexit.register(cleanup)
        
