#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -o pipefail -eux

# Fix for https://github.com/ansible-community/antsibull-nox/issues/222#issuecomment-4778928615
# caused by https://github.com/ansible/azure-pipelines-test-container/blob/7714d81f64f268bbb10779e1265d312128607b76/Containerfile#L4
export PATH="${PATH//:~\//:${HOME}/}"

nox_session="$1"

export PYTHONIOENCODING='utf-8'

if [ -n "${COVERAGE:-}" ]; then
    # on-demand coverage reporting triggered by setting the COVERAGE environment variable to a non-empty value
    export COVERAGE="--coverage"
elif [[ "${COMMIT_MESSAGE}" =~ ci_coverage ]]; then
    # on-demand coverage reporting triggered by having 'ci_coverage' in the latest commit message
    export COVERAGE="--coverage"
else
    # on-demand coverage reporting disabled (default behavior, always-on coverage reporting remains enabled)
    export COVERAGE="--coverage-check"
fi

if [ -n "${COMPLETE:-}" ]; then
    # disable change detection triggered by setting the COMPLETE environment variable to a non-empty value
    export ANTSIBULL_CHANGE_DETECTION=""
elif [[ "${COMMIT_MESSAGE}" =~ ci_complete ]]; then
    # disable change detection triggered by having 'ci_complete' in the latest commit message
    export ANTSIBULL_CHANGE_DETECTION=""
elif [ "${IS_PULL_REQUEST:-}" == "true" ]; then
    # enable change detection for PRs (default behavior)
    export ANTSIBULL_CHANGE_DETECTION="true"
    export ANTSIBULL_BASE_BRANCH="${SYSTEM_PULLREQUEST_TARGETBRANCH}"
    # Create a branch for the current HEAD, which happens to be a merge commit
    git checkout -b "pull-request-branch"
    # Name the target branch
    git branch "${SYSTEM_PULLREQUEST_TARGETBRANCH}" --track "origin/${SYSTEM_PULLREQUEST_TARGETBRANCH}"
    # Show branches
    git branch -vv
else
    # disable change detection for pushes and scheduled runs
    export ANTSIBULL_CHANGE_DETECTION=""
fi

if [[ "${COVERAGE:-}" == "--coverage" ]]; then
    export ANTSIBULL_NOX_TIMEOUT=60
else
    export ANTSIBULL_NOX_TIMEOUT=50
fi

if [ "${IS_PULL_REQUEST:-}" == "true" ]; then
    export ANTSIBULL_NOX_INTEGRATION_ALLOW_UNSTABLE_CHANGED="true"
fi

export FORCE_COLOR=1
export ANTSIBULL_NOX_IGNORE_INSTALLED_COLLECTIONS="true"
export ANTSIBULL_NOX_COVERAGE_DESTINATION="${COVERAGE_DESTINATION_DIRECTORY}"
export ANTSIBULL_NOX_COVERAGE_ANALYSIS_FILE="${COVERAGE_DESTINATION_DIRECTORY}/coverage-analyze-targets.json"
export ANTSIBULL_NOX_COVERAGE_NO_XML="true"

if [ "${nox_session}" == "extra-sanity-tests" ]; then
    export ANTSIBULL_NOX_OUTPUT_BOT_DIRECTORY="tests/output/bot"
    nox --reuse-existing-virtualenvs --no-install
else
    nox --reuse-existing-virtualenvs --no-install -e "${nox_session}" -- ${COVERAGE}
fi
