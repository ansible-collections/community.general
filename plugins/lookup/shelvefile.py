# Copyright (c) 2015, Alejandro Guirao <lekumberri@gmail.com>
# Copyright (c) 2012-17 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: shelvefile
author: Alejandro Guirao (!UNKNOWN) <lekumberri@gmail.com>
short_description: Read keys from Python shelve file
description:
  - Read keys from Python shelve file.
options:
  _terms:
    description: Sets of key value pairs of parameters.
    type: list
    elements: str
  key:
    description: Key to query.
    type: str
    required: true
  file:
    description: Path to shelve file.
    type: path
    required: true
"""

EXAMPLES = r"""
---
- name: Retrieve a string value corresponding to a key inside a Python shelve file
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.shelvefile', 'file=path_to_some_shelve_file.db key=key_to_retrieve') }}"
"""

RETURN = r"""
_list:
  description: Value(s) of key(s) in shelve file(s).
  type: list
  elements: str
"""
import shelve

from ansible.errors import AnsibleError, AnsibleAssertionError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_bytes, to_text


class LookupModule(LookupBase):
    def read_shelve(self, shelve_filename, key):
        """
        Read the value of "key" from a shelve file
        """
        d = shelve.open(to_bytes(shelve_filename))
        res = d.get(key, None)
        d.close()
        return res

    def run(self, terms, variables=None, **kwargs):
        if not isinstance(terms, list):
            terms = [terms]

        ret = []

        for term in terms:
            paramvals = {"file": None, "key": None}
            params = term.split()

            try:
                for param in params:
                    name, value = param.split("=")
                    if name not in paramvals:
                        raise AnsibleAssertionError(f"{name} not in paramvals")
                    paramvals[name] = value

            except (ValueError, AssertionError) as e:
                # In case "file" or "key" are not present
                raise AnsibleError(e)

            key = paramvals["key"]

            # Search also in the role/files directory and in the playbook directory
            shelvefile = self.find_file_in_search_path(variables, "files", paramvals["file"])

            if shelvefile:
                res = self.read_shelve(shelvefile, key)
                if res is None:
                    raise AnsibleError(f"Key {key} not found in shelve file {shelvefile}")
                # Convert the value read to string
                ret.append(to_text(res))
                break
            else:
                raise AnsibleError(f"Could not locate shelve file in lookup: {paramvals['file']}")

        return ret
