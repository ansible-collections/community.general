#!/usr/bin/env bash

[[ -n "$DEBUG" || -n "$ANSIBLE_DEBUG" ]] && set -x

set -euo pipefail

cleanup() {
    echo "Cleanup"
    ansible-playbook playbooks/multipass_cleanup.yml
    echo "Done"
}

trap cleanup INT TERM EXIT

echo "Setup"
ANSIBLE_ROLES_PATH=.. ansible-playbook  playbooks/multipass_setup.yml

echo "Test multipass inventory 1"
ansible-playbook -i inventory_1.multipass.yml playbooks/test_inventory_1.yml

echo "Test multipass inventory 2"
ansible-playbook -i inventory_2.multipass.yml playbooks/test_inventory_2.yml
