# ecs

from deployment import package_merge

# package lists
########################################
# name:{type=inst/req}:{platform=all|[!]?(win|apt|mac)}:{resourcetype=pypi|http[s]?|file|apt-get|macports}:{resource}
# * resourcetype=pypi
#   * resource={pypiname}[(\>|\>=|==){version}]?
# * resourcetype=apt-get
#   * resource={apt-packagename}[,{apt-packagename}]*
# WARNING: pypi version using > needs backslash !

# SQL Adapter, and timezone service, may move into service 
minimal_ecs_service = """
psycopg2:req:apt:apt-get:libpq-dev
psycopg2:req:mac:macports:postgresql84-server
psycopg2:inst:!win:pypi:psycopg2
psycopg2:instbin:win:http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.0.13.win32-py2.6-pg8.4.1-release.exe
pysqlite:req:apt:apt-get:libsqlite3-dev
pysqlite:req:mac:macports:sqlite3
pysqlite:inst:!win:pypi:pysqlite
pysqlite:instbin:win:http://pysqlite.googlecode.com/files/pysqlite-2.5.6.win32-py2.6.exe
pytz:inst:all:pypi:pytz
"""

# sprint 4 Sources
# * modified: south from 0.6.2 to 0.7 
# * added pyPDF, html5lib, reportlab (libfreetype6-dev): (prerequisites for pisa) and pisa
# * added django-db-log for logging of errors to database
sprint4_bundle = minimal_ecs_service+ """ 
django:inst:all:pypi:django==1.1.1
south:inst:all:pypi:south==0.7
django-piston:inst:all:http://bitbucket.org/jespern/django-piston/get/default.gz
werkzeug:inst:all:pypi:werkzeug
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
django-nose:inst:all:http://github.com/jbalogh/django-nose/tarball/master
nose:inst:all:pypi:nose
docutils:inst:all:pypi:docutils
django-reversion:inst:all:pypi:django-reversion
pyPDF:inst:all:pypi:pyPDF
html5lib:inst:all:pypi:html5lib
reportlab:req:apt:apt-get:libfreetype6-dev
reportlab:inst:!win:pypi:reportlab
reportlab:instbin:win:http://pypi.python.org/packages/2.6/r/reportlab/reportlab-2.3.win32-py2.6.exe
pisa:inst:all:pypi:pisa
django-db-log:inst:all:pypi:django-db-log
"""


# sprint 5 sources
sprint5_bundle = minimal_ecs_service+ """ 
django:inst:all:pypi:django==1.1.1
south:inst:all:pypi:south==0.7
django-piston:inst:all:http://bitbucket.org/jespern/django-piston/get/default.gz
werkzeug:inst:all:pypi:werkzeug
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
django-nose:inst:all:http://github.com/jbalogh/django-nose/tarball/django-1.1
nose:inst:all:pypi:nose
docutils:inst:all:pypi:docutils
django-reversion:inst:all:pypi:django-reversion
django-db-log:inst:all:pypi:django-db-log
# docstash now uses django-picklefield
django-picklefield:inst:all:pypi:django-picklefield

# needed for deployment: massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
# antiword:req:win:unzip2path:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1

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
anyjson:inst:all:pypi:anyjson
billard:inst:all:pypi:billiard
django-picklefield:inst:all:pypi:django-picklefield
celery:req:apt:apt-get:rabbitmq-server
celery:req:mac:macports:rabbitmq-server
celery:inst:all:pypi:celery
# use ghettoq if development instead rabbitmq
ghettoq:inst:all:pypi:ghettoq

# media server rendering (includes mockcache for easier testing)
ghostscript:req:apt:apt-get:ghostscript
ghostscript:req:mac:macports:ghostscript
memcachedb:req:apt:apt-get:memcachedb
# FIXME: there is no memcachedb macport yet
python-memcached:req:mac:macports:memcached
python-memcached:inst:all:pypi:python-memcached
mockcache:inst:all:pypi:mockcache
python-pil:req:apt:apt-get:libjpeg62-dev,zlib1g-dev,libfreetype6-dev,liblcms1-dev
python-pil:inst:!win:http://effbot.org/media/downloads/PIL-1.1.7.tar.gz
python-pil:instbin:win:http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe
"""


# sprint 6 sources
sprint6_bundle = minimal_ecs_service+ """
django:inst:all:pypi:django==1.2.1
south:inst:all:pypi:south==0.7
django-piston:inst:all:http://bitbucket.org/jespern/django-piston/get/default.gz
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
# docstash now uses django-picklefield
django-picklefield:inst:all:pypi:django-picklefield
django_compressor:inst:all:http://github.com/mintchaos/django_compressor/tarball/master
docutils:inst:all:pypi:docutils

#debugging
werkzeug:inst:all:pypi:werkzeug
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
django-db-log:inst:all:pypi:django-db-log

# simple testing
nose:inst:all:pypi:nose
django-nose:inst:all:http://github.com/jbalogh/django-nose/tarball/master

# needed for deployment: massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
# antiword:req:win:unzip2path:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
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
anyjson:inst:all:pypi:anyjson
billard:inst:all:pypi:billiard
django-picklefield:inst:all:pypi:django-picklefield
celery:req:apt:apt-get:rabbitmq-server
celery:req:mac:macports:rabbitmq-server
celery:inst:all:pypi:celery
# use ghettoq if development instead rabbitmq
ghettoq:inst:all:pypi:ghettoq

# media server rendering (includes mockcache for easier testing)
ghostscript:req:apt:apt-get:ghostscript
ghostscript:req:mac:macports:ghostscript
memcachedb:req:apt:apt-get:memcachedb
# FIXME: there is no memcachedb macport yet
python-memcached:req:mac:macports:memcached
python-memcached:inst:all:pypi:python-memcached
mockcache:inst:all:pypi:mockcache
python-pil:req:apt:apt-get:libjpeg62-dev,zlib1g-dev,libfreetype6-dev,liblcms1-dev
python-pil:inst:!win:http://effbot.org/media/downloads/PIL-1.1.7.tar.gz
python-pil:instbin:win:http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe
# lamson
chardet:inst:all:pypi:chardet
jinja2:inst:all:pypi:jinja2
lockfile:inst:all:pypi:lockfile
mock:inst:all:pypi:mock
python-daemon:inst:all:pypi:python-daemon==1.5.5
lamson:inst:all:pypi:lamson
"""


# software quality testing packages
quality_packages= """
#django-nose is in main app
#nose is in main app
unittest-xml-reporting:inst:all:pypi:unittest-xml-reporting
coverage:inst:!win:pypi:coverage
nose-xcover:inst:!win:http://github.com/cmheisel/nose-xcover/tarball/master
coverage:instbin:win:http://pypi.python.org/packages/2.6/c/coverage/coverage-3.2.win32-py2.6.exe
logilab-common:inst:all:pypi:logilab-common\>=0.49.0
logilab-astng:inst:all:pypi:logilab-astng\>=0.20.0
pylint:inst:all:pypi:pylint
django-lint:inst:all:http://chris-lamb.co.uk/releases/django-lint/LATEST/django-lint-0.13.tar.gz
"""

# In addition to application packages, packages needed for development
developer_packages=  """
ipython:inst:win:pypi:pyreadline
ipython:inst:all:pypi:ipython
docutils:inst:all:pypi:docutils
sphinx:inst:all:pypi:sphinx
fudge:inst:all:pypi:fudge
beautifulsoup:inst:all:pypi:beautifulsoup\<3.1
simplejson:inst:all:pypi:simplejson
# antiword is needed for ecs/core/management/fakeimport.py (were we load word-doc-type submission documents into the database)
antiword:req:apt:apt-get:antiword
antiword:req:mac:macports:antiword
# antiword:req:win:unzip2path:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip
levenshtein:inst:!win:http://pylevenshtein.googlecode.com/files/python-Levenshtein-0.10.1.tar.bz2
"""
# required for django_extensions unittests:
#pycrypto:inst:all:pypi:pycrypto>=2.0
#pyasn1:inst:all:pypi:pyasn1
#keyczar:inst:all:http://keyczar.googlecode.com/files/python-keyczar-0.6b.061709.tar.gz


# Environments
###############

testing_bundle = sprint5_bundle
default_bundle = sprint6_bundle
future_bundle = sprint6_bundle
developer_bundle = package_merge((default_bundle, quality_packages, developer_packages))
quality_bundle = package_merge((default_bundle, quality_packages))

package_bundles = {
    'default': default_bundle,
    'testing': testing_bundle,
    'future': future_bundle,
    'sprint4': sprint4_bundle,
    'sprint5': sprint5_bundle,
    'sprint6': sprint6_bundle,
    'developer': developer_bundle,
    'quality': quality_bundle,
    'qualityaddon': quality_packages,
}


