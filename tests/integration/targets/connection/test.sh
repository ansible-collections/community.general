#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

[ -f "${INVENTORY}" ]

# Run connection tests with both the default and C locale.

ansible-playbook test_connection.yml -i "${INVENTORY}" "$@"
