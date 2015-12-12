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
    # use queueing 
    CELERY_ALWAYS_EAGER = False

conf_dict = {
    'shredder': ('s.ecsdev.ep3.at', 8833, 'Skj45A6R2z36gVKF17i2', 'SfMS0teNT7E2yD6GVVK6JH0xwfkeykw'),
    #'testecs': ('test.ecsdev.ep3.at', 8843, 'GHz36o6OJHOm8uKmYiD1', 'dwvKMtJmRUiXeaMWGCHnEJZjD4CDEh6'),
    'chipper': ('doc.ecsdev.ep3.at', 8853, 'Edoij38So9js7SEiu982', 'ESDOFK934JSDFihsnu3w4SDOJFuihwi'),
}

if user in conf_dict.keys():
    domain, mailport, ms_key_id, ms_key_secret = conf_dict[user]

    ECSMAIL_OVERRIDE = {
        'port': mailport,
        'authoritative_domain': domain,
        'trusted_sources': ['127.0.0.1', '78.46.72.188'],
    }

    if not any(word in sys.argv for word in set(['test', 'runserver'])):
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    ABSOLUTE_URL_PREFIX = "http://{0}".format(domain)


if user in ['chipper',]:
    DEBUG = False                               # do not show django debug messages
    CELERY_SEND_TASK_ERROR_EMAILS = True        # send errors of tasks via email to admins
