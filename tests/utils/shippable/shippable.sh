#!/usr/bin/env bash

set -o pipefail -eux

declare -a args
IFS='/:' read -ra args <<< "$1"

script="${args[0]}"

test="$1"

docker images ansible/ansible
docker images quay.io/ansible/*
docker ps

for container in $(docker ps --format '{{.Image}} {{.ID}}' | grep -v '^drydock/' | sed 's/^.* //'); do
    docker rm -f "${container}" || true  # ignore errors
done

docker ps

if [ -d /home/shippable/cache/ ]; then
    ls -la /home/shippable/cache/
fi

command -v python
python -V

command -v pip
pip --version
pip list --disable-pip-version-check
pip install https://github.com/ansible/ansible/archive/devel.tar.gz --disable-pip-version-check

export ANSIBLE_COLLECTIONS_PATHS="${HOME}/.ansible"
SHIPPABLE_RESULT_DIR="$(pwd)/shippable"
TEST_DIR="${ANSIBLE_COLLECTIONS_PATHS}/ansible_collections/community/general"
mkdir -p "${TEST_DIR}"
cp -aT "${SHIPPABLE_BUILD_DIR}" "${TEST_DIR}"
cd "${TEST_DIR}"

# STAR: HACK install dependencies
ansible-galaxy -vvv collection install ansible.posix
ansible-galaxy -vvv collection install community.crypto
ansible-galaxy -vvv collection install ansible.netcommon
ansible-galaxy -vvv collection install ovirt.ovirt_collection
ansible-galaxy -vvv collection install cisco.mso
ansible-galaxy -vvv collection install cisco.intersight
ansible-galaxy -vvv collection install check_point.mgmt
ansible-galaxy -vvv collection install community.kubernetes
ansible-galaxy -vvv collection install f5networks.f5_modules
ansible-galaxy -vvv collection install fortinet.fortios
ansible-galaxy -vvv collection install cisco.aci
ansible-galaxy -vvv collection install google.cloud
ansible-galaxy -vvv collection install netapp.ontap

# unit tests
ansible-galaxy -vvv collection install cisco.meraki
ansible-galaxy -vvv collection install junipernetworks.junos

# END: HACK

export PYTHONIOENCODING='utf-8'

if [ "${JOB_TRIGGERED_BY_NAME:-}" == "nightly-trigger" ]; then
    COVERAGE=yes
    COMPLETE=yes
fi

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
    export CHANGED=""
elif [[ "${COMMIT_MESSAGE}" =~ ci_complete ]]; then
    # disable change detection triggered by having 'ci_complete' in the latest commit message
    export CHANGED=""
else
    # enable change detection (default behavior)
    export CHANGED="--changed"
fi

if [ "${IS_PULL_REQUEST:-}" == "true" ]; then
    # run unstable tests which are targeted by focused changes on PRs
    export UNSTABLE="--allow-unstable-changed"
else
    # do not run unstable tests outside PRs
    export UNSTABLE=""
fi

# remove empty core/extras module directories from PRs created prior to the repo-merge
find plugins -type d -empty -print -delete

function cleanup
{
    # for complete on-demand coverage generate a report for all files with no coverage on the "sanity/5" job so we only have one copy
    if [ "${COVERAGE}" == "--coverage" ] && [ "${CHANGED}" == "" ] && [ "${test}" == "sanity/5" ]; then
        stub="--stub"
        # trigger coverage reporting for stubs even if no other coverage data exists
        mkdir -p tests/output/coverage/
    else
        stub=""
    fi

    if [ -d tests/output/coverage/ ]; then
        if find tests/output/coverage/ -mindepth 1 -name '.*' -prune -o -print -quit | grep -q .; then
            process_coverage='yes'  # process existing coverage files
        elif [ "${stub}" ]; then
            process_coverage='yes'  # process coverage when stubs are enabled
        else
            process_coverage=''
        fi

        if [ "${process_coverage}" ]; then
            # use python 3.7 for coverage to avoid running out of memory during coverage xml processing
            # only use it for coverage to avoid the additional overhead of setting up a virtual environment for a potential no-op job
            virtualenv --python /usr/bin/python3.7 ~/ansible-venv
            set +ux
            . ~/ansible-venv/bin/activate
            set -ux

            # shellcheck disable=SC2086
            ansible-test coverage xml --color --requirements --group-by command --group-by version ${stub:+"$stub"}
            cp -a tests/output/reports/coverage=*.xml "$SHIPPABLE_RESULT_DIR/codecoverage/"

            # analyze and capture code coverage aggregated by integration test target
            ansible-test coverage analyze targets generate -v "$SHIPPABLE_RESULT_DIR/testresults/coverage-analyze-targets.json"

            # upload coverage report to codecov.io only when using complete on-demand coverage
            if [ "${COVERAGE}" == "--coverage" ] && [ "${CHANGED}" == "" ]; then
                for file in tests/output/reports/coverage=*.xml; do
                    flags="${file##*/coverage=}"
                    flags="${flags%-powershell.xml}"
                    flags="${flags%.xml}"
                    # remove numbered component from stub files when converting to tags
                    flags="${flags//stub-[0-9]*/stub}"
                    flags="${flags//=/,}"
                    flags="${flags//[^a-zA-Z0-9_,]/_}"

                    bash <(curl -s https://codecov.io/bash) \
                        -f "${file}" \
                        -F "${flags}" \
                        -n "${test}" \
                        -t 20636cf5-4d6a-4b9a-8d2d-6f22ebbaa752 \
                        -X coveragepy \
                        -X gcov \
                        -X fix \
                        -X search \
                        -X xcode \
                    || echo "Failed to upload code coverage report to codecov.io: ${file}"
                done
            fi
        fi
    fi

    if [ -d  tests/output/junit/ ]; then
      cp -aT tests/output/junit/ "$SHIPPABLE_RESULT_DIR/testresults/"
    fi

    if [ -d tests/output/data/ ]; then
      cp -a tests/output/data/ "$SHIPPABLE_RESULT_DIR/testresults/"
    fi

    if [ -d  tests/output/bot/ ]; then
      cp -aT tests/output/bot/ "$SHIPPABLE_RESULT_DIR/testresults/"
    fi
}

trap cleanup EXIT

if [[ "${COVERAGE:-}" == "--coverage" ]]; then
    timeout=60
else
    timeout=50
fi

ansible-test env --dump --show --timeout "${timeout}" --color -v

"tests/utils/shippable/check_matrix.py"
"tests/utils/shippable/${script}.sh" "${test}"
