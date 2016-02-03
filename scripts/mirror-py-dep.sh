#!/bin/bash

if [ -z "$PACKAGES_DIR" ]; then
	PACKAGES_DIR="$(cd ~/ecs-external/packages/ && pwd)"	# absolute path
fi

pip install -d "$PACKAGES_DIR" --no-use-wheel "$@"
