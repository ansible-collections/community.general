#!/usr/bin/env bash
# Copyright (c) 2020, Thales Netherlands
# Copyright (c) 2021, Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
set -eux

ANSIBLE_ROLES_PATH=../ ANSIBLE_LOG_PATH=/tmp/ansible-test-merge-variables \
    ansible-playbook test_merge_lookup.yml "$@"
