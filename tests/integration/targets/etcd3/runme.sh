#!/usr/bin/env bash
#
# 2020, SCC France, Eric Belhomme <ebelhomme@fr.scc.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Copyright: (c) 2018, Ansible Project

set -eux

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook dependencies.yml -v "$@"

ANSIBLE_ROLES_PATH=../ \
    ansible-playbook test_etcd3.yml -v "$@"
