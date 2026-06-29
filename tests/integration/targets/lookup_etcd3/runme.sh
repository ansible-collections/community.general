#!/usr/bin/env bash
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
set -eux

# The etcd3 Python library uses protobuf-generated code that is incompatible
# with protobuf >= 4.x unless the pure-Python implementation is selected.
# This must be set in the controller process so that lookup plugins are affected.
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook test_lookup_etcd3.yml -v "$@"
