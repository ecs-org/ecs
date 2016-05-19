#!/bin/bash

function filter_list(){
    grep -v "#" $1 | grep -v "^$"
}

realpath=`dirname $(readlink -e "$0")`
arch=$(dpkg --print-architecture)

if test "$1" = "--no-upgrade"; then upgrade=false; shift; else upgrade=true; fi
if test "$1" = "--with-postgres-server"; then wps=true; shift; else wps=false; fi

export DEBIAN_FRONTEND=noninteractive
echo "update package lists"
apt-get -y update

if $upgrade; then
    echo "upgrade packages"
    echo "==> Disabling the release upgrader"
    sed -i.bak 's/^Prompt=.*$/Prompt=never/' /etc/update-manager/release-upgrades
    apt-get -y upgrade
    apt-get -y dist-upgrade --force-yes
fi

echo "install system dependencies"
filter_list ${realpath}/../requirements/system.apt | xargs apt-get install -y;

if $wps; then
    echo "install a postgres server"
    apt-get install -y postgresql postgresql-contrib
fi

echo "get and install gosu to /usr/local/bin"
curl -o /usr/local/bin/gosu -fsSL \
    "https://github.com/tianon/gosu/releases/download/1.7/gosu-${arch}"
chmod +x /usr/local/bin/gosu

echo "get and extract wkhtmltopdf to /usr/local/bin"
wkarchive="wkhtmltopdf-0.11.0_rc1-static-${arch}.tar.bz2"
curl -o /tmp/$wkarchive -fsSL \
    "http://download.gna.org/wkhtmltopdf/obsolete/linux/${wkarchive}"
tar xjf /tmp/${wkarchive} -C /usr/local/bin
ln -f -s /usr/local/bin/wkhtmltopdf-amd64  /usr/local/bin/wkhtmltopdf
