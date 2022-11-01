# -*- coding: utf-8 -*-
# Copyright (c) 2015-2021, Felix Fontein <felix@fontein.de>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
name: dependent
short_description: Composes a list with nested elements of other lists or dicts which can depend on previous loop variables
author: Felix Fontein (@felixfontein)
version_added: 3.1.0
description:
  - "Takes the input lists and returns a list with elements that are lists, dictionaries,
     or template expressions which evaluate to lists or dicts, composed of the elements of
     the input evaluated lists and dictionaries."
options:
  _terms:
    description:
      - A list where the elements are one-element dictionaries, mapping a name to a string, list, or dictionary.
        The name is the index that is used in the result object. The value is iterated over as described below.
      - If the value is a list, it is simply iterated over.
      - If the value is a dictionary, it is iterated over and returned as if they would be processed by the
        R(ansible.builtin.dict2items filter,ansible_collections.ansible.builtin.dict2items_filter).
      - If the value is a string, it is evaluated as Jinja2 expressions which can access the previously chosen
        elements with C(item.<index_name>). The result must be a list or a dictionary.
    type: list
    elements: dict
    required: true
"""

EXAMPLES = """
- name: Install/remove public keys for active admin users
  ansible.posix.authorized_key:
    user: "{{ item.admin.key }}"
    key: "{{ lookup('file', item.key.public_key) }}"
    state: "{{ 'present' if item.key.active else 'absent' }}"
  when: item.admin.value.active
  with_community.general.dependent:
    - admin: admin_user_data
    - key: admin_ssh_keys[item.admin.key]
  loop_control:
    # Makes the output readable, so that it doesn't contain the whole subdictionaries and lists
    label: "{{ [item.admin.key, 'active' if item.key.active else 'inactive', item.key.public_key] }}"
  vars:
    admin_user_data:
      admin1:
        name: Alice
        active: true
      admin2:
        name: Bob
        active: true
    admin_ssh_keys:
      admin1:
        - private_key: keys/private_key_admin1.pem
          public_key: keys/private_key_admin1.pub
          active: true
      admin2:
        - private_key: keys/private_key_admin2.pem
          public_key: keys/private_key_admin2.pub
          active: true
        - private_key: keys/private_key_admin2-old.pem
          public_key: keys/private_key_admin2-old.pub
          active: false

- name: Update DNS records
  community.aws.route53:
    zone: "{{ item.zone.key }}"
    record: "{{ item.prefix.key ~ '.' if item.prefix.key else '' }}{{ item.zone.key }}"
    type: "{{ item.entry.key }}"
    ttl: "{{ item.entry.value.ttl | default(3600) }}"
    value: "{{ item.entry.value.value }}"
    state: "{{ 'absent' if (item.entry.value.absent | default(False)) else 'present' }}"
    overwrite: true
  loop_control:
    # Makes the output readable, so that it doesn't contain the whole subdictionaries and lists
    label: |-
        {{ [item.zone.key, item.prefix.key, item.entry.key,
            item.entry.value.ttl | default(3600),
            item.entry.value.absent | default(False), item.entry.value.value] }}
  with_community.general.dependent:
    - zone: dns_setup
    - prefix: item.zone.value
    - entry: item.prefix.value
  vars:
    dns_setup:
      example.com:
        '':
          A:
            value:
            - 1.2.3.4
          AAAA:
            value:
            - "2a01:1:2:3::1"
        'test._domainkey':
          TXT:
            ttl: 300
            value:
            - '"k=rsa; t=s; p=MIGfMA..."'
      example.org:
        'www':
          A:
            value:
            - 1.2.3.4
            - 5.6.7.8
"""

RETURN = """
  _list:
    description:
      - A list composed of dictionaries whose keys are the variable names from the input list.
    type: list
    elements: dict
    sample:
      - key1: a
        key2: test
      - key1: a
        key2: foo
      - key1: b
        key2: bar
"""

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase
from ansible.template import Templar


class LookupModule(LookupBase):
    def __evaluate(self, expression, templar, variables):
        """Evaluate expression with templar.

        ``expression`` is the expression to evaluate.
        ``variables`` are the variables to use.
        """
        templar.available_variables = variables or {}
        return templar.template("{0}{1}{2}".format("{{", expression, "}}"), cache=False)

    def __process(self, result, terms, index, current, templar, variables):
        """Fills ``result`` list with evaluated items.

        ``result`` is a list where the resulting items are placed.
        ``terms`` is the parsed list of terms
        ``index`` is the current index to be processed in the list.
        ``current`` is a dictionary where the first ``index`` values are filled in.
        ``variables`` are the variables currently available.
        """
        # If we are done, add to result list:
        if index == len(terms):
            result.append(current.copy())
            return

        key, expression, values = terms[index]

        if expression is not None:
            # Evaluate expression in current context
            vars = variables.copy()
            vars['item'] = current.copy()
            try:
                values = self.__evaluate(expression, templar, variables=vars)
            except Exception as e:
                raise AnsibleLookupError(
                    'Caught "{error}" while evaluating {key!r} with item == {item!r}'.format(
                        error=e, key=key, item=current))

        if isinstance(values, Mapping):
            for idx, val in sorted(values.items()):
                current[key] = dict([('key', idx), ('value', val)])
                self.__process(result, terms, index + 1, current, templar, variables)
        elif isinstance(values, Sequence):
            for elt in values:
                current[key] = elt
                self.__process(result, terms, index + 1, current, templar, variables)
        else:
            raise AnsibleLookupError(
                'Did not obtain dictionary or list while evaluating {key!r} with item == {item!r}, but {type}'.format(
                    key=key, item=current, type=type(values)))

    def run(self, terms, variables=None, **kwargs):
        """Generate list."""
        self.set_options(var_options=variables, direct=kwargs)

        result = []
        if len(terms) > 0:
            templar = Templar(loader=self._templar._loader)
            data = []
            vars_so_far = set()
            for index, term in enumerate(terms):
                if not isinstance(term, Mapping):
                    raise AnsibleLookupError(
                        'Parameter {index} must be a dictionary, got {type}'.format(
                            index=index, type=type(term)))
                if len(term) != 1:
                    raise AnsibleLookupError(
                        'Parameter {index} must be a one-element dictionary, got {count} elements'.format(
                            index=index, count=len(term)))
                k, v = list(term.items())[0]
                if k in vars_so_far:
                    raise AnsibleLookupError(
                        'The variable {key!r} appears more than once'.format(key=k))
                vars_so_far.add(k)
                if isinstance(v, string_types):
                    data.append((k, v, None))
                elif isinstance(v, (Sequence, Mapping)):
                    data.append((k, None, v))
                else:
                    raise AnsibleLookupError(
                        'Parameter {key!r} (index {index}) must have a value of type string, dictionary or list, got type {type}'.format(
                            index=index, key=k, type=type(v)))
            self.__process(result, data, 0, {}, templar, variables)
        return result
