#!/usr/bin/env bash

set -eux

export ANSIBLE_TEST_PREFER_VENV=1  # see https://github.com/ansible/ansible/pull/73000#issuecomment-757012395; can be removed once Ansible 2.9 and ansible-base 2.10 support has been dropped
source virtualenv.sh

# Requirements have to be installed prior to running ansible-playbook
# because plugins and requirements are loaded before the task runs

pip install jmespath

ANSIBLE_ROLES_PATH=../ ansible-playbook runme.yml "$@"
