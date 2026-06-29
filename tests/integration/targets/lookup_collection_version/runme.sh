#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
