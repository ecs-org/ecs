# ecs main application environment setup
import os
import subprocess
import sys
import shutil
import tempfile
import logging
import distutils.dir_util

from uuid import uuid4
from fabric.api import local, env, warn

from deployment.utils import get_pythonenv, import_from, get_pythonexe, zipball_create, write_regex_replace
from deployment.utils import install_upstart, apache_setup, write_template, which
from deployment.pkgmanager import get_pkg_manager, packageline_split
from deployment.appsupport import SetupTargetObject



class SetupTarget(SetupTargetObject):
    """ SetupTarget(use_sudo=True, dry=False, hostname=None, ip=None) """ 
    def __init__(self, *args, **kwargs):
        super(SetupTarget, self).__init__(*args, **kwargs)
        self.appname = 'ecs'
        self.dirname = os.path.dirname(__file__)
        self.queuing_password = uuid4().get_hex()

    def help(self, *args, **kwargs):
        print('''{0} targets
  * system_setup
        '''.format(self.appname))
    
    def update(self, *args, **kwargs):
        pass
    
    def system_setup(self, *args, **kwargs):
        self.homedir_config()
        self.sslcert_config()
        self.env_baseline()
        """ install_logrotate(appname, use_sudo=use_sudo, dry=dry)"""
        self.local_settings_config()
        self.db_clear()
        self.queuing_config()
        self.signing_config()
        self.db_update()
        self.search_config()
        
        self.apache_config() # restarts apache at end
        self.upstart_install() # because upstart_install re/starts service at end, we put it last
 
    def homedir_config(self):
        homedir = os.path.expanduser('~')
        for name in ('public_html',):
            pathname = os.path.join(homedir, name)
            if not os.path.exists(pathname):
                os.mkdir(pathname)
        
    def sslcert_config(self):
        warn("Creating /autovm/ssleay.cnf")
        local('''cat <<SSLEAYCNF_EOF > /autovm/ssleay.cnf
RANDFILE                = /dev/urandom

[ req ]
default_bits            = 2048
default_keyfile         = privkey.pem
distinguished_name      = req_distinguished_name
prompt                  = no
policy                  = policy_anything

[ req_distinguished_name ]
countryName            = AT
stateOrProvinceName    = Vienna
localityName           = Vienna
organizationName       = ep3 Software & System House
organizationalUnitName = Security
commonName             = {0}
emailAddress           = admin@{0}
SSLEAYCNF_EOF'''.format(self.hostname))
        local('sudo openssl req -config /autovm/ssleay.cnf -nodes -new -newkey rsa:1024 -days 365 -x509 -keyout /etc/ssl/private/{0}.key -out /etc/ssl/certs/{0}.pem'.format(self.hostname))
    
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
BROKER_BACKEND = ''
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
        apache_setup(self.appname, use_sudo=self.use_sudo, dry=self.dry, hostname= self.hostname, ip= self.ip)
        
    def wsgi_config(self):
        write_template(os.path.join(self.dirname, "templates", "apache2", self.appname, "apache.wsgi", "ecs-main.wsgi"),
            os.path.join(self.dirname, "main.wsgi"), 
            {'source': os.path.join(self.dirname, ".."), 'appname': self.appname,}
        )
        write_template(os.path.join(self.dirname, "templates", "apache2", self.appname, "apache.wsgi", "ecs-service.wsgi"),
            os.path.join(self.dirname, "service.wsgi"), 
            {'source': os.path.join(self.dirname, ".."), 'appname': self.appname,}
        )

    def catalina_cmd(self, what):
        TOMCAT_DIR = os.path.join(get_pythonenv(), 'tomcat-6') 
        if sys.platform == 'win32':
            cmd = "set CATALINA_BASE={0}&set CATALINA_OPTS=-Dpdf-as.work-dir={0}\\conf\\pdf-as&cd {0}&bin\\catalina.bat {1}".format(TOMCAT_DIR, what)
        else:
            cmd = subprocess.list2cmdline(['env', 'CATALINA_BASE={0}'.format(TOMCAT_DIR), 'CATALINA_OPTS=-Dpdf-as.work-dir={0}/conf/pdf-as'.format(TOMCAT_DIR), '{0}/bin/catalina.sh'.format(TOMCAT_DIR), what])
        return cmd
    
    def start_dev_signing(self):
        local(self.catalina_cmd('start'))
        
    def stop_dev_signing(self):
        local(self.catalina_cmd('stop'))
    
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
        local('createdb --template=template0 --encoding=utf8 --locale=de_DE.utf8 %s' % self.username)
         
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
  


def custom_check_gettext_runtime(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), 'bin', checkfilename))
    
def custom_install_gettext_runtime(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    pkg_manager.static_install_unzip(filename, get_pythonenv(), checkfilename, pkgline)
    return True

def custom_check_gettext_tools(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), 'bin', checkfilename))
    
def custom_install_gettext_tools(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    pkg_manager.static_install_unzip(filename, get_pythonenv(), checkfilename, pkgline)
    return True

  
def custom_check_tomcat_apt_user(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6"))
    
def custom_install_tomcat_apt_user(pkgline, filename):
    install = 'tomcat6-instance-create -p 4780 -c 4705 \'{0}\''.format(os.path.join(get_pythonenv(), "tomcat-6"))
    popen = subprocess.Popen(install, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        print "Error:", returncode, stdout, stderr
        return False
    else:
        return True

def custom_check_tomcat_other_user(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6"))
    
def custom_install_tomcat_other_user(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    temp_dir = tempfile.mkdtemp()
    temp_dest = os.path.join(temp_dir, checkfilename)
    final_dest = os.path.join(get_pythonenv(), "tomcat-6")
    result = False
    
    try:
        if os.path.exists(final_dest):
            shutil.rmtree(final_dest)
        if pkg_manager.static_install_tar(filename, temp_dir, checkfilename, pkgline):
            write_regex_replace(os.path.join(temp_dest, 'conf', 'server.xml'),
                r'([ \t])+(<Connector port=)("[0-9]+")([ ]+protocol="HTTP/1.1")',
                r'\1\2"4780"\4')
            shutil.copytree(temp_dest, final_dest)
            result = True
    finally:    
        shutil.rmtree(temp_dir)
    
    return result


def custom_check_pdfas(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "webapps", checkfilename))
   
def custom_install_pdfas(pkgline, filename):
    
    def _patch_pdfas_war(target):
        patchlib = import_from(os.path.join(os.path.dirname(get_pythonexe()), 'python-patch.py'))
        patchlib.logger.setLevel(logging.INFO)
        old_cwd = os.getcwd()
        temp_dir = tempfile.mkdtemp()
        pkg_manager = get_pkg_manager()
        success = False
        
        try:
            if pkg_manager.static_install_unzip(target, temp_dir, None, None):
                os.chdir(os.path.join(temp_dir, "jsp"))
                p = patchlib.fromfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'signature', 'pdf-as-3.2-jsp.patch'))
                if p.apply():
                    os.remove(target)
                    zipball_create(target, temp_dir)
                    success = True
                else:
                    print("Error: Failed patching:", target, temp_dir)
        finally:
            os.chdir(old_cwd)
            shutil.rmtree(temp_dir)
            
        return success
    
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    temp_dir = tempfile.mkdtemp()
    temp_dest = os.path.join(temp_dir, "tomcat-6")
    final_dest = os.path.join(get_pythonenv(), "tomcat-6")
    result = False
    
    try:
        if pkg_manager.static_install_unzip(filename, temp_dir, checkfilename, pkgline):
            if _patch_pdfas_war(os.path.join(temp_dest, "webapps", checkfilename)):
                write_regex_replace(
                    os.path.join(temp_dest, 'conf', 'pdf-as', 'cfg', 'config.properties'),
                    r'(moc.sign.url=)(http://127.0.0.1:8080)(/bkuonline/http-security-layer-request)',
                    r'\1http://localhost:4780\3')
                write_regex_replace(
                    os.path.join(temp_dest, 'conf', 'pdf-as', 'cfg', 'pdf-as-web.properties'),
                    r'([#]?)(retrieve_signature_data_url_override=)(http://localhost:8080)(/pdf-as/RetrieveSignatureData)',
                    r'\2http://localhost:4780\4')
                
                distutils.dir_util.copy_tree(temp_dest, final_dest, verbose=True)
                result = True
    finally:    
        shutil.rmtree(temp_dir)
    
    return result


def custom_check_mocca(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "webapps", checkfilename))

def custom_install_mocca(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    outputdir = os.path.join(get_pythonenv(), "tomcat-6", "webapps")
    pkg_manager = get_pkg_manager()
    return pkg_manager.static_install_copy(filename, outputdir, checkfilename, pkgline)


def custom_install_origami(pkgline, filename):
    return custom_install_ruby_gem(pkgline, filename)

def custom_install_ruby_gem(pkgline, filename):
    
    gem_home = os.path.join(get_pythonenv(),'gems')
    filename_dir = os.path.dirname(filename)
    filename = os.path.basename(filename)
    
    if not os.path.exists(gem_home):
        os.mkdir(gem_home)
        
    if not os.path.exists(os.path.join(filename_dir, filename)):
        print "gem to install does not exist:", filename
    
    if sys.platform == 'win32':
        gem_home = gem_home.replace("\\", "/")
        bin_dir = os.path.join(os.environ['VIRTUAL_ENV'],'Scripts').replace("\\", "/")
        install = 'cd {0}& set GEM_HOME="{1}"& set GEM_PATH="{1}"&\
gem install --no-ri --no-rdoc --local --bindir="{2}" {3}'.format(
            filename_dir, gem_home, bin_dir, filename)
    else:
        bin_dir = os.path.join(os.environ['VIRTUAL_ENV'],'bin')
        install = 'export GEM_HOME="{0}"; export GEM_PATH="{0}";\
gem install --no-ri --no-rdoc --local --bindir="{1}" {2}'.format(
            filename_dir, gem_home, bin_dir, filename)
    
    popen = subprocess.Popen(install, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        print "Error:", returncode, stdout, stderr
        return False
    else:
        return True
