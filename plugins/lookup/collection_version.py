# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
name: collection_version
author: Felix Fontein (@felixfontein)
version_added: "4.0.0"
short_description: Retrieves the version of an installed collection
description:
  - This lookup allows to query the version of an installed collection, and to determine whether a collection is installed
    at all.
  - By default it returns V(none) for non-existing collections and V(*) for collections without a version number. The latter
    should only happen in development environments, or when installing a collection from git which has no version in its C(galaxy.yml).
    This behavior can be adjusted by providing other values with O(result_not_found) and O(result_no_version).
options:
  _terms:
    description:
      - The collections to look for.
      - For example V(community.general).
    type: list
    elements: str
    required: true
  result_not_found:
    description:
      - The value to return when the collection could not be found.
      - By default, V(none) is returned.
    type: string
    default: ~
  result_no_version:
    description:
      - The value to return when the collection has no version number.
      - This can happen for collections installed from git which do not have a version number in C(galaxy.yml).
      - By default, V(*) is returned.
    type: string
    default: '*'
"""

EXAMPLES = r"""
- name: Check version of community.general
  ansible.builtin.debug:
    msg: "community.general version {{ lookup('community.general.collection_version', 'community.general') }}"
"""

RETURN = r"""
_raw:
  description:
    - The version number of the collections listed as input.
    - If a collection can not be found, it will return the value provided in O(result_not_found). By default, this is V(none).
    - If a collection can be found, but the version not identified, it will return the value provided in O(result_no_version).
      By default, this is V(*). This can happen for collections installed from git which do not have a version number in V(galaxy.yml).
  type: list
  elements: str
"""

import json
import os
import re
from importlib import import_module

import yaml

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase


FQCN_RE = re.compile(r'^[A-Za-z0-9_]+\.[A-Za-z0-9_]+$')


def load_collection_meta_manifest(manifest_path):
    with open(manifest_path, 'rb') as f:
        meta = json.load(f)
    return {
        'version': meta['collection_info']['version'],
    }


def load_collection_meta_galaxy(galaxy_path, no_version='*'):
    with open(galaxy_path, 'rb') as f:
        meta = yaml.safe_load(f)
    return {
        'version': meta.get('version') or no_version,
    }


def load_collection_meta(collection_pkg, no_version='*'):
    path = os.path.dirname(collection_pkg.__file__)

    # Try to load MANIFEST.json
    manifest_path = os.path.join(path, 'MANIFEST.json')
    if os.path.exists(manifest_path):
        return load_collection_meta_manifest(manifest_path)

    # Try to load galaxy.yml
    galaxy_path = os.path.join(path, 'galaxy.yml')
    if os.path.exists(galaxy_path):
        return load_collection_meta_galaxy(galaxy_path, no_version=no_version)

    return {}


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        result = []
        self.set_options(var_options=variables, direct=kwargs)
        not_found = self.get_option('result_not_found')
        no_version = self.get_option('result_no_version')

        for term in terms:
            if not FQCN_RE.match(term):
                raise AnsibleLookupError(f'"{term}" is not a FQCN')

            try:
                collection_pkg = import_module(f'ansible_collections.{term}')
            except ImportError:
                # Collection not found
                result.append(not_found)
                continue

            try:
                data = load_collection_meta(collection_pkg, no_version=no_version)
            except Exception as exc:
                raise AnsibleLookupError(f'Error while loading metadata for {term}: {exc}')

            result.append(data.get('version', no_version))

        return result
