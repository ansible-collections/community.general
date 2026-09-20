#!/usr/bin/env bash
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
set -eux

# The consul_kv lookup plugin always runs on the controller, so both the
# Consul agent and the test that queries it are run against localhost here,
# rather than relying on ansible-test's usual (possibly separate) target host.

# EXPERIMENT: does this avoid the macOS crash? urllib resolves proxies via
# _scproxy on macOS, which initializes the Objective-C runtime inside the
# forked worker. Setting no_proxy makes getproxies() short-circuit on the
# environment and never reach _scproxy. Everything here talks to localhost,
# so no proxy is wanted anyway.
export no_proxy='*'

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook test_lookup_consul_kv.yml -v "$@"
