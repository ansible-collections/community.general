#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail -eux

# Fix for https://github.com/ansible-community/antsibull-nox/issues/222#issuecomment-4778928615
# caused by https://github.com/ansible/azure-pipelines-test-container/blob/7714d81f64f268bbb10779e1265d312128607b76/Containerfile#L4
export PATH="${PATH//:~\//:${HOME}/}"

nox_session="$1"

docker images ansible/ansible
docker images quay.io/ansible/*
docker ps

for container in $(docker ps --format '{{.Image}} {{.ID}}' | grep -v -e '^drydock/' -e '^quay.io/ansible/azure-pipelines-test-container:' | sed 's/^.* //'); do
    docker rm -f "${container}" || true  # ignore errors
done

docker ps
command -v python
python -V

function retry
{
    # shellcheck disable=SC2034
    for repetition in 1 2 3; do
        set +e
        "$@"
        result=$?
        set -e
        if [ ${result} == 0 ]; then
            return ${result}
        fi
        echo "@* -> ${result}"
    done
    echo "Command '@*' failed 3 times!"
    exit 255
}

command -v pip
pip --version
pip list --disable-pip-version-check
retry pip install https://github.com/ansible-community/antsibull-nox/archive/main.tar.gz --disable-pip-version-check

export PYTHONIOENCODING='utf-8'

export FORCE_COLOR=1
export ANTSIBULL_NOX_IGNORE_INSTALLED_COLLECTIONS="true"

if [ "${nox_session}" == "extra-sanity-tests" ]; then
    # We need the ansible-galaxy CLI tool to install collection dependencies
    retry pip install ansible-core --disable-pip-version-check
    nox --verbose --install-only
else
    nox --verbose --install-only -e "${nox_session}"
fi
