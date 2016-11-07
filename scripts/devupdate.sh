#!/bin/bash

usage(){
    cat << EOF
Usage:  $0 [--restore-dump] init
        $0 [--restore-dump] pull [--force] [branchname [--force]]
        $0 rebase
        $0 dumpdb [targetdumpname]
        $0 freshdb

init    = install/renew all system setup regardless of current state.
            does not touch sourcecode, is safe to use.
pull    = fetch,update current source to origin/branchname(HEAD)
            and run needed devserver updates. restore from dump if needed.
            "pull" will refuse to run if there are uncommited changes/additions
            or unpushed changes exists in the repository.
rebase  = fetch origin, rebase current local branch with
            origin/$ECS_DEV_REBASE_TO(HEAD) (default master)
            and force pushes changes to origin
dumpdb  = dump current database and write it to /app/ecs.pgdump
freshdb = destroy current database and create a new empty ecs database

Option:
    "--force" will ignore and *OVERWRITE* unpushed changes in target branch
    "--restore-dump" will mandatory restore database from dump
        dump will be selected from first existing file of list:
        $HOME/{./ ecs-pgdump ecs-pgdump-iso ecs-pgdump-fallback}/ecs.pgdump

Testing:
    isclean [--ignore-unpushed] = run abort_ifnot_cleanrepo
    get_dumpfilename = get first used dumpfile
Env:
    ECS_DUMP_FILENAME="/path/to/custom.pgdump"
        to restore from a non default dump.
    CLEANUP="true" to cleanup locks
    ECS_DEV_AUTOSTART="false" to your .profile,
        devupdate.sh will not restart devserver

    current autostart: $ECS_DEV_AUTOSTART
    current rebase to: $ECS_DEV_REBASE_TO

EOF
    exit 1
}

dev_update(){
    # call with: $0 $init_all{true/false} $restore_dump{true/false} $target_branch{!=""}
    local init_all restore_dump target_branch current_branch prepare_was_run opt i

    # kill whole processgroup on sigterm
    trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

    init_all=$1
    restore_dump=$2
    target_branch=$3
    current_branch=$(git rev-parse --abbrev-ref HEAD)

    if test -z "$target_branch"; then
        echo "Error: fatal, no target branch set"
        exit 1
    fi
    if test "${CLEANUP:-false}" = "true"; then
        echo "Warning: CLEANUP=true, deleting lock files"
        if test -f $HOME/devupdate.disabled; then rm $HOME/devupdate.disabled; fi
    fi
    if test -e $HOME/devupdate.disabled; then
        echo "ERROR: $HOME/devupdate.disabled was found, aborting"
        exit 1
    fi

    # Open/create lock file and acquire an exclusive lock. The lock will be
    # released automatically when the shell terminates.
    exec 200<>$HOME/devupdate.lock
    if ! flock --nonblock 200; then
        echo "ERROR: another devupdate is already running, aborting"
        exit 1
    fi

    echo "stop ecs-devserver if running"
    sudo systemctl stop devserver
    sudo systemctl disable devserver

    echo "cleanup __pycache__ directories"
    find . -name __pycache__ -exec rm -r '{}' +

    local br_change sys_change ds_change pip_change mig_change mig_add
    if $init_all; then
        # init_all does not need dump restore => mig_change=1
        echo "init_all: marking everything as changed (except mig_change)"
        br_change=true; sys_change=true; ds_change=true; pip_change=true
        mig_change=false; mig_add=true
    else
        echo "collect differences"
        br_change=$(test "$current_branch" != "$target_branch" && echo true || echo false)
        sys_change=$(git diff --name-status HEAD..origin/$target_branch | \
            grep -q  "requirements/system.apt" && echo true || echo false)
        ds_change=$(git diff --name-status HEAD..origin/$target_branch | \
            grep -q "conf/devserver" && echo true || echo false)
        pip_change=$(git diff --name-status HEAD..origin/$target_branch | \
            grep -q "requirements/all.freeze" && echo true || echo false)
        mig_change=$(git diff --name-status HEAD..origin/$target_branch | \
            grep -q "^[^A].*/migrations/" && echo true || echo false)
        mig_add=$(git diff --name-status HEAD..origin/$target_branch | \
            grep -q "^A.*/migrations/" && echo true || echo false)
        echo "changed: br: $br_change, sys: $sys_change, ds: $ds_change, pip: $pip_change, migC: $mig_change, migA: $mig_add"

        echo "reset workdir to origin/$target_branch"
        git checkout -f $target_branch
        git reset --hard origin/$target_branch
    fi

    echo "overwrite version.py"
    scripts/create-version-file.sh $G_srcdir $G_srcdir/ecs/version.py

    if $br_change; then
        echo "delete old static/CACHE entries"
        rm -r static/CACHE
    fi

    if $sys_change; then
        echo "install os-deps"
        sudo ./scripts/install-os-deps.sh --with-postgres-server --autoremove --clean
        # nginx, supervisor are not needed running on devserver
        for i in nginx supervisor; do
            sudo systemctl disable $i
            sudo systemctl stop $i
        done
    fi

    echo "recreate directories"
    ./scripts/create-dirs.sh

    # migrate symlink of bin to symlink to ~/bin/*
    if test -L /app/bin; then rm /app/bin; fi
    # symlink all scripts to ~/bin
    ln -sft /app/bin /app/ecs/scripts/*

    # environment recreation
    if $pip_change; then
        echo "install pip deps"
        ./scripts/install-user-deps.sh $HOME/env requirements/all.freeze
    fi
    . $HOME/env/bin/activate

    # database migration and restore
    prepare_was_run=false
    if test $restore_dump = "true" -o $mig_add = "true" -o $mig_change = "true"; then
        prepare_was_run=true
        opt=$(if test $mig_change = "true" -o $restore_dump = "true"; then echo "--restore-dump"; fi)
        prepare_database $opt
    fi

    ./manage.py compilemessages
    if test $prepare_was_run != "true"; then
        ./manage.py bootstrap
    fi

    if $ds_change; then
        echo "devserver service change"
        sudo cp -f $G_srcdir/conf/devserver.service /etc/systemd/system/devserver.service
        sudo -- bash -c 'grep -qi "^#\?RateLimitBurst" /etc/systemd/journald.conf &&
            sed -i "s/^#\?RateLimitBurst.*/RateLimitBurst=100000/" /etc/systemd/journald.conf ||
            echo "RateLimitBurst=100000" >> /etc/systemd/journald.conf'
        sudo systemctl daemon-reload
        sudo systemctl restart systemd-journald
        sudo systemctl enable devserver
    fi

    if test "$ECS_DEV_AUTOSTART" = "true"; then
        echo "start ecs-devserver, log will be available via 'sudo journalctl -u devserver'"
        sudo systemctl start devserver
    fi

    echo "devupdate finished. git status:"
    git branch -v | grep "^\*" | sed -re "s/\* ([a-z._-]+) ([0-9a-f]+) (.{,27}).*/\1 \2 \3 /g"
}


abort_ifnot_cleanrepo(){
    if ! git diff-files --quiet --ignore-submodules --; then
        echo "error: abort, your working directory is not clean."
        git --no-pager diff-files --name-status -r --ignore-submodules --
        exit 1
    fi
    if ! git diff-index --cached --quiet HEAD --ignore-submodules --; then
        echo "error: abort, you have cached/staged changes"
        git --no-pager diff-index --cached --name-status -r --ignore-submodules HEAD --
        exit 1
    fi
    if test "$(git ls-files --other --exclude-standard --directory)" != ""; then
        echo "error: abort, working directory has extra files"
        git --no-pager ls-files --other --exclude-standard --directory
        exit 1
    fi
    if test ! "$1" = "--ignore-unpushed"; then
        if test "$(git log --branches --not --remotes --pretty=format:'%H')" != ""; then
            echo "error: abort, there are unpushed changes"
           git --no-pager log --branches --not --remotes --pretty=oneline
           exit 1
        fi
    fi
}


main(){
    local restore_dump target_branch err force tmpdir init_all
    if test -z "$1"; then usage; fi

    restore_dump=false
    if test "$1" = "--restore-dump"; then shift; restore_dump=true; fi

    cd $G_srcdir

    case "$1" in
    isclean)
        abort_ifnot_cleanrepo $2
        ;;
    get_dumpfilename)
        get_dumpfilename
        ;;
    dumpdb)
        dump_database $2
        ;;
    _selfcontinue)
        echo "dev_update $2 $3 $4"
        dev_update $2 $3 $4
        ;;
    freshdb)
        sudo systemctl stop devserver
        . $HOME/env/bin/activate
        fresh_database
        deactivate
        if test "$ECS_DEV_AUTOSTART" = "true"; then
            sudo systemctl start devserver
        fi
        ;;
    rebase)
        abort_ifnot_cleanrepo --ignore-unpushed
        git fetch --all --prune
        git rebase $ECS_DEV_REBASE_TO
        git push -f "origin/$(git rev-parse --abbrev-ref HEAD)"
        ;;
    init|pull)
        target_branch="$(git rev-parse --abbrev-ref HEAD)"
        err=$?
        if test "$err" -ne 0; then
            echo "Warning: get current branch ($target_branch) returned error: $err"
        fi

        if test "$1" = "init"; then init_all=true; else init_all=false; fi

        if test "$1" = "pull"; then
            shift
            force=false
            if test "$1" = "--force"; then force=true; shift; fi
            if test "$1" != ""; then target_branch=$1; shift; fi
            if test "$1" = "--force"; then force=true; shift; fi
            abort_ifnot_cleanrepo $(if $force; then echo "--ignore-unpushed"; fi)
            echo "git fetch --all --prune"
            git fetch --all --prune
        fi

        if test "$target_branch" = ""; then
            echo "Error: Fatal, could not determine target_branch!"
            exit 1
        fi

        # copy self to tempdir and continue there so we can update ourself
        tmpdir=`mktemp -d`
        if test ! -d $tmpdir; then
            echo "error: fatal, could not create temporary directory"
            exit 1
        fi
        cp $G_realpath/devupdate.sh $tmpdir/devupdate.sh
        echo "_selfcontinue $init_all $restore_dump $target_branch"
        exec $tmpdir/devupdate.sh _selfcontinue $init_all $restore_dump $target_branch
        ;;
    *)
        usage
        ;;
    esac
}


export ECS_USERSWITCHER_ENABLED=${ECS_USERSWITCHER_ENABLED:-true}
export ECS_DEV_AUTOSTART=${ECS_DEV_AUTOSTART:-true}
export ECS_DEV_REBASE_TO=${ECS_DEV_REBASE_TO:-master}

# HACK: set G_srcdir either to $HOME/ecs or relative to this script
G_srcdir=$HOME/ecs
G_realpath=`dirname $(readlink -e "$0")`
if test -f $G_realpath/database.include; then
    G_srcdir=$G_realpath/..
fi
. $G_srcdir/scripts/database.include
main "$@"
