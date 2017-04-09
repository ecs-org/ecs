#!/bin/bash

if test -z "$1"; then
    echo "Error: Usage: $0 basedirectory" >&2
    exit 1
fi

base=$1
dirnames="storage-vault cache ca gpg pgdump pgdump-iso pgdump-fallback"
install_opts="-g app -o app"

for a in $dirnames; do
    install $install_opts -d $base/ecs-$a
done
for a in new cur tmp; do
    install $install_opts -d $base/ecs-undeliverable/$a
done
chmod 0700 $base/ecs-gpg
install $install_opts -d $base/ecs/static/CACHE
