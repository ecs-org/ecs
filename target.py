# ecs main application environment setup
import os
import subprocess
import shutil
import tempfile
import string
import random
import time
import getpass

from fabric.api import local, env, warn, abort, settings

from deployment.utils import get_pythonenv, get_pythonexe, write_regex_replace, is_precise_or_older
from deployment.utils import touch, control_upstart, apache_setup, strbool, strint, write_template, write_template_dir
from deployment.pkgmanager import get_pkg_manager, packageline_split
from deployment.conf import load_config

class SetupTarget(object):
    """ SetupTargetObject(use_sudo=True, dry=False, hostname=None, ip=None)
    """

    def __init__(self, *args, **kwargs):
        dirname = os.path.dirname(__file__)

        config_file = kwargs.pop('config', None)
        if config_file is None:
            config_file = os.path.join(dirname, '..', 'ecs.yml')

        self.use_sudo = kwargs.pop('use_sudo', True)
        self.dry = kwargs.pop('dry', False)
        self.host = kwargs.pop('hostname', None)
        self.ip = kwargs.pop('ip', None)
        self.username = getpass.getuser()
        self.destructive = strbool(kwargs.pop('destructive', False))

        self.dirname = dirname
        self.appname = 'ecs'

        self.configure(config_file)
        self.extra_kwargs = kwargs


    def local(self, cmd):
        if self.use_sudo:
            cmd = ['sudo'] + cmd
        return local(subprocess.list2cmdline(cmd))

    def configure(self, config_file):
        self.config = load_config(config_file)
        self.homedir = os.path.expanduser('~')
        self.configdir = os.path.join(self.homedir, 'ecs-conf')
        self.pythonexedir = os.path.dirname(get_pythonexe())
        # set legacy attributes
        for attr in ('ip', 'host'):
            setattr(self, attr, self.config[attr])
        self.config['local_hostname'] = self.config['host'].split('.')[0]
        # set default for parameter that are optional
        self.config.setdefault('ssl.chain', '') # chain is optional
        self.config.setdefault('postgresql.username', self.config['user'])
        self.config.setdefault('postgresql.database', self.config['user'])
        self.config.setdefault('postgresql.password', self.random_string(14, simpleset=True))
        self.config.setdefault('rabbitmq.username', self.config['user'])
        self.config.setdefault('rabbitmq.password', self.random_string(20))
        self.config.setdefault('mediaserver.storage.encrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.pub'))
        self.config.setdefault('mediaserver.storage.signing_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.sec'))
        self.config.setdefault('mediaserver.storage.decrypt_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_mediaserver.sec'))
        self.config.setdefault('mediaserver.storage.verify_key', os.path.join(self.homedir, 'src', 'ecs', 'ecs_authority.pub'))
        self.config.setdefault('storagevault.implementation', 'ecs.mediaserver.storagevault.LocalFileStorageVault')
        self.config.setdefault('storagevault.options.localfilestorage_root', os.path.join(self.homedir, 'ecs-storage-vault'))
        self.config.setdefault('debug.logo_border_color', 'white')

    def random_string(self, length=40, simpleset=False):
        if simpleset:
            chars = string.ascii_letters + string.digits
        else:
            chars = string.ascii_letters + string.digits + "_-,.+#!?$%&/()[]{}*;:=<>" # ~6.4 bit/char

        return ''.join(random.choice(chars) for i in xrange(length))

    def print_random_string(self, length=40, simpleset=False):
        simpleset= strbool(simpleset)
        length = strint(length)

        print self.random_string(length=length, simpleset=simpleset)

    def get_config_template(self, template):
        with open(os.path.join(self.dirname, 'templates', 'config', template)) as f:
            data = f.read()
        return data

    def write_config_template(self, template, dst, context=None, filemode=None, backup=True, force=False, use_sudo=False):
        if context is None:
            context = self.config
        print("Writing config template {0} to {1}".format(template, dst))
        write_template(os.path.join(self.dirname, 'templates', 'config', template),
            dst, context=context, filemode=filemode, backup=backup, force=force, use_sudo=use_sudo)

    def write_config_templatedir(self, srcdir, dstdir, context=None, filemode=None, backup=True, force=False, use_sudo=False):
        if context is None:
            context = self.config
        print("Writing config template dir {0} to {1}".format(srcdir, dstdir))
        write_template_dir(
            os.path.join(self.dirname, 'templates', 'config', srcdir),
            dstdir,
            context=context,
            filemode=filemode,
            backup=backup,
            force=force,
            use_sudo=use_sudo)

    def help(self, *args, **kwargs):
        print('''fab target:{0},action[,config=path-to-config.yml]
  * actions: system_setup, update, and others

        '''.format(self.appname))

    def system_setup(self, *args, **kwargs):
        ''' System Setup; Destructive, idempotent '''
        self.destructive = True
        self.setup(self, *args, **kwargs)

    def setup(self, *args, **kwargs):
        ''' Setup; idempotent, tries not to overwrite existing database or eg. ECS-CA , except destructive=True '''
        self.directory_config()
        self.host_config(with_current_ip=True)

        self.env_update()

        self.servercert_config()
        self.backup_config()
        self.mail_config()
        self.queuing_config()

        # install_logrotate(appname, use_sudo=use_sudo, dry=dry)

        self.sysctl_config()
        self.postgresql_config()
        self.postgresql_restart()
        self.pgbouncer_config()

        self.db_clear()
        self.django_config()
        self.gpg_config()
        self.ca_config()

        self.db_update()

        self.search_config()
        self.search_update()

        self.apache_baseline()
        self.apache_config()

        self.pdfas_config()
        self.mocca_config()
        tomcatversion = "6" if is_precise_or_older() else "7"
        extra_env = {'tomcatversion': tomcatversion}
        self.daemons_install(extra_env= extra_env)

        self.custom_network_config()
        self.host_config(with_current_ip=False)
        self.firewall_config()

        self.apache_restart()
        self.daemons_start()


    def update(self, *args, **kwargs):
        ''' System Update: Non destructive '''
        self.directory_config()

        self.env_update()
        self.db_update()

        self.search_config()
        self.search_update()

        self.apache_restart()
        self.daemons_start()

    def maintenance(self, enable=True):
        ''' Enable/Disable System Maintenance (stop daemons, display service html)'''
        enable= strbool(enable)
        if enable:
            touch(os.path.join(self.configdir, 'service.now'))
            self.wsgi_reload()
            self.daemons_stop()
        else:
            os.remove(os.path.join(self.configdir, 'service.now'))
            self.daemons_start()
            self.wsgi_reload()

    def directory_config(self):
        homedir = os.path.expanduser('~')
        for name in ('empty_html', 'public_html', '.python-eggs', 'ecs-conf'):
            pathname = os.path.join(homedir, name)
            if not os.path.exists(pathname):
                os.mkdir(pathname)

        # /opt/ecs directory
        pathname = os.path.join('/opt', self.appname)
        if not os.path.exists(pathname):
            local('sudo mkdir {0}'.format(pathname))
        local('sudo chown {0}:{0} {1}'.format(self.appname, pathname))


    def host_config(self, with_current_ip=False):
        with_current_ip = strbool(with_current_ip)

        _, tmp = tempfile.mkstemp()
        with tempfile.NamedTemporaryFile() as h:
            h.write(self.config['host'])
            h.flush()
            local('sudo cp {0} /etc/hostname'.format(h.name))
        local('sudo hostname -F /etc/hostname')

        value = local('ip addr show eth0 | grep inet[^6] | sed -re "s/[[:space:]]+inet.([^ /]+).+/\\1/g"', capture=True)
        if value != self.config['ip']:
            warn('current ip ({0}) and to be configured ip ({1}) are not the same'.format(value, self.config['ip']))

        if with_current_ip:
            if value.succeeded:
                self.config['current_ip'] = value
                if self.config['current_ip'] != self.config['ip']:
                    warn('Temporary set hosts resolution of {0} to {1} instead of {2}'.format(
                        self.config['host'], self.config['current_ip'], self.config['ip']))
            else:
                abort("no ip address ? ip addr grep returned: {0}".format(value))
        else:
            self.config['current_ip'] = self.config['ip']

        self.write_config_template('hosts', tmp)
        local('sudo cp %s /etc/hosts' % tmp)
        os.remove(tmp)

    def custom_network_config(self):
        if 'network.resolv' in self.config:
            with tempfile.NamedTemporaryFile() as t:
                t.write(self.config['network.resolv'])
                t.flush()
                local('sudo cp {0} /etc/resolv.conf'.format(t.name))

        if 'network.interfaces' in self.config:
            with tempfile.NamedTemporaryFile() as t:
                t.write(self.config['network.interfaces'])
                t.flush()
                local('sudo cp {0} /etc/network/interfaces'.format(t.name))

    def firewall_config(self):
        write_template_dir(os.path.join(self.dirname, 'templates', 'config', 'shorewall'), '/', use_sudo=True)
        local('sudo /etc/init.d/shorewall restart')

    def backup_config(self):
        if not self.config.get('backup', default=False):
            warn('no backup configuration, skipping backup config')
        else:
            with settings(warn_only=True):
                local('sudo bash -c "if test -e /root/.gnupg; then rm -r /root/.gnupg; fi"')
            local('sudo gpg --homedir /root/.gnupg --rebuild-keydb-caches')
            local('sudo gpg --homedir /root/.gnupg --batch --yes --import {0}'.format(self.config.get_path('backup.encrypt_gpg_sec')))
            local('sudo gpg --homedir /root/.gnupg --batch --yes --import {0}'.format(self.config.get_path('backup.encrypt_gpg_pub')))

            with settings(warn_only=True):
                local('sudo mkdir -m 0600 -p /root/.duply/root')
                local('sudo mkdir -m 0600 -p /root/.duply/opt')

            self.config['duplicity.duply_path'] = self.pythonexedir

            self.config['duplicity.root'] = os.path.join(self.config['backup.hostdir'], 'root')
            self.config['duplicity.include'] = "SOURCE='/'"
            self.write_config_template('duply.template',
                '/root/.duply/root/conf', context=self.config, use_sudo=True, filemode= '0600')
            self.write_config_template('duplicity.root.files', '/root/.duply/root/exclude', use_sudo=True)

            self.config['duplicity.root'] = os.path.join(self.config['backup.hostdir'], 'opt')
            self.config['duplicity.include'] = "SOURCE='/opt'"
            self.write_config_template('duply.template',
                '/root/.duply/opt/conf', context=self.config, use_sudo=True, filemode= '0600')
            self.write_config_template('duplicity.opt.files', '/root/.duply/opt/exclude', use_sudo=True)

            self.config['duplicity.duply_conf'] = "root"
            with settings(warn_only=True): # remove legacy duply script, before it was renamed
                local('sudo bash -c "if test -f /etc/backup.d/90duply.sh; then rm /etc/backup.d/90duply.sh; fi"')
            self.write_config_template('duply-backupninja.sh',
                '/etc/backup.d/90duply-root.sh', backup=False, use_sudo=True, filemode= '0600')

            self.config['duplicity.duply_conf'] = "opt"
            with settings(warn_only=True): # remove legacy duply script, before it was renamed
                local('sudo bash -c "if test -f /etc/backup.d/91duply.sh; then rm /etc/backup.d/91duply.sh; fi"')
            self.write_config_template('duply-backupninja.sh',
                '/etc/backup.d/91duply-opt.sh', backup=False, use_sudo=True, filemode= '0600')

            self.write_config_template('10.sys',
                '/etc/backup.d/10.sys', backup=False, use_sudo=True, filemode= '0600')

            self.write_config_template('20.pgsql',
                '/etc/backup.d/20.pgsql', backup=False, use_sudo=True, filemode= '0600')

    def servercert_config(self):
        target_key = '/etc/ssl/private/{0}.key'.format(self.host)
        target_cert = '/usr/local/share/ca-certificates/{0}.crt'.format(self.host)
        target_chain = '/etc/ssl/{0}.chain.pem'.format(self.host)
        target_combined = '/etc/ssl/{0}.combined.pem'.format(self.host)

        try:
            ssl_key = self.config.get_path('ssl.key')
            ssl_cert = self.config.get_path('ssl.cert')
            local('sudo cp {0} {1}'.format(ssl_key, target_key))
            local('sudo cp {0} {1}'.format(ssl_cert, target_cert))
            local('sudo chmod 0600 {0}'.format(target_key))
        except KeyError:
            warn('Missing SSL key or certificate - a new pair will be generated')
            openssl_cnf = os.path.join(self.configdir, 'openssl-ssl.cnf')
            self.write_config_template('openssl-ssl.cnf', openssl_cnf)
            local('sudo openssl req -config {0} -nodes -new -newkey rsa:2048 -days 365 -x509 -keyout {1} -out {2}'.format(openssl_cnf, target_key, target_cert))

        # copy and combine chain file (if exist, or create empty file instead)
        ssl_chain = self.config.get_path('ssl.chain')
        if ssl_chain:
            local('sudo cp {0} {1}'.format(ssl_chain, target_chain))
            # combine cert plus chain to combined.crt
            local('sudo bash -c "cat {0} {1} > {2}"'.format(target_cert, target_chain, target_combined))
        else:
            # no chain is available, clone cert to chain and combined so other software will find them
            local('sudo cp {0} {1}'.format(target_cert, target_chain))
            local('sudo cp {0} {1}'.format(target_cert, target_combined))

        # delete old java cacerts KeyStore, fixes that old certificate of same host will get stuck
        #local('sudo bash -c "if test -f /etc/ssl/certs/java/cacerts; then rm /etc/ssl/certs/java/cacerts; fi"')

        # update local and java store (at least the one in /etc/ssl/certs/java)
        local('sudo update-ca-certificates --verbose') # needed for all in special java that pdf-as knows server cert

    def mail_config(self):
        '''
        with tempfile.NamedTemporaryFile() as h:
            h.write(self.config['host'])
            h.flush()
            local('sudo cp {0} /etc/mailname'.format(h.name))

        self.config['postfix.cert'] = '/etc/ssl/private/{0}.pem'.format(self.host)
        self.config['postfix.key'] = '/etc/ssl/private/{0}.key'.format(self.host)
        self.write_config_template('postfix.main.cf', '/etc/postfix/main.cf', use_sudo=True)
        self.write_config_template('postfix.master.cf', '/etc/postfix/master.cf', use_sudo=True)
        self.write_config_template('aliases', '/etc/aliases', use_sudo=True)

smtpd_tls_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
smtpd_tls_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
myhostname = ecsdev.ep3.at
mydestination = ecsdev.ep3.at, localhost.ep3.at, , localhost
myorigin = /etc/mailname # $myhostname
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 %(ip)s/32
[localhost:8823]

mydestination =
local_recipient_maps =
local_transport = error:local mail delivery is disabled
myorigin = /etc/mailname # $myhostname
relay_domains = $myhostname

  myorigin = example.com
  mydestination =
  local_recipient_maps =
  local_transport = error:local mail delivery is disabled
  relay_domains = example.com
  parent_domain_matches_subdomains =
      debug_peer_list smtpd_access_maps
  smtpd_recipient_restrictions =
      permit_mynetworks reject_unauth_destination

  relay_recipient_maps = hash:/etc/postfix/relay_recipients
  transport_maps = hash:/etc/postfix/transport

/etc/postfix/transport:
$myhostname   smtp:[localhost:8823]
        '''
        pass

    def gpg_config(self):
        for key, filename in (('encrypt_key', 'ecs_mediaserver.pub'), ('signing_key', 'ecs_authority.sec'), ('decrypt_key', 'ecs_mediaserver.sec'), ('verify_key', 'ecs_authority.pub')):
            try:
                path = self.config.get_path('mediaserver.storage.%s' % key)
                shutil.copy(path, os.path.join(self.configdir, filename))
            except KeyError:
                pass

    def ca_config(self):
        cadir = os.path.join(self.homedir, 'ecs-ca')

        if self.destructive:
            if os.path.exists(cadir):
                warn('deleting CA directory because destructive=True')
                local('rm -r %s' % cadir)
        else:
            warn("not removing CA directory because destructive=False")

        try:
            replacement = self.config.get_path('ca.dir')
        except KeyError:
            warn('ca.dir config settings not found, leaving CA directory as it is')
            return

        if os.path.exists(os.path.join(cadir, 'private')):
            warn('CA directory exists (%s), refusing to overwrite.' % cadir)
        else:
            shutil.copytree(replacement, cadir)

            for n in ('certs', 'crl', 'newcerts',):
                t = os.path.join(cadir, n)
                if not os.path.exists(t):
                    os.mkdir(t)


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
        apache_trustycompat = ['sudo', '/bin/bash', '-c', 'if test ! -d /etc/apache2/conf.d; then if test ! -L /etc/apache2/conf.d ; then ln -s /etc/apache2/conf-available/ /etc/apache2/conf.d ; fi; fi']
        local(subprocess.list2cmdline(apache_trustycompat))
        apache_setup(self.appname, use_sudo=self.use_sudo,
            hostname=self.host,
            ip=self.ip,
            ca_certificate_file=os.path.join(self.homedir, 'ecs-ca', 'ca.cert.pem'),
            ca_revocation_file=os.path.join(self.homedir, 'ecs-ca', 'crl.pem'),
        )

    def sysctl_config(self):
        sysctl_conf = '/etc/sysctl.d/30-ECS.conf'
        params = {
            'kernel.shmmax': '2147483648',       # 2 GB
        }
        conf = ''
        for k, v in params.iteritems():
            self.local(['sysctl', '-w', '{0}={1}'.format(k, v)])
            conf += '{0} = {1}'.format(k, v)
        conf += '\n'
        tmp_fd, tmp_name = tempfile.mkstemp()
        os.write(tmp_fd, conf)
        os.close(tmp_fd)
        cat = subprocess.list2cmdline(['cat', tmp_name])
        tee = subprocess.list2cmdline((['sudo'] if self.use_sudo else []) + ['tee', sysctl_conf])
        local('{0} | {1} > /dev/null'.format(cat, tee))
        os.remove(tmp_name)

    def postgresql_version(self):
        result = local('pg_config --version | sed -re "s/[^ ]+ ([0-9]+)\.([0-9]+).*/\\1.\\2/g"', capture=True)
        if result.failed:
            abort("detecting postgresql version failed (pg_config --version): {0} {1}".format(result.stdout, result.stderr))
        pg_version = result.stdout
        return pg_version

    def postgresql_config(self):
        postgresql_conf = '/etc/postgresql/{0}/main/postgresql.conf'.format(self.postgresql_version())
        _marker = '# === ECS config below: do not edit, autogenerated ==='
        conf = ''
        self.local(['cp', postgresql_conf, postgresql_conf + '.bak'])
        with open(postgresql_conf, 'r') as f:
            for line in f:
                if line.strip('\n') == _marker:
                    break
                conf += line
        conf += '\n'.join([
            _marker,
            '# manual tuned settings: 1.10.2014 (similar to pgtune -i postgresql.conf -M 4294967296 -c 40 -T Web)',
            'wal_sync_method = fdatasync',
            'max_connections = 40',
            'maintenance_work_mem = 192MB',
            'effective_cache_size = 2304MB',
            'work_mem = 64MB',
            'wal_buffers = 4MB',
            'shared_buffers = 768MB',
            'checkpoint_segments = 8',
            'checkpoint_completion_target = 0.7',
            '# track long running queries',
            'track_activity_query_size = 4096',
            'log_min_duration_statement = 4000',
            "log_line_prefix = 'user=%u,db=%d '",
            "statement_timeout = 10min",
        ]) + '\n'
        tmp_fd, tmp_name = tempfile.mkstemp()
        os.write(tmp_fd, conf)
        os.close(tmp_fd)
        cat = subprocess.list2cmdline(['cat', tmp_name])
        tee = subprocess.list2cmdline((['sudo'] if self.use_sudo else []) + ['tee', postgresql_conf])
        local('{0} | {1} > /dev/null'.format(cat, tee))
        os.remove(tmp_name)

    def postgresql_restart(self):
        cmd = '/etc/init.d/postgresql'

        if not os.path.exists(cmd):
            cmd += "-"+ self.postgresql_version()

            if not os.path.exists(cmd):
                abort('could not determine postgres control command {0}'.format(cmd))

        self.local([cmd, 'restart'])

    def pgbouncer_config(self):
        self.write_config_templatedir('pgbouncer', '/', use_sudo=True, filemode= "0640")
        local('sudo chown postgres:postgres -R /etc/pgbouncer')
        local('sudo /etc/init.d/pgbouncer restart')

    def mocca_config(self):
        bkuonline_config_path = os.path.join(get_pythonenv(), "mocca", "conf", "Catalina", "localhost")
        local('if test ! -d {0}; then mkdir -p {0}; fi'.format(bkuonline_config_path))
        self.write_config_template('bkuonline.xml',
            os.path.join(bkuonline_config_path, "bkuonline.xml"),
            context=self.config, use_sudo=True, filemode= '0644')
        self.write_config_template('mocca-configuration.xml',
            os.path.join(get_pythonenv(), "mocca", "conf", "mocca-configuration.xml"),
            context=self.config, use_sudo=True, filemode= '0644')

    def pdfas_config(self):
        self.write_config_template('pdf-as-web.properties',
            os.path.join(get_pythonenv(), "pdfas", "conf", "pdf-as-web.properties"),
            context=self.config, use_sudo=True, filemode= '0644')

    def apache_restart(self):
        local('sudo /etc/init.d/apache2 restart')

    def wsgi_reload(self):
        local('sudo touch /etc/apache2/ecs/apache.wsgi/ecs-wsgi.py')

    def daemons_install(self, extra_env={}):
        control_upstart(self.appname, "install", upgrade=True, use_sudo=self.use_sudo, dry=self.dry, extra_env= extra_env)

    def daemons_stop(self):
        control_upstart(self.appname, "stop", use_sudo=self.use_sudo, fail_soft=True, dry=self.dry)

    def daemons_start(self):
        control_upstart(self.appname, "start", use_sudo=self.use_sudo, dry=self.dry)

    def db_clear(self):
        local("sudo su - postgres -c \'createuser -S -d -R %(postgresql.username)s\' | true" % self.config)


        alter_user='''sudo su - postgres -c "psql -c \\"alter user '''+  self.config['postgresql']['username']+ ' with password \''+ self.config['postgresql']['password']+ '\';\\""'
        local(alter_user)

        if self.destructive:
            local('dropdb %(postgresql.database)s | true' % self.config)
        else:
            warn("Not dropping/destroying database, because destructive=False")
        local('createdb --template=template0 --encoding=utf8 --locale=de_DE.utf8 %(postgresql.database)s | true' % self.config)

    def db_update(self):
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py syncdb --noinput'.format(self.homedir))
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py migrate --noinput'.format(self.homedir))
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py bootstrap'.format(self.homedir))

    def db_dump(self):
        dumpname = '{0}/%(postgresql.database)s.pgdump'.format(self.homedir) % self.config
        cmd = 'pg_dump --encoding="utf-8" --format=custom %(postgresql.database)s --file={0}.new'.format(dumpname)
        local(cmd % self.config)
        shutil.move(dumpname+'.new', dumpname)

    def db_restore(self, prefix=""):
        cmd = 'pg_restore --format=custom --schema=public --dbname=%(postgresql.database)s {0}/{1}%(postgresql.database)s.pgdump'.format(self.homedir, prefix)
        local(cmd % self.config)

    def env_clear(self):
        # todo: implement env_clear
        pass

    def env_boot(self):
        env_bootstrap = ['sudo'] if self.use_sudo else []
        env_bootstrap += [os.path.join(os.path.dirname(env.real_fabfile), 'bootstrap.py'), 'whereever/sdfkljsd']
        pass
        # FIXME implement env_boot

    def env_update(self):
        local('sudo bash -c "cd {0}/src/; . {0}/environment/bin/activate;  fab appreq:ecs,flavor=system"'.format(self.homedir))
        local('cd {0}/src/; . {0}/environment/bin/activate; fab appenv:ecs,flavor=system'.format(self.homedir))

    def queuing_config(self):
        with settings(warn_only=True):
            if is_precise_or_older():
                local('sudo /etc/init.d/rabbitmq-server stop')
                local('sudo killall beam')
                local('sudo killall epmd')
                local('sudo DEBIAN_FRONTEND=noninteractive apt-get -y -q remove --purge rabbitmq-server')
                time.sleep(1)
                local('sudo killall beam')
                local('sudo killall epmd')
                local('sudo DEBIAN_FRONTEND=noninteractive apt-get -y -q install rabbitmq-server')
                local('sudo /etc/init.d/rabbitmq-server start')
                time.sleep(1)
                local('sudo rabbitmqctl stop_app')
                local('sudo rabbitmqctl force_reset')
                local('sudo rabbitmqctl start_app')
                time.sleep(1)

            if int(local('sudo rabbitmqctl list_vhosts | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
                local('sudo rabbitmqctl delete_vhost %(rabbitmq.username)s' % self.config)

            local('sudo rabbitmqctl add_vhost %s' % self.username)

            if int(local('sudo rabbitmqctl list_users | grep %(rabbitmq.username)s | wc -l' % self.config, capture=True)):
                local('sudo rabbitmqctl delete_user %(rabbitmq.username)s ' % self.config)

            local('sudo rabbitmqctl add_user %(rabbitmq.username)s %(rabbitmq.password)s' % self.config)
            local('sudo rabbitmqctl set_permissions -p %(rabbitmq.username)s %(rabbitmq.username)s ".*" ".*" ".*"' % self.config)


    def search_config(self):
        source_schema = os.path.join(self.homedir, 'ecs-conf', 'solr_schema.xml')
        source_jetty =  os.path.join(self.homedir, 'ecs-conf', 'jetty.cnf')
        local('cd {0}/src/ecs; . {0}/environment/bin/activate; ./manage.py build_solr_schema > {1}'.format(
            self.homedir,  source_schema))
        local('sudo cp {0} /etc/solr/conf/schema.xml'.format(source_schema))
        with open(source_jetty, 'w') as f:
            f.write('NO_START=0\nVERBOSE=yes\nJETTY_PORT=8983\nfor a in /usr/lib/jvm/java-7-openjdk*; do JAVA_HOME=$a; done')   # jetty version in precise has no default search list for java-7
        local('sudo cp {0} /etc/default/jetty'.format(source_jetty))
        local('sudo /etc/init.d/jetty stop')
        time.sleep(5)
        local('sudo /etc/init.d/jetty start')
        time.sleep(10) # jetty needs time to startup

    def search_update(self):
        if strbool(self.extra_kwargs.get('search_reindex', True)):
            local('cd {0}/src/ecs; . {0}/environment/bin/activate;  if test -d ../../ecs-whoosh; then rm -rf ../../ecs-whoosh; fi; ./manage.py rebuild_index --noinput '.format(self.homedir))
        else:
            warn('skipping search_update reindex, because you said so.')

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


def tomcat_user(tomcatpath, control_port, http_port, ajp_port):
    if os.path.exists(tomcatpath):
        if os.path.exists(tomcatpath+"-old"):
            shutil.rmtree(tomcatpath+"-old")
        shutil.move(tomcatpath, tomcatpath+"-old")


    tomcatversion = "6" if is_precise_or_older() else "7"
    install = 'tomcat{0}-instance-create -p {1} -c {2} \'{3}\''.format(tomcatversion, http_port, control_port, tomcatpath)
    popen = subprocess.Popen(install, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = popen.communicate()
    returncode = popen.returncode
    if returncode != 0:
        print "Error:", returncode, stdout, stderr
        ret= False
    else:
        ret= True

    if ret:
        write_regex_replace(
            os.path.join(tomcatpath, 'conf', 'server.xml'),
                r'^'+
                r'([ \t]+<!--[ \t]*\n|\r\n)?'+
                r'([ \t]+<Connector port=)"8009"( protocol="AJP/1.3" redirectPort="8443" />[ \t]*\n|\r\n)'+
                r'([ \t]+-->[ \t]*\n|\r\n)?',
                r'\2"'+ str(ajp_port)+ r'"\3', multiline=True)

    return ret


def custom_check_mocca(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "mocca", "webapps", checkfilename))

def custom_install_mocca(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    basedir = os.path.join(get_pythonenv(), "mocca")
    ret = tomcat_user(basedir, 4750, 4780, 4790)
    if ret:
        pkg_manager = get_pkg_manager()
        ret = pkg_manager.static_install_copy(filename, os.path.join(basedir, "webapps"), checkfilename, pkgline)
    return ret

def custom_check_pdfas(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "pdfas", "webapps", checkfilename))

def custom_install_pdfas(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    basedir = os.path.join(get_pythonenv(), "pdfas")
    ret = tomcat_user(basedir, 4755, 4785, 4795)
    if ret:
        pkg_manager = get_pkg_manager()
        ret = pkg_manager.static_install_copy(filename, os.path.join(basedir, "webapps"), checkfilename, pkgline)
    return ret

def custom_check_pdfasconfig(pkgline, checkfilename):
    return os.path.exists(os.path.join(get_pythonenv(), "pdfas", "conf", checkfilename))

def custom_install_pdfasconfig(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    outputdir = os.path.join(get_pythonenv(), "pdfas", "conf", checkfilename)
    pkg_manager = get_pkg_manager()
    result = pkg_manager.static_install_unzip(filename, outputdir, checkfilename, pkgline)
    return result


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


def custom_check_duply(pkgline, checkfilename):
    return os.path.exists(os.path.join(os.path.dirname(get_pythonexe()), checkfilename))

def custom_install_duply(pkgline, filename):
    (name, pkgtype, platform, resource, url, behavior, checkfilename) = packageline_split(pkgline)
    pkg_manager = get_pkg_manager()
    tempdir = tempfile.mkdtemp()
    outputdir = os.path.dirname(get_pythonexe())
    result = False

    try:
        if pkg_manager.static_install_tar(filename, tempdir, checkfilename, pkgline):
            try:
                shutil.copy(os.path.join(tempdir, 'duply_1.5.5.4', checkfilename),
                    os.path.join(outputdir, checkfilename))
            except EnvironmentError:
                pass
            else:
                result = True
    finally:
        shutil.rmtree(tempdir)

    return result
