#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

platform="${args[0]}"
version="${args[1]}"

if [ "${#args[@]}" -gt 2 ]; then
    target="azp/posix/${args[2]}/"
else
    target="azp/posix/"
fi

stage="${S:-prod}"
provider="${P:-default}"

if [ "${platform}" == "rhel" ] && [[ "${version}" =~ ^8 ]]; then
    echo "pynacl >= 1.4.0, < 1.5.0; python_version == '3.6'" >> tests/utils/constraints.txt
fi

# shellcheck disable=SC2086
ansible-test integration --color -v --retry-on-error "${target}" ${COVERAGE:+"$COVERAGE"} ${CHANGED:+"$CHANGED"} ${UNSTABLE:+"$UNSTABLE"} \
    --remote "${platform}/${version}" --remote-terminate always --remote-stage "${stage}" --remote-provider "${provider}"
