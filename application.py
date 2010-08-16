# ecs main application environment config

"""
# package lists format
########################################

general:
 name:type:platform:resourcetype:resource[:optional]*
 name=[a-zA-Z0-9-_]+
 type=(req:inst|instbin)
 platform=(all|[!]?win|[!]?mac|[!]?apt)
 resourcetype=(pypi|http[s]?|ftp|file|dir)
 resource=url or packagelist seperated with space or comma
 optional depends on command
 
type=req  # third party packages not written in python
 platform=apt:resourcetype=apt-get:resource=pkglist # can be space or comma seperated
 resource={apt-packagename}[,{apt-packagename}]*
 
 platform=mac:resourcetype=(macports|homebrew):resource=pkglist # can be space or comma seperated
 resource={macports-packagename}[,{macports-packagename}]*

 platform=win:resourcetype=(http[s]?|ftp|file):resource=url:additional=(unzipflat|unzipflatmain):additional=executable 
 # executable= to be checked if exists in path, package is considered installed if found
 unzipflat unzips all files in zip file to one directory where they will be in path (Scripts directory on windwos)
 unzipflatmain unzips only first directory level above and including rootdir of zipfile to one directory -,,-
 
type=inst # python libraries to install and use
 platform=(all|[!]?win|[!]?mac|[!]?apt)
 resourcetype=(http[s]?|ftp|file):resource=url
 resourcetype=pypi:resource={pypiname}[(\>|\>=|==){version}]?
 # WARNING: pypi version using > or < needs backslash !

type=instbin # precompiled python libraries to install and use
 platform=win
 resourcetype=(http[s]?|ftp|file)
 installes a binary version of a python package (which is equivalent to unzip self extracting exe to libs)
 
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
# django-haystack currently has an issue with whoosh 1.x, so we use 0.3.18 or therelike
whoosh:inst:all:pypi:whoosh\<=0.4
# pysolr uses httplib2 with fallback to httplib
httplib2:inst:all:pypi:httplib2
pysolr:inst:all:pypi:pysolr
django-haystack:inst:all:http://github.com/toastdriven/django-haystack/tarball/master
pdftotext:req:apt:apt-get:poppler-utils
pdftotext:req:mac:macports:poppler
pdftotext:req:win:http://gd.tuwien.ac.at/publishing/xpdf/xpdf-3.02pl4-win32.zip:unzipflat:pdftotext.exe

# simple testing
nose:inst:all:pypi:nose
django-nose:inst:all:pypi:django-nose
#http://github.com/jbalogh/django-nose/tarball/master

#debugging
werkzeug:inst:all:pypi:werkzeug
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
# did throw errors in own code itself, instead of doing its job of logging errors django-db-log:inst:all:pypi:django-db-log

# needed for deployment: massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
antiword:req:win:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:unzipflat:antiword.exe
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
# needed for massimport statistic function
mpmath:inst:all:pypi:mpmath

# pdf validation
pdfminer:inst:all:pypi:pdfminer

# pisa / pdf generation
# deprecated for ecs in favour of pdfminer, and optional for pisa:  pyPDF:inst:all:pypi:pyPDF
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
#celery:req:apt:apt-get:rabbitmq-server
celery:req:mac:macports:rabbitmq-server
celery:inst:all:pypi:celery
# use ghettoq if development instead rabbitmq
ghettoq:inst:all:pypi:ghettoq
pyparsing:inst:all:pypi:pyparsing
django-celery:inst:all:pypi:django-celery

# pdf document server rendering (includes mockcache for easier testing)
ghostscript:req:apt:apt-get:ghostscript
ghostscript:req:mac:macports:ghostscript
#ghostscript:req:win:http://ghostscript.com/releases/gs871w32.exe:exe::gswin32c.exe needs a portable exe file not that, but the url for now
imagemagick:req:apt:apt-get:imagemagick
imagemagick:req:mac:macports:imagemagick
imagemagick:req:win:http://www.imagemagick.org/download/binaries/ImageMagick-6.6.3-Q16-windows.zip:unzipflatmain:montage.exe
# we check for montage.exe because on windows convert.exe exists already ... :-(
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
pdftk:req:win:http://www.pdfhacks.com/pdftk/pdftk-1.41.exe.zip:unzipflat:pdftk.exe
#pdftk:req:mac:dmg:http://fredericiana.com/downloads/pdftk1.41_OSX10.6.dmg

# lamson mail server
chardet:inst:all:pypi:chardet
jinja2:inst:all:pypi:jinja2
lockfile:inst:all:pypi:lockfile
mock:inst:all:pypi:mock
# we dont use python-daemon functionality in lamson, but lamson.utils imports daemon, so we fake it for windows
python-daemon:inst:!win:pypi:python-daemon==1.5.5
python-daemon:inst:win:dir:ecs/utils/fake-daemon/
lamson:inst:all:pypi:lamson
beautifulcleaner:inst:all:http://github.com/downloads/enki/beautifulcleaner/BeautifulCleaner-2.0dev.tar.gz

# excel output
xlwt:inst:all:pypi:xlwt
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


# In addition to application packages, packages needed or nice to have for development
developer_packages=  """
# mutt is needed if you what to have an easy time with mail and lamson for testing, use it with mutt -F ecsmail/muttrc
mutt:req:apt:apt-get:mutt
mutt:req:win:http://download.berlios.de/mutt-win32/mutt-win32-1.5.9-754ea0f091fc-2.zip:unzipflat:mutt.exe
mutt:req:mac:macports:mutt
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
antiword:req:win:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:unzipflat:antiword.exe
#graphviz is required for manage.py graph_models
# graphviz:req:apt:apt-get:graphviz-dev
# graphviz:inst:apt:pypi:pygraphviz
#FIXME: who needs levenshtein ?
levenshtein:inst:!win:http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
"""
# required for django_extensions unittests:
#pycrypto:inst:all:pypi:pycrypto>=2.0
#pyasn1:inst:all:pypi:pyasn1
#keyczar:inst:all:http://keyczar.googlecode.com/files/python-keyczar-0.6b.061709.tar.gz


system_packages = """
# ecs-main via wsgi
apache2:req:apt:apt-get:apache2-mpm-prefork
modwsgi:req:apt:apt-get:libapache2-mod-wsgi
postgresql:req:apt:apt-get:postgresql
exim:req:apt:apt-get:exim4
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

testing_bundle = sprint7_bundle
default_bundle = sprint7_bundle
future_bundle = sprint7_bundle
developer_bundle = package_merge((default_bundle, quality_packages, developer_packages))
quality_bundle = package_merge((default_bundle, quality_packages))
system_bundle = package_merge((default_bundle, system_packages))

package_bundles = {
    'default': default_bundle,
    'testing': testing_bundle,
    'future': future_bundle,
    'sprint7': sprint7_bundle,
    'developer': developer_bundle,
    'quality': quality_bundle,
    'qualityaddon': quality_packages,
    'system': system_bundle,
}

upstart_targets = {
    'mainapp_celery': './manage.py celeryd',
    'mailserver': './manage.py ecsmail server',
}

test_flavors = {
    'default': './manage.py test',
    'mainapp': './manage.py test',
    'mediaserver': 'false',  # TODO: implement
    'logmailserver': 'false', # TODO: implement
    'mailserver': '.false', # TODO: implement
    'signing': 'false', # TODO: implement
}
