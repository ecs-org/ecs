# ecs main application environment setup
import os
import subprocess
import sys
import shutil
import tempfile
import logging
import string
import random
import distutils.dir_util

from uuid import uuid4
from fabric.api import local, env, warn

from deployment.utils import get_pythonenv, import_from, get_pythonexe, zipball_create, write_regex_replace
from deployment.utils import control_upstart, apache_setup, strbool, write_template
from deployment.pkgmanager import get_pkg_manager, packageline_split
from deployment.appsupport import SetupTargetObject
from deployment.conf import load_config


class SetupTarget(SetupTargetObject):
    """ SetupTarget(use_sudo=True, dry=False, hostname=None, ip=None) """ 
    def __init__(self, *args, **kwargs):
        dirname = os.path.dirname(__file__)
        config_file = kwargs.pop('config', None)
        if config_file is None:
            config_file = os.path.join(dirname, '..', 'ecs.yml')
        super(SetupTarget, self).__init__(*args, **kwargs)
        self.dirname = dirname
        self.appname = 'ecs'
        
        if config_file:
            self.configure(config_file)
        
    def configure(self, config_file):
        self.config = load_config(config_file)
        self.homedir = os.path.expanduser('~')
        self.configdir = os.path.join(self.homedir, 'ecs-conf')
        # set legacy attributes
        for attr in ('ip', 'host'):
            setattr(self, attr, self.config[attr])
        self.config['local_hostname'] = self.config['host'].split('.')[0]
        self.config.setdefault('postgresql.username', self.config['user'])
        self.config.setdefault('postgresql.database', self.config['user'])
        self.config.setdefault('rabbitmq.username', self.config['user'])
        self.config.setdefault('rabbitmq.password', self.random_string(20))
        self.config.setdefault('mediaserver.storage.encrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.pub'))
        self.config.setdefault('mediaserver.storage.signing_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.sec'))
        self.config.setdefault('mediaserver.storage.decrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.sec'))
        self.config.setdefault('mediaserver.storage.verify_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.pub'))

    def random_string(self, length=40):
        chars = string.ascii_letters + string.digits + "_-,.+#!?$%&/()[]{}*;:=<>" # ~6.4 bit/char
        return ''.join(random.choice(chars) for i in xrange(length))
        
    def print_random_string(self, length=40):
        print self.random_string(length=length)
    
    def write_config_template(self, template, dst, context=None):
        if context is None:
            context = self.config
        write_template(os.path.join(self.dirname, 'templates', 'config', template), dst, context=context)
        
    def help(self, *args, **kwargs):
        print('''{0} targets
  * system_setup
  # howto update:
        # on host: fab target:ecs,service,True
        # from executing host: make source update, clean_pyc, write version.py
        # on host bootstrap, fab appreq, fab appenv, fab appsys:ecs,update=True
        # on host: fab target:ecs,service,False 
        
        '''.format(self.appname))
    
    def service(self, enable=True):
        enable= strbool(enable)
        if enable:
            # TODO: write scheduled service note into file where ecs-wsgi.py reads it
            self.wsgi_reload()
            self.upstart_stop()
        else:
            # TODO: delete service mode file
            self.upstart_start()
            self.wsgi_reload()

    def update(self, *args, **kwargs):
        self.host_config()
        self.homedir_config()
        self.servercert_config()
        
        self.apache_baseline()
        self.django_config()
        self.queuing_config()
        
        self.ca_update()
        self.db_update()
        self.search_config()
        
        self.apache_config() 
        self.upstart_install()
        
        self.apache_restart()
        self.upstart_start()
        
    
    def system_setup(self, *args, **kwargs):
        self.host_config()
        self.homedir_config()
        self.servercert_config()
        
        self.apache_baseline()
        # install_logrotate(appname, use_sudo=use_sudo, dry=dry)
        self.django_config()
        self.db_clear()
        self.queuing_config()

        self.gpg_config()
        self.ca_config()
        
        self.ca_update()
        self.db_update()
        self.search_config()
        
        self.apache_config() 
        self.upstart_install()
        
        self.apache_restart()
        self.upstart_start()
        
    def host_config(self):
        _, tmp = tempfile.mkstemp()
        self.write_config_template('hosts', tmp)
        local('sudo cp %s /etc/hosts' % tmp)
        os.remove(tmp)
 
    def homedir_config(self):
        homedir = os.path.expanduser('~')
        for name in ('public_html', '.python-eggs', 'ecs-conf'):
            pathname = os.path.join(homedir, name)
            if not os.path.exists(pathname):
                os.mkdir(pathname)

    def servercert_config(self):
        try:
            ssl_key = self.config.get_path('ssl.key')
            ssl_cert = self.config.get_path('ssl.cert')
            local('sudo cp %s /etc/ssl/private/%s.key' % (ssl_key, self.host))
            local('sudo cp %s /etc/ssl/certs/%s.pem' % (ssl_cert, self.host))
            local('sudo chmod 0600 /etc/ssl/private/%s.key' % self.host)
        except KeyError:
            warn('Missing SSL key or certificate - a new pair will be generated')
            openssl_cnf = os.path.join(self.configdir, 'openssl-ssl.cnf')
            self.write_config_template('openssl-ssl.cnf', openssl_cnf)
            local('sudo openssl req -config {0} -nodes -new -newkey rsa:1024 -days 365 -x509 -keyout /etc/ssl/private/{1}.key -out /etc/ssl/certs/{1}.pem'.format(openssl_cnf, self.host))
    
    def gpg_config(self):
        for key, filename in (('encrypt_key', 'ecs_mediaserver.pub'), ('signing_key', 'ecs_authority.sec'), ('decrypt_key', 'ecs_mediaserver.sec'), ('verify_key', 'ecs_authority.pub')):
            try:
                path = self.config.get_path('mediaserver.storage.%s' % key)
                shutil.copy(path, os.path.join(self.configdir, filename))
            except KeyError:
                pass
    
    def ca_config(self):
        openssl_cnf = os.path.join(self.configdir, 'openssl-ca.cnf')
        from ecs.pki.openssl import CA
        cadir = os.path.join(self.homedir, 'ecs-ca')
        if os.path.exists(cadir):
            local('rm -r %s' % cadir)
        ca = CA(cadir, config=openssl_cnf)
        self.write_config_template('openssl-ca.cnf', openssl_cnf, ca.__dict__)
        
    def ca_update(self):
        try:
            replacement = self.config.get_path('ca.dir')
        except KeyError:
            return
        basedir = os.path.join(self.homedir, 'ecs-ca')
        if os.path.exists(basedir):
            warn('CA directory exists (%s), refusing to overwrite.' % basedir)
            return
        shutil.copytree(replacement, basedir)
        
    def django_config(self):
        self.write_config_template('django.py', os.path.join(self.configdir, 'django.py'))
        
    def apache_baseline(self):
        baseline_bootstrap = ['sudo'] if self.use_sudo else []
        baseline_bootstrap += [os.path.join(os.path.dirname(env.real_fabfile), 'bootstrap.py'), '--baseline', '/etc/apache2/ecs/wsgibaseline/']
        local(subprocess.list2cmdline(baseline_bootstrap))
 
    def apache_config(self):
        apache_mkdirs = ['sudo'] if self.use_sudo else []
        apache_mkdirs += ['mkdir', '-p', '/etc/apache2/ecs', '/etc/apache2/ecs/apache.wsgi', '/etc/apache2/ecs/apache.conf']
        local(subprocess.list2cmdline(apache_mkdirs))
        apache_setup(self.appname, use_sudo=self.use_sudo, 
            hostname=self.host, 
            ip=self.ip, 
            ca_certificate_file=os.path.join(self.homedir, 'ecs-ca', 'ca.cert.pem'),
            ca_revocation_file=os.path.join(self.homedir, 'ecs-ca', 'crl.pem'),
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
        local('sudo /etc/init.d/apache2 restart')
        
    def wsgi_reload(self):
        pass
    
    
    def upstart_install(self):
        control_upstart(self.appname, "install", upgrade=True, use_sudo=self.use_sudo, dry=self.dry)

    def upstart_stop(self):
        control_upstart(self.appname, "stop", use_sudo=self.use_sudo, dry=self.dry)
        
    def upstart_start(self):
        control_upstart(self.appname, "start", use_sudo=self.use_sudo, dry=self.dry)
        
        
    def db_clear(self):
        local("sudo su - postgres -c \'createuser -S -d -R %(postgresql.username)s\' | true" % self.config)
        local('dropdb %(postgresql.database)s | true' % self.config)
        local('createdb --template=template0 --encoding=utf8 --locale=de_DE.utf8 %(postgresql.database)s' % self.config)
         
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

    def queuing_config(self):
        if int(local('sudo rabbitmqctl list_vhosts | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
            local('sudo rabbitmqctl delete_vhost %(rabbitmq.username)s' % self.config)
        
        local('sudo rabbitmqctl add_vhost %s' % self.username)
            
        if int(local('sudo rabbitmqctl list_users | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
            local('sudo rabbitmqctl delete_user %(rabbitmq.username)s ' % self.config)
        
        local('sudo rabbitmqctl add_user %(rabbitmq.username)s %(rabbitmq.password)s' % self.config)
        local('sudo rabbitmqctl set_permissions -p %(rabbitmq.username)s %(rabbitmq.username)s ".*" ".*" ".*"' % self.config)

    def search_config(self):
        local('cd ~/src/ecs; . ~/environment/bin/activate; ./manage.py build_solr_schema > ~%s/ecs-conf/solr_schema.xml' % self.username)
        local('sudo cp ~%s/ecs-conf/solr_schema.xml /etc/solr/conf/schema.xml' % self.username)
        with open(os.path.expanduser('~/ecs-conf/jetty.cnf'), 'w') as f:
            f.write("NO_START=0\nVERBOSE=yes\nJETTY_PORT=8983\n")
        local('sudo cp ~{0}/ecs-conf/jetty.cnf /etc/default/jetty'.format(self.username))
        local('sudo /etc/init.d/jetty stop')
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
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "conf", "server.xml"))
    
def custom_install_tomcat_apt_user(pkgline, filename):
    tomcatpath = os.path.join(get_pythonenv(), "tomcat-6")
    
    if os.path.exists(os.path.join(tomcatpath)):
        if os.path.exists(tomcatpath+"-old"):
            shutil.rmtree(tomcatpath+"-old")
        shutil.move(tomcatpath, tomcatpath+"-old")
        
    install = 'tomcat6-instance-create -p 4780 -c 4705 \'{0}\''.format(tomcatpath)
    popen = subprocess.Popen(install, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate() 
    returncode = popen.returncode  
    if returncode != 0:
        print "Error:", returncode, stdout, stderr
        return False
    else:
        return True

def custom_check_tomcat_other_user(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "tomcat-6", "conf", "server.xml"))
    
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
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    temp_dir = tempfile.mkdtemp()
    temp_dest = os.path.join(temp_dir, "tomcat-6")
    final_dest = os.path.join(get_pythonenv(), "tomcat-6")
    result = False
    
    try:
        pkg_manager.static_install_unzip(filename, temp_dir, checkfilename, pkgline)
        if pkg_manager.static_install_unzip(filename, temp_dir, checkfilename, pkgline):
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


def custom_install_pdftotext(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    tempdir = tempfile.mkdtemp()
    outputdir = os.path.dirname(get_pythonexe())
    result = False
    
    try:
        if pkg_manager.static_install_unzip(filename, tempdir, checkfilename, pkgline):
            try:
                shutil.copy(os.path.join(tempdir,"xpdfbin-win-3.03", "bin32", checkfilename), 
                    os.path.join(outputdir, checkfilename))
            except EnvironmentError:
                pass
            else:
                result = True
    finally:    
        shutil.rmtree(tempdir)
    
    return result
    
def custom_install_origami(pkgline, filename):
    env = get_pythonenv()
    gem_bindir = gem_home = os.path.join(env, 'gems', 'bin')
    if sys.platform == 'win32':
        bindir = os.path.join(env, 'Scripts')
        for binfile in ['pdfcop', 'pdfdecrypt']:
            with open(os.path.join(bindir, '{0}.bat'.format(binfile)), 'w') as f:
                f.write("""@echo off
set GEM_HOME=%VIRTUAL_ENV%\gems
set GEM_PATH=%GEM_HOME%
ruby.exe %GEM_HOME%\\bin\\{0} %*
                """.format(binfile))
    else:
        bindir = os.path.join(env, 'bin')
        for binfile in ['pdfcop', 'pdfdecrypt']:
            wrapper = os.path.join(bindir, binfile)
            with open(wrapper, 'w') as f:
                f.write("""#!/bin/sh
export GEM_HOME="${{VIRTUAL_ENV}}/gems"
export GEM_PATH="${{GEM_HOME}}"
"${{GEM_HOME}}/bin/{0}" $*
                """.format(binfile))
            os.chmod(wrapper, 0755)
    return custom_install_ruby_gem(pkgline, filename)

def custom_install_ruby_gem(pkgline, filename):
    env = get_pythonenv()
    gem_home = os.path.join(env, 'gems')

    os.environ['GEM_HOME'] = gem_home
    os.environ['GEM_PATH'] = gem_home

    is_win = sys.platform == 'win32'
    bindir = os.path.join(env, 'Scripts' if is_win else 'bin')
    gembin = 'gem.bat' if is_win else 'gem'
    gem_cmd = [gembin, 'install', '--no-ri', '--no-rdoc', filename]
    gem = subprocess.Popen(gem_cmd)
    gem.wait()
    return gem.returncode == 0
