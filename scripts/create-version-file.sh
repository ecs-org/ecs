#!/bin/bash
set -e

if test "$2" = "" -o ! -d "$1"; then
    cat << EOF
Usage: $0 path/to/sourcedir outputfile

creates a file with following entries:

ECS_VERSION= "branch shorthash commitmessage"
ECS_GIT_REV= "long git hash"
ECS_GIT_BRANCH= "git branch name"
ECS_CHANGED= "date and time of execution"

information is taken (in order) from
    * environment variables GIT_REV and GIT_BRANCH,
    * or from git (where path/to/sourcedir is a git repository)
    * or script fails with exit 1

EOF
    exit 1
fi

sourcedir=$1
versionfile=$2

if test ! -z "$GIT_REV"; then
    ECS_GIT_REV="${GIT_REV}"
    ECS_GIT_BRANCH="${GIT_BRANCH:-unknown}"
    ECS_VERSION="${ECS_GIT_BRANCH} ${ECS_GIT_REV::10} dev"
else
    if $(git -C "$sourcedir" rev-parse --is-inside-work-tree); then
        ECS_GIT_REV="$(git -C "$sourcedir" rev-parse HEAD)"
        ECS_GIT_BRANCH="$(git -C "$sourcedir" rev-parse --abbrev-ref HEAD)"
        ECS_VERSION="$((echo -n "${ECS_GIT_BRANCH} ${ECS_GIT_REV::10} "; git -C "$sourcedir" log --pretty=format:'%s' HEAD^..HEAD|cut -c -30)|python -c 'print(repr(__import__("sys").stdin.read().strip()))')"
    fi
fi

if test -z "$ECS_GIT_REV"; then
    echo "ERROR: could not retrieve ecs GIT_REV, abort"
    exit 1
fi

cat > $versionfile << EOF
ECS_VERSION=$ECS_VERSION
ECS_GIT_BRANCH="$ECS_GIT_BRANCH"
ECS_GIT_REV="$ECS_GIT_REV"
ECS_CHANGED="$(date +"%d.%m.%Y %H:%M")"
EOF
