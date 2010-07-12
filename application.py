# ecs
"""
# package lists format
########################################

general:
 name:type:platform:resourcetype:resource[:additional]*
 name=[a-zA-Z0-9-_]+
 type=(req:inst|instbin)
 platform=(all|[!]?win|[!]?mac|[!]?apt)
 resourcetype=(pypi|http[s]?|ftp|file)
 resource=url or packagelist seperated with space or comma
 additional depends on command
 
type=req
 platform=apt:resourcetype=apt-get:resource=pkglist # can be space or comma seperated
 resource={apt-packagename}[,{apt-packagename}]*
 
 platform=mac:resourcetype=(macports|homebrew):resource=pkglist # can be space or comma seperated
 resource={macports-packagename}[,{macports-packagename}]*

 platform=win:resourcetype=(http[s]?|ftp|file):resource=url:additional=unzip2scripts:additional=executable 
 # executable to be checked if exists in path
 
 platform=win:resourcetype=(http[s]?|ftp|file):resource=url:additional=exe:additional=silentinstall parameter: additional=executable 
 # executable to be checked if exists in path

type=inst
 platform=(all|[!]?win|[!]?mac|[!]?apt)
 resourcetype=(http[s]?|ftp|file):resource=url
 resourcetype=pypi:resource={pypiname}[(\>|\>=|==){version}]?
 # WARNING: pypi version using > needs backslash !

type=instbin
 platform=win
 resourcetype=(http[s]?|ftp|file)
 
"""

from deployment import package_merge

# sprint 7 sources
sprint7_bundle = """

# database bindings
psycopg2:req:apt:apt-get:libpq-dev
psycopg2:req:mac:macports:postgresql84-server
psycopg2:inst:!win:pypi:psycopg2
psycopg2:instbin:win:http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.0.13.win32-py2.6-pg8.4.1-release.exe
pysqlite:req:apt:apt-get:libsqlite3-dev
pysqlite:req:mac:macports:sqlite3
pysqlite:inst:!win:pypi:pysqlite
pysqlite:instbin:win:http://pysqlite.googlecode.com/files/pysqlite-2.5.6.win32-py2.6.exe

# timezone handling
pytz:inst:all:pypi:pytz

# django main
django:inst:all:pypi:django==1.2.1
south:inst:all:pypi:south
django-piston:inst:all:http://bitbucket.org/jespern/django-piston/get/default.gz
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
# docstash now uses django-picklefield
django-picklefield:inst:all:pypi:django-picklefield
django_compressor:inst:all:http://github.com/mintchaos/django_compressor/tarball/master
docutils:inst:all:pypi:docutils
django-dbtemplates:inst:all:pypi:django-dbtemplates

#search
whoosh:inst:all:pypi:whoosh
django-haystack:inst:all:pypi:http://github.com/toastdriven/django-haystack/tarball/master
poppler:req:apt:apt-get:poppler-utils
poppler:req:mac:macports:poppler
poppler:req:win:ftp://ftp.gnome.org/Public/GNOME/binaries/win32/dependencies/poppler-dev_0.12.0-1_win32.zip:unzip2scripts:pdftotext.exe

# simple testing
nose:inst:all:pypi:nose
django-nose:inst:all:http://github.com/jbalogh/django-nose/tarball/master

#debugging
werkzeug:inst:all:pypi:werkzeug
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
django-db-log:inst:all:pypi:django-db-log

# needed for deployment: massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
antiword:req:win:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:unzip2scripts:antiword.exe
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
# needed for massimport statistic function
mpmath:inst:all:pypi:mpmath

# pisa
pyPDF:inst:all:pypi:pyPDF
html5lib:inst:all:pypi:html5lib
reportlab:req:apt:apt-get:libfreetype6-dev
reportlab:inst:!win:pypi:reportlab
reportlab:instbin:win:http://pypi.python.org/packages/2.6/r/reportlab/reportlab-2.3.win32-py2.6.exe
pisa:inst:all:pypi:pisa

# celery 
amqplib:inst:all:pypi:amqplib
carrot:inst:all:pypi:carrot
importlib:inst:all:pypi:importlib
python-dateutil:inst:all:pypi:python-dateutil
mailer:inst:all:pypi:mailer
sqlalchemy:inst:all:pypi:sqlalchemy
anyjson:inst:all:pypi:anyjson
billard:inst:all:pypi:billiard
django-picklefield:inst:all:pypi:django-picklefield
celery:req:apt:apt-get:rabbitmq-server
celery:req:mac:macports:rabbitmq-server
celery:inst:all:pypi:celery
# use ghettoq if development instead rabbitmq
ghettoq:inst:all:pypi:ghettoq
pyparsing:inst:all:pypi:pyparsing
django-celery:inst:all:pypi:django-celery

# media server rendering (includes mockcache for easier testing)
ghostscript:req:apt:apt-get:ghostscript
ghostscript:req:mac:macports:ghostscript
#ghostscript:req:win:http://ghostscript.com/releases/gs871w32.exe:exe:--silent:gs.exe
memcachedb:req:apt:apt-get:memcachedb
# FIXME: there is no memcachedb macport yet
python-memcached:req:mac:macports:memcached
python-memcached:inst:all:pypi:python-memcached
mockcache:inst:all:pypi:mockcache
python-pil:req:apt:apt-get:libjpeg62-dev,zlib1g-dev,libfreetype6-dev,liblcms1-dev
python-pil:inst:!win:pypi:PIL
python-pil:instbin:win:http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe

#barcode stamping
pdftk:req:apt:apt-get:pdftk
pdftk:req:win:http://www.pdfhacks.com/pdftk/pdftk-1.41.exe.zip:unzip2scripts:pdftk.exe
#pdftk:req:mac:dmg:http://fredericiana.com/downloads/pdftk1.41_OSX10.6.dmg

# lamson mail server
chardet:inst:all:pypi:chardet
jinja2:inst:all:pypi:jinja2
lockfile:inst:all:pypi:lockfile
mock:inst:all:pypi:mock
python-daemon:inst:!win:pypi:python-daemon==1.5.5
lamson:inst:all:pypi:lamson
beautifulcleaner:inst:all:http://github.com/downloads/enki/beautifulcleaner/BeautifulCleaner-2.0dev.tar.gz
"""

# software quality testing packages
quality_packages= """
# nose and django-nose is in main app
unittest-xml-reporting:inst:all:pypi:unittest-xml-reporting
coverage:inst:!win:pypi:coverage
nose-xcover:inst:!win:http://github.com/cmheisel/nose-xcover/tarball/master
coverage:instbin:win:http://pypi.python.org/packages/2.6/c/coverage/coverage-3.2.win32-py2.6.exe
logilab-common:inst:all:pypi:logilab-common\>=0.49.0
logilab-astng:inst:all:pypi:logilab-astng\>=0.20.0
pylint:inst:all:pypi:pylint
#django-lint:inst:all:http://chris-lamb.co.uk/releases/django-lint/LATEST/django-lint-0.13.tar.gz
"""


# In addition to application packages, packages needed for development
developer_packages=  """
ipython:inst:win:pypi:pyreadline
ipython:inst:all:pypi:ipython
docutils:inst:all:pypi:docutils
sphinx:inst:all:pypi:sphinx
# fudge:inst:all:pypi:fudge
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
simplejson:inst:all:pypi:simplejson
# antiword is needed for ecs/core/management/massimport.py (were we load word-doc-type submission documents into the database)
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
antiword:req:win:unzip2scripts:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:antiword.exe
#graphviz is required for manage.py graph_models
# graphviz:req:apt:apt-get:graphviz-dev
# graphviz:inst:apt:pypi:pygraphviz
levenshtein:inst:!win:http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
"""
# required for django_extensions unittests:
#pycrypto:inst:all:pypi:pycrypto>=2.0
#pyasn1:inst:all:pypi:pyasn1
#keyczar:inst:all:http://keyczar.googlecode.com/files/python-keyczar-0.6b.061709.tar.gz


# TODO: make system environment for sprint 7
sprint7_ecs_machine = """apache, mod_wsgi, exim4"""


# Environments
###############

testing_bundle = sprint7_bundle
default_bundle = sprint7_bundle
future_bundle = sprint7_bundle
developer_bundle = package_merge((default_bundle, quality_packages, developer_packages))
quality_bundle = package_merge((default_bundle, quality_packages))


package_bundles = {
    'default': default_bundle,
    'testing': testing_bundle,
    'future': future_bundle,
    'sprint7': sprint7_bundle,
    'developer': developer_bundle,
    'quality': quality_bundle,
    'qualityaddon': quality_packages,
}

upstart_flavors = {
    'default': './manage.py runserver',
    'mainapp': './manage.py runserver',
    'mediaserver': './manage.py celeryd',
    'logmailserver': './manage.py ecsmail log',
    'mailserver': './manage.py ecsmail server',
    'signing': 'true',   # FIXME: how to do this?
}

test_flavors = {
    'default': './manage.py test',
    'mainapp': './manage.py test',
    'mediaserver': 'false',  # TODO: implement
    'logmailserver': 'false', # TODO: implement
    'mailserver': '.false', # TODO: implement
    'signing': 'false', # TODO: implement
}

"""
class job:
    def __init__(self, app, user, base, src, environment):
        self.src    = os.abspath(src)
        self.config = os.abspath(config)
        self.environment = os.abspath(environment)
        self.user = user
        self.app = app
        
    def _get_config_pairs(self):
        raise NotImplementedError

    def _config_target(self, configsetpair):
        return configpair[1]
        
    def _config_source(self, template):
        return configpair[0]
        return = os.path.join(self.src, self.app, configpair[0])
    
    def _generate_config_from_template(self, template):
        target_conf = self._config_target(template)
        template_conf = self._config_source(template)
        context = {
            'appdir': os.path.join(self.src, self.app),
            'user': self.user,
            'environment': self.environment
        }
        write_template(template_conf, target_conf, context)

    def _link_config(self, template):
        raise NotImplementedError
        
    def register(self):
        for template in self._get_templates()
            self._generate_from_template(self, template)
            if os.path.exists (self._template_target(template):
               if os.shutil.compare(self._template_target

    def setup(self):
    def register(self):
    def stop(self):
    def start(self):
    def status(self):

class wsgijob(job):
    def __init__(self, user, base, environment):
    def _template_target(self, template)
        return = os.path.join(self.config, "upstart.conf", "-".join(self.app,template))
       
    
class upstartjob(job):
    def __init__(self, user, target, environment):
"""
    

