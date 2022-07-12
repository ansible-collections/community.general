#!/usr/bin/env bash

set -eux

[ -f "${INVENTORY}" ]

# Run connection tests with both the default and C locale.

ansible-playbook test_connection.yml -i "${INVENTORY}" "$@"

if ansible --version | grep ansible | grep -E ' 2\.(9|10|11|12|13)\.'; then
    LC_ALL=C LANG=C ansible-playbook test_connection.yml -i "${INVENTORY}" "$@"
fi
