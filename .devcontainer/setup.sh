#!/usr/bin/env bash
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

sudo chown -R vscode:vscode /workspace/

pip install -U pip
pip install -r .devcontainer/requirements-dev.txt
pip install -r tests/unit/requirements.txt

export ANSIBLE_COLLECTIONS_PATH=/workspace:${ANSIBLE_COLLECTIONS_PATH}
ansible-galaxy collection install -v -r tests/unit/requirements.yml
ansible-galaxy collection install -v -r tests/integration/requirements.yml

pre-commit install
