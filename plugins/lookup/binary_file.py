# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

DOCUMENTATION = r"""
name: binary_file
author: Felix Fontein (@felixfontein)
short_description: Read binary file and return it Base64 encoded
version_added: 11.2.0
description:
  - This lookup returns the contents from a file on the Ansible controller's file system.
  - The file is read as a binary file and its contents are returned Base64 encoded.
    This is similar to using P(ansible.builtin.file#lookup) combined with P(ansible.builtin.b64encode#filter),
    except that P(ansible.builtin.file#lookup) does not support binary files as it interprets the contents as UTF-8,
    which can cause the wrong content being Base64 encoded.
options:
  _terms:
    description:
      - Paths of the files to read.
      - Relative paths will be searched for in different places. See R(Ansible task paths, playbook_task_paths) for more details.
    required: true
    type: list
    elements: str
  not_exist:
    description:
      - Determine how to react if the specified file cannot be found.
    type: str
    choices:
      error: Raise an error.
      empty: Return an empty string for the file.
      empty_str:
        - Return the string C(empty) for the file.
        - This cannot be confused with Base64 encoding due to the missing padding.
    default: error
notes:
  - This lookup does not understand 'globbing' - use the P(ansible.builtin.fileglob#lookup) lookup instead.
seealso:
  - plugin: ansible.builtin.b64decode
    plugin_type: filter
    description: >-
      The b64decode filter can be used to decode Base64 encoded data.
      Note that Ansible cannot handle binary data, the data will be interpreted as UTF-8 text!
  - plugin: ansible.builtin.file
    plugin_type: lookup
    description: You can use this lookup plugin to read text files from the Ansible controller.
  - module: ansible.builtin.slurp
    description: >-
      Also allows to read binary files Base64 encoded, but from remote targets.
      With C(delegate_to: localhost) can be redirected to run on the controller, but you have to know the path to the file to read.
      Both this plugin and P(ansible.builtin.file#lookup) use some search path logic to for example also find files in the C(files)
      directory of a role.
  - ref: playbook_task_paths
    description: Search paths used for relative files.
"""

EXAMPLES = r"""
---
- name: Output Base64 contents of binary files on screen
  ansible.builtin.debug:
    msg: "Content: {{ lookup('community.general.binary_file', item) }}"
  loop:
    - some-binary-file.bin
"""

RETURN = r"""
_raw:
  description:
    - Base64 encoded content of requested files, or an empty string resp. the string C(empty), depending on the O(not_exist) option.
    - This list contains one string per element of O(_terms) in the same order as O(_terms).
  type: list
  elements: str
  returned: success
"""

import base64

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase

from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        not_exist = self.get_option("not_exist")

        result = []
        for term in terms:
            display.debug(f"Searching for binary file: {term!r}")
            path = self.find_file_in_search_path(variables, "files", term, ignore_missing=(not_exist != "error"))
            display.vvvv(f"community.general.binary_file lookup using {path} as file")

            if not path:
                if not_exist == "empty":
                    result.append("")
                    continue
                if not_exist == "empty_str":
                    result.append("empty")
                    continue
                raise AnsibleLookupError(f"Could not locate file in community.general.binary_file lookup: {term}")

            try:
                with open(path, "rb") as f:
                    result.append(base64.b64encode(f.read()).decode("utf-8"))
            except Exception as exc:
                raise AnsibleLookupError(f"Error while reading {path}: {exc}")

        return result
