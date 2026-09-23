#!/usr/bin/env bash
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
set -eux

# The consul_kv lookup plugin always runs on the controller, so both the
# Consul agent and the test that queries it are run against localhost here,
# rather than relying on ansible-test's usual (possibly separate) target host.

# Everything here talks to localhost, so no proxy is ever wanted. This is also
# required on macOS: without it, resolving the system proxy configuration
# initializes the Objective-C runtime inside the forked worker and kills it
# ("A worker was found in a dead state"), see
# https://github.com/ansible/ansible/issues/49207. Any *_proxy variable makes
# getproxies() answer from the environment instead of asking the system.
export no_proxy='*'

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook test_lookup_consul_kv.yml -v "$@"
