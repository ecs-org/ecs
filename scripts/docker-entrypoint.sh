#!/bin/bash
set -e
echo "docker-entrypoint.sh called with:\"$@\""

selfname=`echo $(cd $(dirname "$0") && pwd -L)/$(basename "$0")`
selfpath=`dirname $selfname`
. $selfpath/database.include

if test "$1" = "web"; then
  shift
  cd /app/ecs

  echo "activate environment"
  . /app/env/bin/activate

  echo "prepare database"
  prepare_database

  echo "execute gunicorn"
  exec gunicorn ecs.wsgi -w ${ECS_WORKER_NUM:-4} -b 0.0.0.0:5000 --chdir=/app/ecs
else
  exec "$@"
fi
