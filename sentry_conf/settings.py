import os.path, platform, sys

PROJECT_DIR = os.path.dirname(__file__)

MANAGERS = ADMINS = ()
MAIL_ADMINS = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': dict(
        ENGINE = 'django.db.backends.sqlite3',
        NAME = os.path.join(PROJECT_DIR, 'ecs_sentry.db'),
    ),
}

TIME_ZONE = 'Europe/Vienna'
LANGUAGE_CODE = 'de-AT'
DEFAULT_CHARSET = "utf-8"
FILE_CHARSET = "utf-8"
USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = '9!c$o8phpnow_v@*q@%ar_ax&#pngn-xbdx0fhlau+$foa$qv-'
SENTRY_KEY = 'okdzo74fungotd9t89ec1ffi0f56bmvwlgd'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'sentry',
    'sentry.client',
    'paging',
    'indexer',
)

ROOT_URLCONF = 'sentry.urls'
