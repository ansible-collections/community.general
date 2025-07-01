# -*- coding: utf-8 -*-
# Copyright (c) 2017, Brian Coca
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
name: yaml
short_description: YAML formatted files
description:
  - This cache uses YAML formatted, per host, files saved to the filesystem.
author: Brian Coca (@bcoca)
options:
  _uri:
    required: true
    description:
      - Path in which the cache plugin saves the files.
    env:
      - name: ANSIBLE_CACHE_PLUGIN_CONNECTION
    ini:
      - key: fact_caching_connection
        section: defaults
    type: string
  _prefix:
    description: User defined prefix to use when creating the files.
    env:
      - name: ANSIBLE_CACHE_PLUGIN_PREFIX
    ini:
      - key: fact_caching_prefix
        section: defaults
    type: string
  _timeout:
    default: 86400
    description: Expiration timeout in seconds for the cache plugin data. Set to 0 to never expire.
    env:
      - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT
    ini:
      - key: fact_caching_timeout
        section: defaults
    type: integer
        # TODO: determine whether it is OK to change to: type: float
"""


import codecs

import yaml

from ansible.parsing.yaml.loader import AnsibleLoader
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.plugins.cache import BaseFileCacheModule


class CacheModule(BaseFileCacheModule):
    """
    A caching module backed by yaml files.
    """

    def _load(self, filepath):
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            return AnsibleLoader(f).get_single_data()

    def _dump(self, value, filepath):
        with codecs.open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(value, f, Dumper=AnsibleDumper, default_flow_style=False)
