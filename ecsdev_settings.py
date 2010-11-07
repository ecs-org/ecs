# -*- coding: utf-8 -*-

import os
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
    CARROT_BACKEND = ""
    # use queueing 
    CELERY_ALWAYS_EAGER = False

# change urls of signing application depending username
if user == "shredder":
    PDFAS_SERVICE = 'http://s.ecsdev.ep3.at:4780/pdf-as/'
elif user == "testecs":
    PDFAS_SERVICE = 'http://test.ecsdev.ep3.at:4780/pdf-as/'
    
    
# ecsmail server settings
# FIXME: we should only change settings but not carbon copy it from settings.py
ECSMAIL = {
    'queue_dir': os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ecs-mail"),
    'log_dir':   os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ecs-log"),
    'postmaster': 'root', # ecs user where emails from local machine to postmaster will get send, THIS MUST BE A VALID ecs user name !
    'listen': '0.0.0.0', 
    'port': 8823,
    'handlers': ['ecs.communication.mailreceiver'],
    'trusted_sources': ['127.0.0.1'],
    'authoritative_domain': 'ecsdev.ep3.at',
    }

if user == "shredder":
    ECSMAIL ['port']= 8833
    ECSMAIL ['authoritative_domain']= 's.ecsdev.ep3.at'
    ECSMAIL ['trusted_sources'] = ['127.0.0.1', '78.46.72.188']
elif user == "testecs":
    ECSMAIL ['port']= 8843
    ECSMAIL ['authoritative_domain']= 'test.ecsdev.ep3.at'
    ECSMAIL ['trusted_sources'] = ['127.0.0.1', '78.46.72.189']

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'noreply@%s' % (ECSMAIL ['authoritative_domain']) 
if user in ["shredder", "testecs"]:
    # FIXME: this should only apply if sysargv not test or runserver
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'




# Mediaserver Client Access (things needed to access a mediaserver, needed for both Server and Client)
if user == "testecs":    
    MS_CLIENT ["url"] = "http://test.ecsdev.ep3.at"
    MS_CLIENT ["key_id"] = "GHz36o6OJHOm8uKmYiD1"
    MS_CLIENT ["key_secret"] = "dwvKMtJmRUiXeaMWGCHnEJZjD4CDEh6"
elif user == "shredder":
    MS_CLIENT ["url"] = "http://s.ecsdev.ep3.at"
    MS_CLIENT ["key_id"] = "Skj45A6R2z36gVKF17i2"
    MS_CLIENT ["key_secret"] = "SfMS0teNT7E2yD6GVVK6JH0xwfkeykw"

# on ecsdev we use memcache instead of mockcache
MS_SERVER ["render_memcache_lib"] = 'memcache'
MS_SERVER ["render_memcache_host"] = '127.0.0.1'
MS_SERVER ["render_memcache_host"] = 11211


if user == "testecs":
    # fulltext search engine override (testecs uses solr instead of whoosh)
    HAYSTACK_SEARCH_ENGINE = "solr"
    HAYSTACK_SOLR_URL = "http://localhost:8099/solr"
    
    # testecs does not show django debug messages
    DEBUG = False
    TEMPLATE_DEBUG = False
    CELERY_SEND_TASK_ERROR_EMAILS = True # send errors of tasks via email to admins

