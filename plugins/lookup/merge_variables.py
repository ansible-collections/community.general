# -*- coding: utf-8 -*-
# Copyright (c) 2020, Thales Netherlands
# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    author:
      - Roy Lenferink (@rlenferink)
      - Mark Ettema (@m-a-r-k-e)
    name: merge_variables
    short_description: merge variables with a certain suffix
    description:
        - This lookup returns the merged result of all variables in scope that match the given prefixes, suffixes, or
         regular expressions, optionally.
    version_added: 6.5.0
    options:
      _terms:
        description:
          - Depending on the value of O(pattern_type), this is a list of prefixes, suffixes, or regular expressions
            that will be used to match all variables that should be merged.
        required: true
        type: list
        elements: str
      pattern_type:
        description:
          - Change the way of searching for the specified pattern.
        type: str
        default: 'regex'
        choices:
          - prefix
          - suffix
          - regex
        env:
          - name: ANSIBLE_MERGE_VARIABLES_PATTERN_TYPE
        ini:
          - section: merge_variables_lookup
            key: pattern_type
      initial_value:
        description:
          - An initial value to start with.
        type: raw
      override:
        description:
          - Return an error, print a warning or ignore it when a key will be overwritten.
          - The default behavior V(error) makes the plugin fail when a key would be overwritten.
          - When V(warn) and V(ignore) are used, note that it is important to know that the variables
            are sorted by name before being merged. Keys for later variables in this order will overwrite
            keys of the same name for variables earlier in this order. To avoid potential confusion,
            better use O(override=error) whenever possible.
        type: str
        default: 'error'
        choices:
          - error
          - warn
          - ignore
        env:
          - name: ANSIBLE_MERGE_VARIABLES_OVERRIDE
        ini:
          - section: merge_variables_lookup
            key: override
"""

EXAMPLES = """
# Some example variables, they can be defined anywhere as long as they are in scope
test_init_list:
  - "list init item 1"
  - "list init item 2"

testa__test_list:
  - "test a item 1"

testb__test_list:
  - "test b item 1"

testa__test_dict:
  ports:
    - 1

testb__test_dict:
  ports:
    - 3


# Merge variables that end with '__test_dict' and store the result in a variable 'example_a'
example_a: "{{ lookup('community.general.merge_variables', '__test_dict', pattern_type='suffix') }}"

# The variable example_a now contains:
# ports:
#   - 1
#   - 3


# Merge variables that match the '^.+__test_list$' regular expression, starting with an initial value and store the
# result in a variable 'example_b'
example_b: "{{ lookup('community.general.merge_variables', '^.+__test_list$', initial_value=test_init_list) }}"

# The variable example_b now contains:
#   - "list init item 1"
#   - "list init item 2"
#   - "test a item 1"
#   - "test b item 1"
"""

RETURN = """
  _raw:
    description: In case the search matches list items, a list will be returned. In case the search matches dicts, a
     dict will be returned.
    type: raw
    elements: raw
"""

import re

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()


def _verify_and_get_type(variable):
    if isinstance(variable, list):
        return "list"
    elif isinstance(variable, dict):
        return "dict"
    else:
        raise AnsibleError("Not supported type detected, variable must be a list or a dict")


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(direct=kwargs)
        initial_value = self.get_option("initial_value", None)
        self._override = self.get_option('override', 'error')
        self._pattern_type = self.get_option('pattern_type', 'regex')

        ret = []
        for term in terms:
            if not isinstance(term, str):
                raise AnsibleError("Non-string type '{0}' passed, only 'str' types are allowed!".format(type(term)))

            ret.append(self._merge_vars(term, initial_value, variables))

        return ret

    def _var_matches(self, key, search_pattern):
        if self._pattern_type == "prefix":
            return key.startswith(search_pattern)
        elif self._pattern_type == "suffix":
            return key.endswith(search_pattern)
        elif self._pattern_type == "regex":
            matcher = re.compile(search_pattern)
            return matcher.search(key)

        return False

    def _merge_vars(self, search_pattern, initial_value, variables):
        display.vvv("Merge variables with {0}: {1}".format(self._pattern_type, search_pattern))
        var_merge_names = sorted([key for key in variables.keys() if self._var_matches(key, search_pattern)])
        display.vvv("The following variables will be merged: {0}".format(var_merge_names))

        prev_var_type = None
        result = None

        if initial_value is not None:
            prev_var_type = _verify_and_get_type(initial_value)
            result = initial_value

        for var_name in var_merge_names:
            var_value = self._templar.template(variables[var_name])  # Render jinja2 templates
            var_type = _verify_and_get_type(var_value)

            if prev_var_type is None:
                prev_var_type = var_type
            elif prev_var_type != var_type:
                raise AnsibleError("Unable to merge, not all variables are of the same type")

            if result is None:
                result = var_value
                continue

            if var_type == "dict":
                result = self._merge_dict(var_value, result, [var_name])
            else:  # var_type == "list"
                result += var_value

        return result

    def _merge_dict(self, src, dest, path):
        for key, value in src.items():
            if isinstance(value, dict):
                node = dest.setdefault(key, {})
                self._merge_dict(value, node, path + [key])
            elif isinstance(value, list) and key in dest:
                dest[key] += value
            else:
                if (key in dest) and dest[key] != value:
                    msg = "The key '{0}' with value '{1}' will be overwritten with value '{2}' from '{3}.{0}'".format(
                        key, dest[key], value, ".".join(path))

                    if self._override == "error":
                        raise AnsibleError(msg)
                    if self._override == "warn":
                        display.warning(msg)

                dest[key] = value

        return dest
