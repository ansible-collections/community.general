#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
module: plugin_requirements_info
short_description: Gather requirements for one or multiple plugins
description:
  - Gather requirements for one or multiple plugins.
version_added: 8.2.0
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.attributes.flow
attributes:
  action:
    support: full
  async:
    support: none
requirements: []
installable_requirements: []
options:
  plugins:
    description:
      - A list of plugins to query requirements for.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the plugin.
        required: true
        type: str
      type:
        description:
          - The type of the plugin.
          - Not all types are supported by all versions of ansible-core. Generally C(ansible-doc -t <type>) must work.
        default: 'module'
        type: str
        choices:
          # CONFIGURABLE_PLUGINS
          - become
          - cache
          - callback
          - cliconf
          - connection
          - httpapi
          - inventory
          - lookup
          - netconf
          - shell
          - vars
          # DOCUMENTABLE_PLUGINS
          - module
          - strategy
          - test
          - filter
  modules_on_remote:
    description:
      - Whether to assume that modules run on the remote, and not the controller.
      - Set to V(false) if you plan to run the module(s) on the controller.
    type: bool
    default: true

author:
  - Felix Fontein (@felixfontein)
'''

EXAMPLES = r'''
- name: Unconditionally shut down the machine with all defaults
  community.general.plugin_requirements_info:
    plugins:
      - name: community.general.plugin_requirements_info
  register: requirements

- name: Install system requirements
  ansible.builtin.package:
    name: "{{ requirements.system }}"
  when: "requirements.system"

- name: Install Python requirements
  ansible.builtin.pip:
    name: "{{ requirements.python }}"
  when: "requirements.python"
'''

RETURN = r'''
system:
  description:
    - A list of system requirements.
  type: list
  elements: str
  returned: success
  sample:
    - openssl

python:
  description:
    - A list of Python requirements.
  type: list
  elements: str
  returned: success
  sample:
    - cryptography
'''
