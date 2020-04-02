#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

version="${args[1]}"
group="${args[2]}"

if [[ "${COVERAGE:-}" == "--coverage" ]]; then
    timeout=90
else
    timeout=30
fi

group1=()

case "${group}" in
    1) options=("${group1[@]:+${group1[@]}}") ;;
esac

ansible-test env --timeout "${timeout}" --color -v

# shellcheck disable=SC2086
ansible-test units --color -v --docker default --python "${version}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
    "${options[@]:+${options[@]}}" \
