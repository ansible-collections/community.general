# (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
name: collection_version
author: Felix Fontein (@felixfontein)
version_added: "4.0.0"
short_description: Retrieves the version of an installed collection
description:
  - This lookup allows to query the version of an installed collection, and to determine whether a
    collection is installed at all.
  - By default it returns C(none) for non-existing collections and C(*) for collections without a
    version number. The latter should only happen in development environments, or when installing
    a collection from git which has no version in its C(galaxy.yml). This behavior can be adjusted
    by providing other values with I(result_not_found) and I(result_no_version).
options:
  _terms:
    description:
      - The collections to look for.
      - For example C(community.general).
    type: list
    elements: str
    required: true
  result_not_found:
    description:
      - The value to return when the collection could not be found.
      - By default, C(none) is returned.
    type: string
    default: ~
  result_no_version:
    description:
      - The value to return when the collection has no version number.
      - This can happen for collections installed from git which do not have a version number
        in C(galaxy.yml).
      - By default, C(*) is returned.
    type: string
    default: '*'
"""

EXAMPLES = """
- name: Check version of community.general
  ansible.builtin.debug:
    msg: "community.general version {{ lookup('community.general.collection_version', 'community.general') }}"
"""

RETURN = """
  _raw:
    description:
      - The version number of the collections listed as input.
      - If a collection can not be found, it will return the value provided in I(result_not_found).
        By default, this is C(none).
      - If a collection can be found, but the version not identified, it will return the value provided in
        I(result_no_version). By default, this is C(*). This can happen for collections installed
        from git which do not have a version number in C(galaxy.yml).
    type: list
    elements: str
"""

import json
import os
import re

import yaml

from ansible.errors import AnsibleLookupError
from ansible.module_utils.compat.importlib import import_module
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

    # Try to load galaxy.y(a)ml
    galaxy_path = os.path.join(path, 'galaxy.yml')
    galaxy_alt_path = os.path.join(path, 'galaxy.yaml')
    # galaxy.yaml was only supported in ansible-base 2.10 and ansible-core 2.11. Support was removed
    # in https://github.com/ansible/ansible/commit/595413d11346b6f26bb3d9df2d8e05f2747508a3 for
    # ansible-core 2.12.
    for path in (galaxy_path, galaxy_alt_path):
        if os.path.exists(path):
            return load_collection_meta_galaxy(path, no_version=no_version)

    return {}


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        result = []
        self.set_options(var_options=variables, direct=kwargs)
        not_found = self.get_option('result_not_found')
        no_version = self.get_option('result_no_version')

        for term in terms:
            if not FQCN_RE.match(term):
                raise AnsibleLookupError('"{term}" is not a FQCN'.format(term=term))

            try:
                collection_pkg = import_module('ansible_collections.{fqcn}'.format(fqcn=term))
            except ImportError:
                # Collection not found
                result.append(not_found)
                continue

            try:
                data = load_collection_meta(collection_pkg, no_version=no_version)
            except Exception as exc:
                raise AnsibleLookupError('Error while loading metadata for {fqcn}: {error}'.format(fqcn=term, error=exc))

            result.append(data.get('version', no_version))

        return result
