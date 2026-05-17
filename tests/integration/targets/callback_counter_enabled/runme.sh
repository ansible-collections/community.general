#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eu

for arg in "$@"; do
    case "${arg}" in
        -v*) set -x; break ;;
    esac
done

export ANSIBLE_STDOUT_CALLBACK=community.general.counter_enabled
export ANSIBLE_NOCOLOR=true
export ANSIBLE_FORCE_COLOR=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INVENTORY="${SCRIPT_DIR}/inventory.yml"
PLAYBOOKS="${SCRIPT_DIR}/playbooks"

assert_in_output() {
    local description="$1"
    local pattern="$2"
    if ! echo "${output}" | grep -qE "${pattern}"; then
        echo "FAIL: ${description}"
        echo "Expected pattern: ${pattern}"
        echo "--- actual output ---"
        echo "${output}"
        exit 1
    fi
    echo "OK: ${description}"
}

# Test: task and host counters are shown in the N/M format
output=$(ansible-playbook "${PLAYBOOKS}/counting.yml" -i "${INVENTORY}" "$@")
assert_in_output "task counter: task 1 of 2" "^TASK 1/2 \["
assert_in_output "task counter: task 2 of 2" "^TASK 2/2 \["
assert_in_output "host counter: 1 of 3" "^ok: 1/3 \["
assert_in_output "host counter: 2 of 3" "^ok: 2/3 \["
assert_in_output "host counter: 3 of 3" "^ok: 3/3 \["

# Test: looped task shows one output line per item (regression for #8187)
output=$(ansible-playbook "${PLAYBOOKS}/loop_ok.yml" -i "${INVENTORY}" "$@")
assert_in_output "loop: item_a shown" "^ok: \[host1\] => \(item=item_a\)"
assert_in_output "loop: item_b shown" "^ok: \[host1\] => \(item=item_b\)"
assert_in_output "loop: item_c shown" "^ok: \[host1\] => \(item=item_c\)"

# Test: delegated looped task shows delegation target per item (regression for #8187)
output=$(ansible-playbook "${PLAYBOOKS}/delegated_loop_ok.yml" -i "${INVENTORY}" "$@")
assert_in_output "delegated loop: item_a shown with delegation" "^ok: \[host1 -> [^]]+\] => \(item=item_a\)"
assert_in_output "delegated loop: item_b shown with delegation" "^ok: \[host1 -> [^]]+\] => \(item=item_b\)"
assert_in_output "delegated loop: item_c shown with delegation" "^ok: \[host1 -> [^]]+\] => \(item=item_c\)"
