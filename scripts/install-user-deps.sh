#!/bin/bash

selfname=`echo $(cd $(dirname "$0") && pwd -L)/$(basename "$0")`
selfpath=`dirname $selfname`
defreq="${selfpath}/../requirements/all.freeze"

if test -z "$1"; then
  cat <<EOF
usage: $0 environmentdir [requirementfile [requirementfile]+]"

install a new python3 virtual environment and installs the requirements via pip
default if no requirementfile is "$defreq"

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

python3 -m venv $envdir
. $envdir/bin/activate
pip install $reqs
