'''
Created on 26.09.2010

@author: felix
'''
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
    
# on ecsdev we use memcache instead of mockcache
RENDER_MEMCACHE_LIB  = 'memcache'
RENDER_MEMCACHE_HOST = '127.0.0.1' # host= localhost, not used for mockcache
RENDER_MEMCACHE_PORT = 11211


# ecsmail server settings
# FIXME: we should only change settings but not carbon copy it from settings.py
ECSMAIL = {
    'queue_dir': os.path.join(PROJECT_DIR, "..", "..", "ecs-mail"),
    'log_dir':   os.path.join(PROJECT_DIR, "..", "..", "ecs-log"),
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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'



if user == "testecs":
    # fulltext search engine override (testecs uses solr instead of whoosh)
    HAYSTACK_SEARCH_ENGINE = "solr"
    HAYSTACK_SOLR_URL = "http://localhost:8099/solr"
    
    # testecs does not show django debug messages
    DEBUG = False
    TEMPLATE_DEBUG = False
    CELERY_SEND_TASK_ERROR_EMAILS = True # send errors of tasks via email to admins

if user == "testecs":    
    MEDIASERVER_URL = "http://test.ecsdev.ep3.at"
elif user == "shredder":
    MEDIASERVER_URL = "http://s.ecsdev.ep3.at"
    
