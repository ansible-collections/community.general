#!/usr/bin/env bash
# Derived from ../connection_proxmox_pct_remote/runme.sh Copyright (c) 2025 Nils Stein (@mietzen) <github.nstein@mailbox.org>
# Copyright (c) 2025 Rui Lopes (@rgl) <ruilopes.com>
# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

# signal the wsl connection plugin that its running under the integration testing mode.
# NB while running integration tests, the mock wsl.exe implementation is actually
#    running on unix, instead of on running windows, so the wsl.exe command line
#    construction must use unix rules instead of windows rules.
export _ANSIBLE_TEST_WSL_CONNECTION_PLUGIN_Waeri5tepheeSha2fae8=1

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

./test.sh "$@"

ansible-playbook plugin-specific-tests.yml -i "./test_connection.inventory" \
    -e target_hosts=wsl \
    -e action_prefix= \
    -e local_tmp=/tmp/ansible-local \
    -e remote_tmp=/tmp/ansible-remote \
    "$@"
