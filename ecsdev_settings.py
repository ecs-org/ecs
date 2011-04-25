# -*- coding: utf-8 -*-

import sys
# use different settings if on host ecsdev.ep3.at depending username
import getpass

user = getpass.getuser()

DBPWD_DICT = {}

if user in DBPWD_DICT:
    # django database
    DATABASES= {}
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': user, 'USER': user, 'PASSWORD': DBPWD_DICT[user],
        'HOST': '127.0.0.1', 'PORT': '',
    }
    
    # Use RabbitMQ for celery (and carrot); rabbit mq users and db users are the same (also passwords)
    BROKER_USER = user
    BROKER_PASSWORD = DBPWD_DICT[user]
    BROKER_VHOST = user
    CARROT_BACKEND = ''
    # use queueing 
    CELERY_ALWAYS_EAGER = False

conf_dict = {
    'shredder': (2, 's.ecsdev.ep3.at', 8833, 'Skj45A6R2z36gVKF17i2', 'SfMS0teNT7E2yD6GVVK6JH0xwfkeykw'),
    'testecs': (3, 'test.ecsdev.ep3.at', 8843, 'GHz36o6OJHOm8uKmYiD1', 'dwvKMtJmRUiXeaMWGCHnEJZjD4CDEh6'),
    'chipper': (4, 'doc.ecsdev.ep3.at', 8853, 'Edoij38So9js7SEiu982', 'ESDOFK934JSDFihsnu3w4SDOJFuihwi'),
}

if user in rofl.keys():
    site_id, domain, mailport, ms_key_id, ms_key_secret = conf_dict[user]

    SITE_ID = site_id
    ECSMAIL_OVERRIDE = {
        'port': mailport,
        'authoritative_domain': domain,
        'trusted_sources': ['127.0.0.1', '78.46.72.188'],
    }

    # Mediaserver Client Access (things needed to access a mediaserver, needed for both Server and Client)
    MS_CLIENT = {
        'server': 'http://{0}'.format(domain),
        'bucket': '/mediaserver/',
        'key_id': ms_key_id,
        'key_secret': ms_key_secret,
    }
    
    if not any(word in sys.argv for word in set(['test', 'runserver','runconcurrentserver', 'testmaker'])):
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

if user == 'testecs':
    # FIXME: Disabled, will use mock interface default
    # PDFAS_SERVICE = 'http://test.ecsdev.ep3.at:4780/pdf-as/'
    pass

# Mediaserver Server Access
MS_SERVER_OVERRIDE = {
    'render_memcache_lib': 'memcache',
    'render_memcache_host': '127.0.0.1',
    'render_memcache_host': 11211,
}

if user in ['testecs', 'chipper']:
    DEBUG = False                               # do not show django debug messages
    TEMPLATE_DEBUG = True                       # but sentry does show template errors
    CELERY_SEND_TASK_ERROR_EMAILS = True        # send errors of tasks via email to admins

if user == 'testecs':
    # fulltext search engine override (testecs uses solr instead of whoosh)
    HAYSTACK_SEARCH_ENGINE = 'solr'
    HAYSTACK_SOLR_URL = 'http://localhost:8099/solr'

