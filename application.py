# ecs main application environment config

import os
import subprocess
import getpass

from uuid import uuid4
from fabric.api import local, env
from deployment.utils import package_merge, install_upstart, apache_setup, write_template


# packages needed for the application
main_packages = """

# postgresql database bindings
psycopg2:req:apt:apt-get:libpq-dev
psycopg2:req:mac:macports:postgresql84-server
psycopg2:req:suse:zypper:postgresql-devel
psycopg2:req:openbsd:pkg:postgresql-server
psycopg2:req:openbsd:pkg:postgresql-client
psycopg2:inst:!win:pypi:psycopg2
psycopg2:instbin:win:http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.0.13.win32-py2.6-pg8.4.1-release.exe

# sqlite database bindings
pysqlite:req:apt:apt-get:libsqlite3-dev
pysqlite:req:mac:macports:sqlite3
pysqlite:req:suse:zypper:sqlite3-devel
pysqlite:req:openbsd:pkg:sqlite3
pysqlite:inst:!win:pypi:pysqlite
pysqlite:instbin:win:http://pysqlite.googlecode.com/files/pysqlite-2.5.6.win32-py2.6.exe

# timezone handling
pytz:inst:all:pypi:pytz


# django main
django:inst:all:pypi:django==1.2.3
south:inst:all:pypi:south
django-piston:inst:all:http://bitbucket.org/jespern/django-piston/get/default.gz
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
# docstash now uses django-picklefield
django-picklefield:inst:all:pypi:django-picklefield
django_compressor:inst:all:http://github.com/mintchaos/django_compressor/tarball/master
docutils:inst:all:pypi:docutils
django-dbtemplates:inst:all:pypi:django-dbtemplates
# django caching uses memcache if available
python-memcached:inst:all:pypi:python-memcached

# testing
nose:inst:all:pypi:nose
django-nose:inst:all:pypi:django-nose


# queuing: celery 
amqplib:inst:all:pypi:amqplib\>=0.6
carrot:inst:all:pypi:carrot\>=0.10.7
importlib:inst:all:pypi:importlib
python-dateutil:inst:all:pypi:python-dateutil
anyjson:inst:all:pypi:anyjson
pyparsing:inst:all:pypi:pyparsing
celery:inst:all:pypi:celery\>=2.1.2

django-picklefield:inst:all:pypi:django-picklefield
django-celery:inst:all:pypi:django-celery\>=2.1.2

# use ghettoq if development instead rabbitmq
odict:inst:all:pypi:odict
ghettoq:inst:all:pypi:ghettoq


# mail: ecsmail, communication: lamson mail server
chardet:inst:all:pypi:chardet
jinja2:inst:all:pypi:jinja2
lockfile:inst:all:pypi:lockfile
mock:inst:all:pypi:mock
nose:inst:all:pypi:nose
# we dont use python-daemon functionality in lamson, but lamson.utils imports daemon and fails
# so we fake it for windows and right now also for the rest, was python-daemon:inst:!win:pypi:python-daemon==1.5.5
python-daemon:inst:all:dir:ecs/utils/fake-daemon/
lamson:inst:all:pypi:lamson
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
beautifulcleaner:inst:all:http://github.com/downloads/enki/beautifulcleaner/BeautifulCleaner-2.0dev.tar.gz


# ecs/mediaserver: file encryption, used for storage vault 
gnupg:req:apt:apt-get:gnupg
gnupg:req:mac:macports:gnupg
gnupg:req:mac:homebrew:gnupg
gnupg:req:suse:zypper:gpg2
gnupg:req:openbsd:pkg:gnupg
gnupg:req:win:ftp://ftp.gnupg.org/gcrypt/binary/gnupg-w32cli-1.4.10b.exe:exec:gpg.exe


# search
# XXX: haystack should be compatible to whoosh>0.4 but it seems not to be
whoosh:inst:all:pypi:whoosh\<=0.4
# pysolr uses httplib2 with fallback to httplib
httplib2:inst:all:pypi:httplib2
pysolr:inst:all:pypi:pysolr
django-haystack:inst:all:http://github.com/toastdriven/django-haystack/tarball/master
# pdf text extract
pdftotext:req:apt:apt-get:poppler-utils
pdftotext:req:mac:macports:poppler
pdftotext:req:suse:zypper:poppler-tools
pdftotext:req:openbsd:pkg:poppler
pdftotext:req:openbsd:pkg:poppler-data
pdftotext:req:win:http://gd.tuwien.ac.at/publishing/xpdf/xpdf-3.02pl4-win32.zip:unzipflat:pdftotext.exe

# excel generation / xlwt
xlwt:inst:all:pypi:xlwt


# pdf generation / pisa
# pyPDF is deprecated for ecs in favour of pdfminer, and optional for pisa:  pyPDF:inst:all:pypi:pyPDF
html5lib:inst:all:pypi:html5lib
reportlab:req:apt:apt-get:libfreetype6-dev
reportlab:inst:!win:pypi:reportlab
reportlab:instbin:win:http://pypi.python.org/packages/2.6/r/reportlab/reportlab-2.3.win32-py2.6.exe
pisa:inst:all:pypi:pisa


# (ecs/mediaserver): pdf validation (is_valid, pages_nr)
pdfminer:inst:all:pypi:pdfminer


# mediaserver image generation
# ############################

# pdf manipulation, barcode stamping
pdftk:req:apt:apt-get:pdftk
pdftk:req:win:http://www.pdfhacks.com/pdftk/pdftk-1.41.exe.zip:unzipflat:pdftk.exe
# Available in: http://packman.mirrors.skynet.be/pub/packman/suse/11.3/Packman.repo
pdftk:req:suse:zypper:pdftk
# Mac OS X: get pdftk here: http://www.pdflabs.com/docs/install-pdftk/
#pdftk:req:mac:dmg:http://fredericiana.com/downloads/pdftk1.41_OSX10.6.dmg
# OpenBSD: build pdftk yourself: http://www.pdflabs.com/docs/build-pdftk/

# mediaserver: python-memcached (and mockcache for testing) 
python-memcached:inst:all:pypi:python-memcached
mockcache:inst:all:pypi:mockcache

# mediaserver: needs ghostscript for rendering
ghostscript:req:apt:apt-get:ghostscript
ghostscript:req:mac:macports:ghostscript
ghostscript:req:suse:zypper:ghostscript-library
ghostscript:req:openbsd:pkg:ghostscript--
ghostscript:req:win:http://ghostscript.com/releases/gs871w32.exe:exec:gswin32c.exe

# mediaserver: image magick is used for rendering tasks as well
imagemagick:req:apt:apt-get:imagemagick
imagemagick:req:mac:macports:imagemagick
imagemagick:req:suse:zypper:ImageMagick
imagemagick:req:openbsd:pkg:ImageMagick--
# we check for montage.exe because on windows convert.exe exists already ... :-(
imagemagick:req:win:ftp://ftp.imagemagick.org/pub/ImageMagick/binaries/ImageMagick-6.6.5-Q16-windows.zip:unzipflatsecond:montage.exe

python-pil:req:apt:apt-get:libjpeg62-dev,zlib1g-dev,libfreetype6-dev,liblcms1-dev
# PIL requirements for opensuse
libjpeg-devel:req:suse:zypper:libjpeg-devel
zlib-devel:req:suse:zypper:zlib
freetype2-devel:req:suse:zypper:freetype2-devel
liblcms1:req:suse:zypper:liblcms1
python-pil:inst:!win:pypi:PIL
python-pil:instbin:win:http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe

# deployment: manage.py massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
# antiword has to be build by hand for opensuse
#antiword:req:suse:zypper:antiword
antiword:req:openbsd:pkg:antiword
antiword:req:win:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:unzipflat:antiword.exe
# antiword is needed for ecs/core/management/massimport.py (were we load word-doc-type submission documents into the database)
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
# mpmath needed for massimport statistic function
mpmath:inst:all:pypi:mpmath

# feedback: jsonrpclib for ecs feedback and fab ticket
jsonrpclib:inst:all:file:externals/joshmarshall-jsonrpclib-283a2a9-ssl_patched.tar.gz

# debugging
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master

# logging: django-sentry
django-indexer:inst:all:pypi:django-indexer
django-paging:inst:all:pypi:django-paging
django-templatetag-sugar:inst:all:pypi:django-templatetag-sugar
pygooglechart:inst:all:pypi:pygooglechart
django-sentry:inst:all:pypi:django-sentry

# diff_match_patch is used for the submission diff
diff_match_patch:inst:all:http://github.com/pinax/diff-match-patch/tarball/master

"""


# software quality testing packages, not strictly needed, except you do coverage analysis
quality_packages= """
# nose and django-nose is in main app
unittest-xml-reporting:inst:all:pypi:unittest-xml-reporting
coverage:inst:!win:pypi:coverage\<3.4
coverage:instbin:win:http://pypi.python.org/packages/2.6/c/coverage/coverage-3.2.win32-py2.6.exe
nose-xcover:inst:all:http://github.com/cmheisel/nose-xcover/tarball/master
logilab-common:inst:all:pypi:logilab-common\>=0.49.0
logilab-astng:inst:all:pypi:logilab-astng\>=0.20.0
pylint:inst:all:pypi:pylint
#django-lint:inst:all:http://chris-lamb.co.uk/releases/django-lint/LATEST/django-lint-0.13.tar.gz
"""


# packages needed or nice to have for development
developer_packages=  """
# dependency generation for python programs
sfood:inst:all:pypi:snakefood

# mutt is needed if you what to have an easy time with mail and lamson for testing, use it with mutt -F ecsmail/muttrc
mutt:req:apt:apt-get:mutt
mutt:req:suse:zypper:mutt
mutt:req:win:http://download.berlios.de/mutt-win32/mutt-win32-1.5.9-754ea0f091fc-2.zip:unzipflat:mutt.exe
mutt:req:mac:macports:mutt

# interactive python makes your life easier
ipython:inst:win:pypi:pyreadline
ipython:inst:all:pypi:ipython

simplejson:inst:all:pypi:simplejson
# deployment: massimport statistics and diff-match-patch
levenshtein:inst:!win:http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
"""
# required for django_extensions unittests:
#pycrypto:inst:all:pypi:pycrypto>=2.0
#pyasn1:inst:all:pypi:pyasn1
#keyczar:inst:all:http://keyczar.googlecode.com/files/python-keyczar-0.6b.061709.tar.gz

# maybe interesting: fudge:inst:all:pypi:fudge


# packages needed for full production rollout (eg. VM Rollout)
system_packages = """
# apache via modwsgi is used to serve the main app
apache2:req:apt:apt-get:apache2-mpm-prefork
modwsgi:req:apt:apt-get:libapache2-mod-wsgi

# postgresql is used as primary database
postgresql:req:apt:apt-get:postgresql

# exim is used as incoming smtp firewall and as smartmx for outgoing mails
exim:req:apt:apt-get:exim4

# solr is used for fulltext indexing
solr-jetty:req:apt:apt-get:solr-jetty

# rabbitmq is used as AMPQ Broker in production
rabbitmq-server:req:apt:apt-get:rabbitmq-server
#rabbitmq-server:req:mac:macports:rabbitmq-server
# available here: http://www.rabbitmq.com/releases/rabbitmq-server/v2.1.0/rabbitmq-server-2.1.0-1.suse.noarch.rpm
# uncomment is if there is a possibility to specify repositories for suse
#rabbitmq-server:req:suse:zypper:rabbitmq-server

# Memcached is used for django caching, and the mediaserver uses memcached for its docshot caching
memcached:req:apt:apt-get:memcached
#memcached:req:mac:macports:memcached
#memcached:req:suse:zypper:memcached
#memcached:req:win:http://splinedancer.com/memcached-win32/memcached-1.2.4-Win32-Preview-20080309_bin.zip:unzipflatroot:memcached.exe
# btw, we only need debian packages in the system_packages, but it doesnt hurt to fillin for others 
"""

"""
# should install exim4 and config it instead of postfix; Later
# needs mod_wsgi enabled
a2enmod wsgi #should be automatic active because is extra package
# modify /etc/apache2/mods-enabled/wsgi.conf (is symlink, delete that, copy file from ../mods-available, edit it)
 # where the empty python environment is taken from: For this server it is at user ecsdev directory baseline
 WSGIPythonHome /home/ecsdev/baseline
 # create a baseline python environment (this is a minimal virtual env)
 ./bootstrap.py --baseline /home/ecsdev/baseline
# needs apache config snippet (see apache.conf)
# needs apache wsgi snippet (see main.wsgi)
# these should not be generated inside the sourcedir, because main.wsgi is restarted if file is touched
# needs ecs-main application celeryd upstart.conf
# needs mediaserver application celeryd upstart.conf
"""


# Environments
###############

testing_bundle = main_packages
default_bundle = main_packages
future_bundle = main_packages
developer_bundle = package_merge((default_bundle, quality_packages, developer_packages))
quality_bundle = package_merge((default_bundle, quality_packages))
system_bundle = package_merge((default_bundle, system_packages))

package_bundles = {
    'default': default_bundle,
    'testing': testing_bundle,
    'future': future_bundle,
    'developer': developer_bundle,
    'quality': quality_bundle,
    'qualityaddon': quality_packages,
    'system': system_bundle,
}

logrotate_targets = {
    'default': '*.log'
}

upstart_targets = {
    'celeryd': './manage.py celeryd -l warning -L ../../ecs-log/celeryd.log',
    'celerybeat': './manage.py celerybeat -S djcelery.schedulers.DatabaseScheduler -l warning -L ../../ecs-log/celerybeat.log',
    'ecsmail': './manage.py ecsmail server ../../ecs-log/ecsmail.log', 
}

test_flavors = {
    'default': './manage.py test',
    'mainapp': './manage.py test',
    'mediaserver': 'false',  # include in the mainapp tests
    'mailserver': 'false', # included in the mainapp tests
}


class SetupApplication(object): 
    def __init__(self, use_sudo=True, dry=False, hostname=None, ip=None):
        self.use_sudo = use_sudo
        self.dry = dry
        self.hostname = hostname
        self.ip = ip
        self.appname = 'ecs'
        self.dirname = os.path.dirname(__file__)
        self.username = getpass.getuser()
        self.queuing_password = uuid4().get_hex()
    
    def update(self, *args):
        pass
    
    def system_setup(self):
        self.homedir_config()
        self.sslcert_config()
        self.upstart_install()
        self.apache_config()
        """ install_logrotate(appname, use_sudo=use_sudo, dry=dry)"""
        self.env_baseline()
        self.local_settings_config()
        self.db_clear()
        self.db_update()
        self.queuing_config()                       
        self.search_config()
 
    def homedir_config(self):   
        os.mkdir(os.path.join(os.path.expanduser('~'), 'public_html'))
        
    def sslcert_config(self):
        local('sudo openssl req -config /root/ssleay.cnf -nodes -new -newkey rsa:1024 -days 365 -x509 -keyout /etc/ssl/private/%s.key -out /etc/ssl/certs/%s.pem' %
        (self.hostname, self.hostname))
    
    def local_settings_config(self):
        local_settings = open(os.path.join(self.dirname, 'local_settings.py'), 'w')
        local_settings.write("""
# database settings
local_db = {
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
            {'appdir': os.path.join(self.dirname), 'appname': self.appname,}
            )
        write_template(os.path.join(self.dirname, "templates", "apache2", self.appname, "apache.wsgi", "ecs-service.wsgi"),
            os.path.join(self.dirname, "service.wsgi"), 
            {'appdir': os.path.join(self.dirname), 'appname': self.appname,}
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
        local("sudo su - postgres -c \'createuser -S -d -R %s\'" % (self.username))
        local('dropdb %s' % self.username)
        local('createdb %s' % self.username)
         
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
        local('sudo rabbitmqctl set_permissions -p %s %s "" ".*" ".*"' % (self.username, self.username))

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
        local('sudo cp ~%s /etc/default/jetty' % self.username)
        local('sudo /etc/init.d/jetty start')

    def search_update(self):
        pass
    def massimport(self):
        pass

def wsgi_config(appname, use_sudo=True, dry=False, hostname=None, ip=None):
    s = SetupApplication(use_sudo, dry, hostname, ip)
    s.wsgi_config(
                  )
def system_setup(appname, use_sudo=True, dry=False, hostname=None, ip=None):
    s = SetupApplication(use_sudo, dry, hostname, ip)
    s.system_setup()
    
