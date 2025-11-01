# Copyright (c) 2023, Steffen Scheib <steffen@scheib.me>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: from_ini
short_description: Converts INI text input into a dictionary
version_added: 8.2.0
author: Steffen Scheib (@sscheib)
description:
  - Converts INI text input into a dictionary.
options:
  _input:
    description: A string containing an INI document.
    type: string
    required: true
"""

EXAMPLES = r"""
- name: Slurp an INI file
  ansible.builtin.slurp:
    src: /etc/rhsm/rhsm.conf
  register: rhsm_conf

- name: Display the INI file as dictionary
  ansible.builtin.debug:
    var: rhsm_conf.content | b64decode | community.general.from_ini

- name: Set a new dictionary fact with the contents of the INI file
  ansible.builtin.set_fact:
    rhsm_dict: >-
      {{
          rhsm_conf.content | b64decode | community.general.from_ini
      }}
"""

RETURN = r"""
_value:
  description: A dictionary representing the INI file.
  type: dictionary
"""


from io import StringIO
from configparser import ConfigParser

from ansible.errors import AnsibleFilterError


class IniParser(ConfigParser):
    """Implements a configparser which is able to return a dict"""

    def __init__(self):
        super().__init__(interpolation=None)
        self.optionxform = str

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop("__name__", None)

        if self._defaults:
            d["DEFAULT"] = dict(self._defaults)

        return d


def from_ini(obj):
    """Read the given string as INI file and return a dict"""

    if not isinstance(obj, str):
        raise AnsibleFilterError(f"from_ini requires a str, got {type(obj)}")

    parser = IniParser()

    try:
        parser.read_file(StringIO(obj))
    except Exception as ex:
        raise AnsibleFilterError(f"from_ini failed to parse given string: {ex}", orig_exc=ex)

    return parser.as_dict()


class FilterModule:
    """Query filter"""

    def filters(self):
        return {"from_ini": from_ini}
