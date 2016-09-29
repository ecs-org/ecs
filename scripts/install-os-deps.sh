#!/bin/bash

function usage(){
    cat <<EOF
usage: $0 [options]

options:
--no-upgrade            # does not upgrade packages as first step
--with-postgres-server  # additionaly install a postgresql server
--autoremove            # "apt-get autoremove", remove unused packages after install
--clean                 # "apt-get clean", remove downloaded archives after install
--list                  # just display the list of packages to be installed
--update-pkgcache < Dockerfile > Dockerfile.new  # replaces PKGCACHE with up2date pkg list

any other cmdline option shows this help, needs to be called as root

EOF
    exit 1
}

function filter_list(){
    # filter comments starting with "#" & whitespace lines
    sed 's/#.*//; /^[[:space:]]*$/d' "$1"
}

function update_pkgcache(){
    local pkgs=$(filter_list "$1" | sort | tr '\n' ' ')
    sed '/^cat << PKGCACHE/,/^PKGCACHE$/c cat << PKGCACHE | xargs apt-get install -y \\\n'"${pkgs}"'\\\nPKGCACHE'
}


export DEBIAN_FRONTEND=noninteractive
realpath=`dirname $(readlink -e "$0")`
arch=$(dpkg --print-architecture)
upgrade=true
withpostgres=false
autoremove=false
clean=false
OPTS=`getopt -o aclup --long autoremove,clean,list,update-pkgcache,with-postgres-server -- "$@"`
[[ $? -eq 0 ]] || usage

eval set -- "${OPTS}"

while true; do
    case $1 in
    -a|--autoremove)
        autoremove=true
        ;;
    -c|--clean)
        clean=true
        ;;
    -l|--list)
        filter_list ${realpath}/../requirements/system.apt
        exit 0
        ;;
    -u|--update-pkgcache)
        update_pkgcache ${realpath}/../requirements/system.apt
        exit 0
        ;;
    -p|--with-postgres-server)
        withpostgres=true
        ;;
    --)
        shift
        break
        ;;
    *)
        usage
        ;;
    esac
    shift
done

[[ $# -eq 0 ]] || usage

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
filter_list ${realpath}/../requirements/system.apt | xargs apt-get install -y

if $withpostgres; then
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
rm /tmp/${wkarchive}

if $autoremove; then
    echo "remove installed but unused packages"
    apt-get autoremove -y
    apt-get autoremove -y   # call it twice, because first remove does not remove all
fi
if $clean; then
    echo "remove downloaded packages"
    apt-get clean -y
fi
