#!/usr/bin/env bash

set -eux

pip install hashids

ANSIBLE_ROLES_PATH=../ ansible-playbook runme.yml "$@"
