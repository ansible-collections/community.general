#!/usr/bin/env bash

set -eux

export ANSIBLE_TEST_PREFER_VENV=1  # see https://github.com/ansible/ansible/pull/73000#issuecomment-757012395; can be removed once Ansible 2.9 and ansible-base 2.10 support has been dropped
source virtualenv.sh

# The collection loader ignores paths which have more than one ansible_collections in it.
# That's why we have to copy this directory to a temporary place and run the test there.

# Create temporary folder
TEMPDIR=$(mktemp -d)
trap '{ rm -rf ${TEMPDIR}; }' EXIT

cp -r . "${TEMPDIR}"
cd "${TEMPDIR}"

ansible-playbook runme.yml "$@"
