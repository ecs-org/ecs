#!/bin/bash
if test -z "$1"; then
    base=/app
else
    base=$1
fi

dirs="storage-vault log cache ca gpg undeliverable-mail pgdump pgdump-iso pgdump-fallback"

for a in $dirs; do
    mkdir -p $base/ecs-$a
done
