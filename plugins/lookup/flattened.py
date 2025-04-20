# -*- coding: utf-8 -*-
# Copyright (c) 2013, Serge van Ginderachter <serge@vanginderachter.be>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
name: flattened
author: Serge van Ginderachter (!UNKNOWN) <serge@vanginderachter.be>
short_description: return single list completely flattened
description:
  - Given one or more lists, this lookup will flatten any list elements found recursively until only 1 list is left.
options:
  _terms:
    description: Lists to flatten.
    type: list
    elements: raw
    required: true
notes:
  - Unlike the P(ansible.builtin.items#lookup) lookup which only flattens 1 level, this plugin will continue to flatten until
    it cannot find lists anymore.
  - Aka highlander plugin, there can only be one (list).
"""

EXAMPLES = r"""
- name: "'unnest' all elements into single list"
  ansible.builtin.debug:
    msg: "all in one list {{lookup('community.general.flattened', [1,2,3,[5,6]], ['a','b','c'], [[5,6,1,3], [34,'a','b','c']])}}"
"""

RETURN = r"""
_raw:
  description:
    - Flattened list.
  type: list
"""
from ansible.errors import AnsibleError
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase
from ansible.utils.listify import listify_lookup_plugin_terms


class LookupModule(LookupBase):

    def _check_list_of_one_list(self, term):
        # make sure term is not a list of one (list of one..) item
        # return the final non list item if so

        if isinstance(term, list) and len(term) == 1:
            term = term[0]
            if isinstance(term, list):
                term = self._check_list_of_one_list(term)

        return term

    def _do_flatten(self, terms, variables):

        ret = []
        for term in terms:
            term = self._check_list_of_one_list(term)

            if term == 'None' or term == 'null':
                # ignore undefined items
                break

            if isinstance(term, string_types):
                # convert a variable to a list
                try:
                    term2 = listify_lookup_plugin_terms(term, templar=self._templar)
                except TypeError:
                    # The loader argument is deprecated in ansible-core 2.14+. Fall back to
                    # pre-2.14 behavior for older ansible-core versions.
                    term2 = listify_lookup_plugin_terms(term, templar=self._templar, loader=self._loader)
                # but avoid converting a plain string to a list of one string
                if term2 != [term]:
                    term = term2

            if isinstance(term, list):
                # if it is a list, check recursively for items that are a list
                term = self._do_flatten(term, variables)
                ret.extend(term)
            else:
                ret.append(term)

        return ret

    def run(self, terms, variables=None, **kwargs):
        if not isinstance(terms, list):
            raise AnsibleError("with_flattened expects a list")

        self.set_options(var_options=variables, direct=kwargs)

        return self._do_flatten(terms, variables)
