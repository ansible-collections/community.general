#!/usr/bin/env bash
# Copyright (c) 2025 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

./test.sh "$@"

ansible-playbook plugin-specific-tests.yml -i "./test_connection.inventory" \
    -e target_hosts="proxmox_pct_remote" \
    -e action_prefix= \
    -e local_tmp=/tmp/ansible-local \
    -e remote_tmp=/tmp/ansible-remote \
    "$@"
