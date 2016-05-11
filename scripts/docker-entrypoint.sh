#!/bin/bash
set -e
echo "docker-entrypoint.sh called with:\"$@\""

realpath=`dirname $(readlink -e "$0")`
. $realpath/database.include

if test -z "$1"; then
  cat << EOF
Usage: "$0 cmd" to start
    web       = supervisor controlled web service (nginx + uWSGI)
    combined  = combined web,worker,beat,smtpd container
    simple    = as "web", but no automatic migrations
    worker    = celery worker daemon
    beat      = celery beat daemon
    smtpd     = smtp daemon

one time commands:
    migrate   = run database migration
    run \$@   = \$@ as user app in workdir with activated python environment
    \$@       = \$@ executed as typed as user root

Environment:
    ECS_MIGRATE_AUTO = true
        will migrate on startup if first container of type "web" or "combined"

Examples:
    + web
    + run ./manage.py shell_plus
    + migrate
    + /bin/bash ls -la /root

EOF
  exit 1
fi


if [[ "web combined simple worker beat smtpd migrate run _prepare _user" =~ $1 ]]; then
  cmd=$1
  shift

  if test "$cmd" = "web"; then
    # call @app user, _prepare
    gosu app $0 _user _prepare
    echo "execute supervisor (web)"
    exec /usr/bin/supervisord -c /app/supervisord-web.conf

  elif test "$cmd" = "combined"; then
    # call @app user, _prepare
    gosu app $0 _user _prepare
    echo "execute supervisor (combined)"
    exec /usr/bin/supervisord -c /app/supervisord-combined.conf

  elif test "$cmd" = "simple"; then
    echo "execute supervisor (web)"
    exec /usr/bin/supervisord -c /app/supervisord-web.conf

  elif [[ "worker beat smtpd migrate run _prepare" =~ $cmd ]]; then
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

    elif test "$cmd" = "smtpd"; then
      echo "execute smtpd"
      exec /app/ecs/manage.py smtpd

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
