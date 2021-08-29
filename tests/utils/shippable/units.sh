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

if [ "$2" == "2.10" ]; then
    sed -i -E 's/^python-gitlab($| .*)/python-gitlab < 2.10.1 ; python_version >= '\'3.6\''/g' tests/unit/requirements.txt
    echo "python-gitlab ; python_version < '3.6'" >> tests/unit/requirements.txt
fi

# shellcheck disable=SC2086
ansible-test units --color -v --docker default --python "${version}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
    "${options[@]:+${options[@]}}" \
