#!/bin/sh

cat <<'EOF' > /etc/apt/sources.list.d/pgdg.list
deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main
EOF

# main application
apt-get install apache2-mpm-prefork gettext language-pack-de \
    libapache2-mod-wsgi libpq-dev libmemcached-dev memcached \
    openjdk-7-jre-headless pgbouncer postfix postgresql rabbitmq-server \
    solr-jetty tomcat7-user

# documents
apt-get install ghostscript gnupg pdftk qpdf

# deps for PIL
apt-get install libfreetype6-dev libjpeg62-dev liblcms1-dev

# backup
apt-get install backupninja debconf-utils duplicity duply ncftp rsync

# firewall
apt-get install shorewall

# see http://wkhtmltopdf.org/downloads.html
# http://download.gna.org/wkhtmltopdf/obsolete/linux/wkhtmltopdf-0.11.0_rc1-static-amd64.tar.bz2

# packages needed for full production rollout (eg. VM Rollout)
# pdfas and mocca is used for electronic signing using the austrian citizen card
# was: pdfas:static:all:https://joinup.ec.europa.eu/site/pdf-as/releases/4.0.7/pdf-as-web-4.0.7.war:custom:pdf-as-web.war
# was: pdfasconfig:static:all:https://joinup.ec.europa.eu/site/pdf-as/releases/4.0.7/cfg/defaultConfig.zip:custom:pdf-as-web
# was: mocca:static:all:https://joinup.ec.europa.eu/system/files/project/bkuonline-1.3.18.war:custom:bkuonline.war
