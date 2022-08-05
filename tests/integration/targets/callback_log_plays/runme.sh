#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

set -eux

# ANSIBLE_CALLBACK_WHITELIST has been deprecated in ansible-base 2.11, ANSIBLE_CALLBACKS_ENABLED should be used
export ANSIBLE_CALLBACK_WHITELIST="community.general.log_plays,${ANSIBLE_CALLBACK_WHITELIST:-}"
export ANSIBLE_CALLBACKS_ENABLED="community.general.log_plays,${ANSIBLE_CALLBACKS_ENABLED:-}"

# run play, should create log and dir if needed
export ANSIBLE_LOG_FOLDER="logit"
ansible-playbook ping_log.yml -v "$@"
[[ -f "${ANSIBLE_LOG_FOLDER}/localhost" ]]

# now force it to fail
export ANSIBLE_LOG_FOLDER="logit.file"
touch "${ANSIBLE_LOG_FOLDER}"
ansible-playbook ping_log.yml -v "$@" 2>&1| grep 'Failure using method (v2_runner_on_ok) in callback plugin'
[[ ! -f "${ANSIBLE_LOG_FOLDER}/localhost" ]]
