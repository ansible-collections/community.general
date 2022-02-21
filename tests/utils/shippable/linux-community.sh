#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

image="${args[1]}"
python="${args[2]}"

if [ "${#args[@]}" -gt 3 ]; then
    target="shippable/posix/group${args[3]}/"
else
    target="shippable/posix/"
fi

# shellcheck disable=SC2086
ansible-test integration --color -v --retry-on-error "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} \
    --docker "quay.io/ansible-community/test-image:${image}" --python "${python}"
