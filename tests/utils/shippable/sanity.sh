#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

group="${args[1]}"

if [ "${BASE_BRANCH:-}" ]; then
    base_branch="origin/${BASE_BRANCH}"
else
    base_branch=""
fi

if [ "${group}" == "extra" ]; then
    ../internal_test_tools/tools/run.py --color --bot --junit
    exit
fi

case "${group}" in
    1) options=(--skip-test pylint --skip-test ansible-doc --skip-test validate-modules) ;;
    2) options=(                   --test      ansible-doc      --test validate-modules) ;;
    3) options=(--test pylint           plugins/modules/) ;;
    4) options=(--test pylint --exclude plugins/modules/) ;;
esac

# allow collection migration sanity tests for groups 3 and 4 to pass without updating this script during migration
network_path="lib/ansible/modules/network/"

if [ -d "${network_path}" ]; then
    if [ "${group}" -eq 3 ]; then
        options+=(--exclude "${network_path}")
    elif [ "${group}" -eq 4 ]; then
        options+=("${network_path}")
    fi
fi

# shellcheck disable=SC2086
ansible-test sanity --color -v --junit ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} \
    --docker --base-branch "${base_branch}" \
    "${options[@]}" --allow-disabled
