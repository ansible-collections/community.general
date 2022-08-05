#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Generate code coverage reports for uploading to Azure Pipelines and codecov.io.

set -o pipefail -eu

PATH="${PWD}/bin:${PATH}"

if ! ansible-test --help >/dev/null 2>&1; then
    # Install the devel version of ansible-test for generating code coverage reports.
    # This is only used by Ansible Collections, which are typically tested against multiple Ansible versions (in separate jobs).
    # Since a version of ansible-test is required that can work the output from multiple older releases, the devel version is used.
    pip install https://github.com/ansible/ansible/archive/devel.tar.gz --disable-pip-version-check
fi

ansible-test coverage xml --group-by command --stub --venv --venv-system-site-packages --color -v
