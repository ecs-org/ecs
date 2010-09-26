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
