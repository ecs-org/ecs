#!/bin/bash

selfname=`echo $(cd $(dirname "$0") && pwd -L)/$(basename "$0")`
selfpath=`dirname $selfname`
arch=$(dpkg --print-architecture)

function filter_list(){
     grep -v "#" $1 | grep -v "^$";
}

echo "update package lists, upgrade packages"
export DEBIAN_FRONTEND=noninteractive
apt-get -y update
apt-get -y upgrade

echo "update python-pip (workaround docker issue)"
apt-get -y install python-pip
pip install --upgrade pip

echo "install system dependencies"
filter_list ${selfpath}/../requirements/system.apt | xargs apt-get install -y;

if test "$1" = "--with-postgres-server"; then
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
