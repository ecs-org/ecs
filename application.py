# ecs main application environment config
import platform
from deployment.pkgmanager import package_merge

# packages
##########

# main packages needed for the application
main_packages = """
# language support for german locales, eg. needed by postgresql to create a database with de_DE.utf8 locale 
language-pack-de:req:apt:apt-get:language-pack-de

# postgresql database bindings
psycopg2:req:apt:apt-get:libpq-dev
psycopg2:req:mac:homebrew:postgresql
psycopg2:req:mac:macports:postgresql84-server
psycopg2:req:suse:zypper:postgresql-devel
psycopg2:req:openbsd:pkg:postgresql-server
psycopg2:req:openbsd:pkg:postgresql-client
psycopg2:inst:!win:pypi:psycopg2==2.4.1
psycopg2:instbin:win:http://www.stickpeople.com/projects/python/win-psycopg/psycopg2-2.4.1.win32-py2.6-pg9.0.4-release.exe

# sqlite database bindings
pysqlite:req:apt:apt-get:libsqlite3-dev
pysqlite:req:mac:homebrew:sqlite
pysqlite:req:mac:macports:sqlite3
pysqlite:req:suse:zypper:sqlite3-devel
pysqlite:req:openbsd:pkg:sqlite3
pysqlite:inst:!win:pypi:pysqlite
pysqlite:instbin:win:http://pysqlite.googlecode.com/files/pysqlite-2.6.3.win32-py2.6.exe
                     
# timezone handling
pytz:inst:all:pypi:pytz

# python docutils, needed by django, ecs, and others
roman:inst:all:pypi:roman
docutils:inst:all:pypi:docutils\>=0.7


# django main
django:inst:all:pypi:django==1.2.3
south:inst:all:pypi:south==0.7.2
django-piston:inst:all:pypi:django-piston
django-extensions:inst:all:http://github.com/django-extensions/django-extensions/tarball/master
# docstash now uses django-picklefield
django-picklefield:inst:all:pypi:django-picklefield
# Todo: django-dbtemplates version 1.2.1 has many new features (reversion support, south support, better caching support)
django-dbtemplates:inst:all:pypi:django-dbtemplates==0.7.4
# django caching uses memcache if available
python-memcached:inst:all:pypi:python-memcached

# preprocessing, combining, compressing of js and css 
#lxml could be used by django_compressor, but we use HtmlParser
#lxml:req:apt:apt-get:libxslt1-dev,libxml2-dev
#lxml:inst:!win:pypi:lxml\<2.3
#lxml:instbin:win:http://pypi.python.org/packages/2.6/l/lxml/lxml-2.2.8.win32-py2.6.exe
cssmin:inst:all:pypi:cssmin
versiontools:inst:all:pypi:versiontools
django-appconf:inst:all:pypi:django-appconf\>=0.4.1
django_compressor:inst:all:pypi:django_compressor\>=1.1
# sass/scss css preprocessor
pyscss:inst:all:pypi:pyScss\>=1.0.8


# pdf parsing/cleaning: origami
ruby:req:apt:apt-get:ruby
rubygems:req:apt:apt-get:rubygems
ruby:req:win:http://rubyforge.org/frs/download.php/75107/rubyinstaller-1.8.7-p352.exe:exec:ruby.exe
#origami:static:all:http://rubygems.org/gems/origami-1.2.3.gem:custom:pdfcop


# unit testing
nose:inst:all:pypi:nose
django-nose:inst:all:pypi:django-nose==0.1.2
# for testing the export we need concurrent requests
django_concurrent_test_server:inst:all:pypi:django_concurrent_test_server
"""


# importlib is a dependency of celery, but importlib is included in
# Python 2.7 and newer for 2.x
v = platform.python_version_tuple()
if not (int(v[0]) == 2 and int(v[1]) >= 7):
    main_packages += "importlib:inst:all:pypi:importlib\n"

main_packages += """
# queuing: celery 
python-dateutil:inst:all:pypi:python-dateutil\<2.0.0
anyjson:inst:all:pypi:anyjson\>=0.3.1
amqplib:inst:all:pypi:amqplib\>=1.0.2
kombu:inst:all:pypi:kombu\>=1.4.1
pyparsing:inst:all:pypi:pyparsing\<2.0.0
ordereddict:inst:all:pypi:ordereddict
celery:inst:all:pypi:celery==2.3.3
django-picklefield:inst:all:pypi:django-picklefield
django-celery:inst:all:pypi:django-celery==2.3.3


# mail: ecsmail, communication: lamson mail server
chardet:inst:all:pypi:chardet
jinja2:inst:all:pypi:jinja2
lockfile:inst:all:pypi:lockfile
mock:inst:all:pypi:mock\<0.8
# we dont use python-daemon functionality in lamson, but lamson.utils imports daemon and fails
# so we fake it for windows and right now also for the rest, was python-daemon:inst:!win:pypi:python-daemon==1.5.5
python-daemon:inst:all:dir:ecs/utils/fake-daemon/
lamson:inst:all:pypi:lamson
beautifulsoup:inst:all:http://www.crummy.com/software/BeautifulSoup/download/3.x/BeautifulSoup-3.0.8.tar.gz
beautifulcleaner:inst:all:http://github.com/downloads/enki/beautifulcleaner/BeautifulCleaner-2.0dev.tar.gz


# ecs/signature: tomcat, mocca and pdf-as
# needed for crossplatform patch support (we patch pdf-as.war for preview of signed pdf)
python-patch:static:all:http://python-patch.googlecode.com/files/patch-11.01.py:copy:python-patch.py
# for apt (ubuntu/debian) systems, tomcat 6 is used as a user installation
tomcat:req:apt:apt-get:tomcat6-user
tomcat_apt_user:static:apt:file:dummy:custom:None
# for all others, a custom downloaded tomcat 6 is used
tomcat_other_user:static:!apt:http://mirror.sti2.at/apache/tomcat/tomcat-6/v6.0.33/bin/apache-tomcat-6.0.33.tar.gz:custom:apache-tomcat-6.0.33
pdfas:static:all:http://egovlabs.gv.at/frs/download.php/276/pdf-as-3.2-webapp.zip:custom:pdf-as.war
mocca:static:all:http://egovlabs.gv.at/frs/download.php/312/BKUOnline-1.3.6.war:custom:bkuonline.war


# ecs/mediaserver: file encryption, used for storage vault 
gnupg:req:apt:apt-get:gnupg
gnupg:req:mac:macports:gnupg
gnupg:req:mac:homebrew:gnupg
gnupg:req:suse:zypper:gpg2
gnupg:req:openbsd:pkg:gnupg
gnupg:req:win:ftp://ftp.gnupg.org/gcrypt/binary/gnupg-w32cli-1.4.10b.exe:exec:gpg.exe


# search
whoosh:inst:all:pypi:whoosh\>=2.2.2
# pysolr uses beautiful soup optional for solr error support
# pysolr uses httplib2 with fallback to httplib
httplib2:inst:all:pypi:httplib2
# we use == for pysolr because we dont want 2.1beta
pysolr:inst:all:pypi:pysolr==2.0.15
ordereddict:inst:all:pypi:ordereddict
django-haystack:inst:all:pypi:django-haystack\>=1.2.5
# pdf text extract
pdftotext:req:apt:apt-get:poppler-utils
#pdftotext:req:mac:homebrew:poppler
pdftotext:req:mac:macports:poppler
pdftotext:req:suse:zypper:poppler-tools
pdftotext:req:openbsd:pkg:poppler
pdftotext:req:openbsd:pkg:poppler-data
pdftotext:static:win:http://gd.tuwien.ac.at/publishing/xpdf/xpdfbin-win-3.03.zip:custom:pdftotext.exe

# excel generation / xlwt
xlwt:inst:all:pypi:xlwt


# webkit html to pdf
wkhtmltopdf:static64:apt|suse:http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.10.0_rc2-static-amd64.tar.bz2:tar:wkhtmltopdf-amd64
wkhtmltopdf:static32:apt|suse:http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-0.10.0_rc2-static-i386.tar.bz2:tar:wkhtmltopdf-i386
wkhtmltopdf:static:mac:http://wkhtmltopdf.googlecode.com/files/wkhtmltopdf-OSX-0.10.0_rc2-static.tar.bz2:tar:wkhtmltopdf
wkhtmltopdf:req:win:http://wkhtmltopdf.googlecode.com/files/wkhtmltox-0.10.0_rc2-installer.exe:exec:wkhtmltopdf.exe

# (ecs/utils/pdfutils): pdf validation (is_valid, pages_nr)
pdfminer:inst:all:pypi:pdfminer


# mediaserver image generation
# ############################

# pdf manipulation, barcode stamping
pdftk:req:apt:apt-get:pdftk
pdftk:static:win:http://www.pdfhacks.com/pdftk/pdftk-1.41.exe.zip:unzipflat:pdftk.exe
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
#ghostscript:req:mac:homebrew:ghostscript
ghostscript:req:mac:macports:ghostscript
ghostscript:req:suse:zypper:ghostscript-library
ghostscript:req:openbsd:pkg:ghostscript--
ghostscript:req:win:http://ghostscript.com/releases/gs871w32.exe:exec:gswin32c.exe

# mediaserver: new rendering may use mupdf
mupdf:static32:apt|suse:http://mupdf.com/download/mupdf-0.9-linux-i386.tar.gz:tarflat:pdfdraw
mupdf:static64:apt|suse:http://mupdf.com/download/mupdf-0.9-linux-amd64.tar.gz:tarflat:pdfdraw
mupdf:static:win:http://mupdf.com/download/mupdf-0.9-windows.zip:unzipflat:pdfdraw
#mupdf 0.8.165 if currently not available for mac, last available is 0.7
mupdf:static:mac:http://mupdf.com/download/archive/mupdf-0.7-darwin-i386.tar.gz:tarflat:pdfdraw

# mediaserver: image magick is used for rendering tasks as well
imagemagick:req:apt:apt-get:imagemagick
#imagemagick:req:mac:homebrew:imagemagick
imagemagick:req:mac:macports:imagemagick
imagemagick:req:suse:zypper:ImageMagick
imagemagick:req:openbsd:pkg:ImageMagick--
# we check for montage.exe because on windows convert.exe exists already ... :-(
imagemagick:static:win:ftp://ftp.imagemagick.org/pub/ImageMagick/binaries/ImageMagick-6.7.4-Q16-windows.zip:unzipflatsecond:montage.exe

# PIL requirements for ubuntu
libjpeg62-dev:req:apt:apt-get:libjpeg62-dev
zlib1g-dev:req:apt:apt-get:zlib1g-dev
libfreetype6-dev:req:apt:apt-get:libfreetype6-dev
liblcms1-dev-devel:req:apt:apt-get:liblcms1-dev
# PIL requirements for opensuse
libjpeg62-devel:req:suse:zypper:libjpeg62-devel
zlib-devel:req:suse:zypper:zlib
freetype2-devel:req:suse:zypper:freetype2-devel
liblcms1:req:suse:zypper:liblcms1

python-pil:inst:!win:pypi:PIL
python-pil:instbin:win:http://effbot.org/media/downloads/PIL-1.1.7.win32-py2.6.exe

# deployment: manage.py massimport
antiword:req:apt:apt-get:antiword
antiword:req:mac:homebrew:antiword
antiword:req:mac:macports:antiword
# antiword has to be built by hand for opensuse
#antiword:req:suse:zypper:antiword
antiword:req:openbsd:pkg:antiword
antiword:static:win:http://www.informatik.uni-frankfurt.de/~markus/antiword/antiword-0_37-windows.zip:unzipflat:antiword.exe
# antiword is needed for ecs/core/management/massimport.py (were we load word-doc-type submission documents into the database)


# feedback: jsonrpclib for ecs feedback and fab ticket
jsonrpclib:inst:all:file:externals/joshmarshall-jsonrpclib-283a2a9-ssl_patched.tar.gz


# logging: django-sentry; 
# uuid:inst:all:pypi:uuid uuid is in mainlibs since 2.3 ... and was not thread safe in 2.5...
django-templatetag-sugar:inst:all:pypi:django-templatetag-sugar
django-indexer:inst:all:pypi:django-indexer\>=0.3.0
django-paging:inst:all:pypi:django-paging\>=0.2.4
pygooglechart:inst:all:pypi:pygooglechart
django-sentry:inst:all:pypi:django-sentry==1.11.4

# ecs.help needs reversion from now on
django-reversion:inst:all:pypi:django-reversion==1.3.3

# diff_match_patch is used for the submission diff and django-reversion
diff_match_patch:inst:all:http://github.com/pinax/diff-match-patch/tarball/master

# gettext and companions (msgfmt) are needed for make- and compile-messages which are part of bootstrap
gettext:req:apt:apt-get:gettext
gettext_runtime:static:win:http://ftp.gnome.org/pub/gnome/binaries/win32/dependencies/gettext-runtime-0.17.zip:custom:intl.dll
gettext_tools:static:win:http://ftp.gnome.org/pub/gnome/binaries/win32/dependencies/gettext-tools-0.17.zip:custom:xgettext.exe

# django-rosetta is used only for doc.ecsdev.ep3.at , but we keep it in the main requirements for now
django-rosetta:inst:all:pypi:django-rosetta
"""

# packages that are needed to run guitests using windmill, not strictly needed, except you do guitesting
guitest_packages = """
windmill:inst:all:pypi:windmill\>=1.6
# for random text generation in windmill tests
cicero:inst:all:pypi:cicero
# Firefox and a vncserver is needed for headless gui testing
firefox:req:apt:apt-get:firefox
vncserver:req:apt:apt-get:vnc4server
"""


# software quality testing packages, not strictly needed, except you do coverage analysis
quality_packages= """
# nose and django-nose is in main app
unittest-xml-reporting:inst:all:pypi:unittest-xml-reporting
coverage:inst:!win:pypi:coverage
coverage:instbin:win:http://pypi.python.org/packages/2.6/c/coverage/coverage-3.5.1.win32-py2.6.exe
nose-xcover:inst:all:http://github.com/cmheisel/nose-xcover/tarball/master
unittest2:inst:all:pypi:unittest2
#logilab-common:inst:all:pypi:logilab-common\>=0.49.0
#logilab-astng:inst:all:pypi:logilab-astng\>=0.20.0
# disbaled pylint for now because it throws errors: pylint:inst:all:pypi:pylint
#django-lint:inst:all:http://chris-lamb.co.uk/releases/django-lint/LATEST/django-lint-0.13.tar.gz

"""


# packages needed or nice to have for development
developer_packages=  """

# debugging toolbar, switched back to robhudson original tree
django-debug-toolbar:inst:all:http://github.com/robhudson/django-debug-toolbar/tarball/master
#django-debug-toolbar:inst:all:http://github.com/dcramer/django-debug-toolbar/tarball/master

# support for django-devserver
guppy:inst:!win:pypi:guppy
guppy:instbin:win:http://pypi.python.org/packages/2.6/g/guppy/guppy-0.1.9.win32-py2.6.exe
sqlparse:inst:all:pypi:sqlparse
werkzeug:inst:all:pypi:werkzeug
django-devserver:inst:all:https://github.com/dcramer/django-devserver/tarball/master

# cherrypy running django (threaded wsgi server)
django-wsgiserver:inst:all:pypi:django-wsgiserver

# interactive python makes your life easier
ipython:inst:win:pypi:pyreadline
ipython:inst:all:pypi:ipython

# dependency generation for python programs
sfood:inst:all:pypi:snakefood

# FIXME: who needs simplejson, and why is it in developer packages
simplejson:inst:all:pypi:simplejson
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

# postfix is used as incoming smtp firewall and as smartmx for outgoing mails
postfix:req:apt:apt-get:postfix

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

 

# target bundles
################

import ecs.target as target

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
    'guitestaddon': guitest_packages,
    'developeraddon': developer_packages,
    'system': system_bundle,
}

logrotate_targets = {
    'default': '*.log'
}

upstart_targets = {
    'celeryd': (None, './manage.py celeryd -l warning -L ../../ecs-log/celeryd.log'),    
    'celerybeat': (None, './manage.py celerybeat -S djcelery.schedulers.DatabaseScheduler -l warning -L ../../ecs-log/celerybeat.log'),
    'ecsmail': (None, './manage.py ecsmail server ../../ecs-log/ecsmail.log'), 
    'signature': ('upstart-tomcat.conf', ''),
}

test_flavors = {
    'default': './manage.py test',
    'mainapp': './manage.py test',
    'mediaserver': 'false',  # include in the mainapp tests
    'mailserver': 'false', # included in the mainapp tests
}


