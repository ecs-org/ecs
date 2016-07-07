#!/bin/bash

usage(){
    cat << EOF
Usage: "$0 cmd"

    web         = supervisor controlled web service (nginx + uWSGI)
    simple      = as "web", but no automatic migrations
    combined    = combined web,worker,beat,smtpd container
    worker      = celery worker daemon
    beat        = celery beat daemon
    smtpd       = smtp daemon

one time commands:
    migrate     = run database migration
    run \$@     = execute \$@ as user app in workdir with activated python environment
    \$@         = execute \$@ as user root

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
}


set -e
echo "docker-entrypoint.sh called with:\"$@\""
realpath=`dirname $(readlink -e "$0")`
. $realpath/database.include

if test -z "$1"; then
    usage
fi

if [[ ! "$1" =~ ^(web|combined|simple|worker|beat|smtpd|migrate|run|_prepare|_user)$ ]]; then
    exec "$@"
fi

cmd=$1
shift

if [[ "$cmd" =~ ^(worker|beat|smtpd|migrate|run|_prepare)$ ]]; then
    # needs running as app user
    exec gosu app $0 _user $cmd "$@"
fi

case "$cmd" in
web)
    gosu app $0 _user _prepare
    echo "execute supervisor (web)"
    exec /usr/bin/supervisord -c /app/supervisord-web.conf
    ;;
combined)
    gosu app $0 _user _prepare
    echo "execute supervisor (combined)"
    exec /usr/bin/supervisord -c /app/supervisord-combined.conf
    ;;
simple)
    echo "execute supervisor (web)"
    exec /usr/bin/supervisord -c /app/supervisord-web.conf
    ;;
_user)
    sub=$1
    shift

    echo "activate environment"
    cd /app/ecs
    . /app/env/bin/activate

    if test ! -f ./ecs/version.py; then
        echo "no version.py found, trying to create a version.py from git-rev/branch"
        ./scripts/create-version-file.sh ./ ./ecs/version.py
    fi

    case "$sub" in
    worker)
        echo "execute celery worker"
        exec /app/env/bin/celery --events -A ecs worker -l warning
        ;;
    beat)
        echo "execute celery beat"
        exec /app/env/bin/celery -A ecs beat -l warning
        ;;
    smtpd)
        echo "execute smtpd"
        exec /app/ecs/manage.py smtpd
        ;;
    migrate)
        prepare_database
        ;;
    run)
        exec "$@"
        ;;
    _prepare)
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
                echo "container number $dyno_count >1, skipping automatic migration"
            fi
            echo "container number $dyno_count >1, skipping manage.py bootstrap"
        fi
        ;;
    esac
esac
