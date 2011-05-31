# ecs main application environment setup
import os
import subprocess

from uuid import uuid4
from fabric.api import local, env
from deployment.utils import install_upstart, apache_setup, write_template
from deployment.targetsupport import SetupTargetObject


class SetupTarget(SetupTargetObject):
    """ SetupTarget(use_sudo=True, dry=False, hostname=None, ip=None) """ 
    def __init__(self, *args, **kwargs):
        # FIXME: some of SetupApplication methods dont honor dry=True
        super(SetupTarget, self).__init__(*args, **kwargs)
        self.appname = 'ecs'
        self.queuing_password = uuid4().get_hex()

    def help(self, *args, **kwargs):
        print('''%s targets

targets:
  
  * update
    usage: fab target:%s,update,*commands,**kwargs
    
    commands:
      * homedir_config
      * sslcert_config
      * many others (unfinished)
        ''' % (self.appname, self.appname))
    
    def update(self, *args, **kwargs):
        pass
    
    def system_setup(self, *args, **kwargs):
        self.homedir_config()
        self.sslcert_config()
        self.upstart_install()
        self.apache_config()
        """ install_logrotate(appname, use_sudo=use_sudo, dry=dry)"""
        self.env_baseline()
        self.local_settings_config()
        self.db_clear()
        self.queuing_config()
        self.db_update()
        self.search_config()
 
    def homedir_config(self):   
        os.mkdir(os.path.join(os.path.expanduser('~'), 'public_html'))
        
    def sslcert_config(self):
        local('sudo openssl req -config /ecs/ssleay.cnf -nodes -new -newkey rsa:1024 -days 365 -x509 -keyout /etc/ssl/private/%s.key -out /etc/ssl/certs/%s.pem' %
        (self.hostname, self.hostname))
    
    def local_settings_config(self):
        local_settings = open(os.path.join(self.dirname, 'local_settings.py'), 'w')
        local_settings.write("""
# database settings
DATABASES_OVERRIDE = {}
DATABASES_OVERRIDE['default'] = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '%(username)s',
    'USER': '%(username)s',
}

# rabbitmq/celery settings
BROKER_USER = '%(username)s'
BROKER_PASSWORD = '%(queuing_password)s'
BROKER_VHOST = '%(username)s'
CARROT_BACKEND = ''
CELERY_ALWAYS_EAGER = False

# haystack settings
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/'

DEBUG = False
TEMPLATE_DEBUG = False
            """ % {
            'username': self.username,
            'queuing_password': self.queuing_password,
        })
        local_settings.close()
    
    def apache_config(self):
        apache_setup(self.appname, use_sudo=self.use_sudo, dry=self.dry, hostname=self.hostname, ip=self.ip)
        
    def wsgi_config(self):
        write_template(os.path.join(self.dirname, "templates", "apache2", self.appname, "apache.wsgi", "ecs-main.wsgi"),
            os.path.join(self.dirname, "main.wsgi"), 
            {'source': os.path.join(self.dirname, ".."), 'appname': self.appname,}
            )
        write_template(os.path.join(self.dirname, "templates", "apache2", self.appname, "apache.wsgi", "ecs-service.wsgi"),
            os.path.join(self.dirname, "service.wsgi"), 
            {'source': os.path.join(self.dirname, ".."), 'appname': self.appname,}
            )
        
    
    def apache_restart(self):
        pass
    
    def wsgi_reload(self):
        pass
    
    def upstart_install(self):
        install_upstart(self.appname, use_sudo=self.use_sudo, dry=self.dry)
    def upstart_stop(self):
        pass
    def upstart_start(self):
        pass

    def db_clear(self):
        local("sudo su - postgres -c \'createuser -S -d -R %s\' | true" % (self.username))
        local('dropdb %s | true' % self.username)
        local('createdb createdb --template=template0 --encoding=utf8 --locale=de_DE.utf8 %s' % self.username)
         
    def db_update(self):
        local('cd ~/src/ecs; . ~/environment/bin/activate; ./manage.py syncdb --noinput')
        local('cd ~/src/ecs; . ~/environment/bin/activate; ./manage.py migrate --noinput')
        local('cd ~/src/ecs; . ~/environment/bin/activate; ./manage.py bootstrap')

    def env_clear(self):
        pass
    def env_boot(self):
        pass
    def env_update(self):
        pass
    
    def env_baseline(self):        
        baseline_bootstrap = ['sudo'] if self.use_sudo else []
        baseline_bootstrap += [os.path.join(os.path.dirname(env.real_fabfile), 'bootstrap.py'), '--baseline', '/etc/apache2/ecs/wsgibaseline/']
        local(subprocess.list2cmdline(baseline_bootstrap))
 
    def queuing_config(self):
        local('sudo rabbitmqctl add_user %s %s' % (self.username, self.queuing_password))
        local('sudo rabbitmqctl add_vhost %s' % self.username)
        local('sudo rabbitmqctl set_permissions -p %s %s ".*" ".*" ".*"' % (self.username, self.username))

    def search_config(self):
        local('cd ~/src/ecs; . ~/environment/bin/activate; ./manage.py build_solr_schema > ~%s/solr_schema.xml' % self.username)
        local('sudo cp ~%s/solr_schema.xml /etc/solr/conf/schema.xml' % self.username)
        
        jetty_cnf = open(os.path.expanduser('~/jetty.cnf'), 'w')
        jetty_cnf.write("""
NO_START=0
VERBOSE=yes
JETTY_PORT=8983
        """)
        jetty_cnf.close()
        local('sudo cp ~{0}/jetty.cnf /etc/default/jetty'.format(self.username))
        local('sudo /etc/init.d/jetty start')

    def search_update(self):
        pass
    def massimport(self):
        pass
