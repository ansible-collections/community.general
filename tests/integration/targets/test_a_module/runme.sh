#!/usr/bin/env bash

set -eux

source virtualenv.sh

# The collection loader ignores paths which have more than one ansible_collections in it.
# That's why we have to copy this directory to a temporary place and run the test there.

# Create temporary folder
TEMPDIR=$(mktemp -d)
trap '{ rm -rf ${TEMPDIR}; }' EXIT

cp -r . "${TEMPDIR}"
cd "${TEMPDIR}"

ansible-playbook runme.yml "$@"
