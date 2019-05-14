#!/bin/bash

realpath=`dirname $(readlink -e "$0")`
defreq="${realpath}/../requirements/all.freeze"

if test -z "$1"; then
    cat <<EOF
usage: $0 environmentdir [requirementfile [requirementfile]+]"

install a new python3 virtual environment and the requirements via pip.
if no requirementfile is specified, the default "$defreq" is used.

EOF
    exit 1
fi

envdir=$1
shift

reqs="$@"
if test -z "$reqs"; then
    reqs=$defreq
fi
reqs=$(for a in $reqs; do echo "-r $a"; done)

if test -d $envdir; then
    rm -rf $envdir
fi

# XXX use upgraded pip and virtualenv, see install-os-deps.sh
realpython=$(echo $(which -a python3)| tr " " "\n"| grep "/usr"| sort -r| head -n 1)
$realpython -m venv $envdir
. $envdir/bin/activate
pip install $reqs
