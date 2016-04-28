#!/bin/bash
set -e
echo "docker-entrypoint.sh called with:\"$@\""

realpath=`dirname $(readlink -e "$0")`
. $realpath/database.include

if test -z "$1"; then
  cat << EOF
Usage: "$0 cmd" to start
  web       = supervisor controlled web service (nginx + uWSGI)
              if ECS_MIGRATE_AUTO is true, first web container will do migration on startup
  simple    = as "web", but no automatic migrations
  worker    = celery worker daemon
  beat      = celery beat daemon

one time commands:
  migrate   = run database migration
  run \$@   = \$@ as user app in workdir with activated python environment
  \$@       = \$@ executed as typed as user root

Examples:
  * web
  * run ./manage.py shell_plus
  * migrate
  * /bin/bash ls -la /root

EOF
  exit 1
fi


if [[ "web simple worker beat migrate run _prepare _user" =~ $1 ]]; then
  cmd=$1
  shift

  if test "$cmd" = "web"; then
    # change to app user, call _prepare
    gosu app $0 _user _prepare
    # needs running as root user
    echo "execute supervisor"
    exec /usr/bin/supervisord -c /app/ecs/conf/supervisord.conf

  elif test "$cmd" = "simple"; then
    # needs running as root user
    echo "execute supervisor"
    exec /usr/bin/supervisord -c /app/ecs/conf/supervisord.conf

  elif [[ "worker beat migrate run _prepare" =~ $cmd ]]; then
    # needs running as app user
    exec gosu app $0 _user $cmd "$@"

  elif test "$cmd" = "_user"; then
    cmd=$1
    shift

    echo "activate environment"
    cd /app/ecs
    . /app/env/bin/activate

    if test ! -f ./ecs/version.py; then
      echo "no version.py found, trying to create a version.py from git-rev/branch"
      ./scripts/create-version-file.sh ./ ./ecs/version.py
    fi

    if test "$cmd" = "worker"; then
      echo "execute celery worker"
      exec /app/env/bin/celery --events -A ecs worker -l warning

    elif test "$cmd" = "beat"; then
      echo "execute celery beat"
      exec /app/env/bin/celery -A ecs beat -l warning

    elif test "$cmd" = "migrate"; then
      prepare_database

    elif test "$cmd" = "run"; then
      exec "$@"

    elif test "$cmd" = "_prepare"; then
      # get number of proctype container we are running"
      dyno_clean=$(printf "%s" "$DYNO" | tr -d \'\")
      dyno_count="${dyno_clean##*.}"

      if test -z "$dyno_count" -o "$dyno_count" = "1"; then
        if test "$ECS_MIGRATE_AUTO" = "true"; then
          # prepare_database makes bootstrap as last step
          prepare_database
        else
          echo "manage.py bootstrap"
          ./manage.py bootstrap
        fi
      else
        if test "$ECS_MIGRATE_AUTO" = "true"; then
          echo "container number $dyno_count >1, skipping automatic database migration"
        fi
        echo "container number $dyno_count >1, skipping manage.py bootstrap"
      fi
    fi
  fi
else
  exec "$@"
fi
