#!/bin/bash
set -e

if test "$2" = "" -o ! -d "$1"; then
    cat << EOF
Usage: $0 path/to/sourcedir outputfile

creates a file with following entries:

ECS_VERSION= "branch shorthash commitmessage"
ECS_GIT_REV= "long git hash"
ECS_GIT_BRANCH= "git branch name"

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
    ECS_GIT_SHORT=$(echo "$ECS_GIT_REV"| cut -c -10)
    ECS_VERSION="${ECS_GIT_BRANCH} ${ECS_GIT_SHORT} dev"
else
    if $(cd $sourcedir && git rev-parse --is-inside-work-tree); then
        ECS_GIT_REV="$(cd $sourcedir && git rev-parse HEAD)"
        ECS_GIT_BRANCH="$(cd $sourcedir && git rev-parse --abbrev-ref HEAD)"
        ECS_VERSION="${ECS_GIT_BRANCH} $(echo "$ECS_GIT_REV"| cut -c -10) $(cd $sourcedir && git log --pretty=format:'%s' HEAD^..HEAD|cut -c -30 | tr \" \')"
    fi
fi

if test -z "$ECS_GIT_REV"; then
    echo "ERROR: could not retrieve ecs GIT_REV, abort"
    exit 1
fi

cat > $versionfile << EOF
ECS_VERSION="$ECS_VERSION"
ECS_GIT_BRANCH="$ECS_GIT_BRANCH"
ECS_GIT_REV="$ECS_GIT_REV"
EOF
