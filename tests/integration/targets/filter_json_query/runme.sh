#!/usr/bin/env bash

set -eux

# Requirements have to be installed prior to running ansible-playbook
# because plugins and requirements are loaded before the task runs

ANSIBLE_ROLES_PATH=../ ansible-playbook setup.yml "$@"

ANSIBLE_ROLES_PATH=../ ansible-playbook runme.yml "$@"
