# -*- coding: utf-8 -*-
# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
name: random_pet
author:
  - Abhijeet Kasurde (@Akasurde)
short_description: Generates random pet names
version_added: '3.1.0'
requirements:
  - petname U(https://github.com/dustinkirkland/python-petname)
description:
  - Generates random pet names that can be used as unique identifiers for the resources.
options:
  words:
    description:
      - The number of words in the pet name.
    default: 2
    type: int
  length:
    description:
      - The maximal length of every component of the pet name.
      - Values below 3 will be set to 3 by petname.
    default: 6
    type: int
  prefix:
    description: A string to prefix with the name.
    type: str
  separator:
    description: The character to separate words in the pet name.
    default: "-"
    type: str
"""

EXAMPLES = r"""
- name: Generate pet name
  ansible.builtin.debug:
    var: lookup('community.general.random_pet')
  # Example result: 'loving-raptor'

- name: Generate pet name with 3 words
  ansible.builtin.debug:
    var: lookup('community.general.random_pet', words=3)
  # Example result: 'fully-fresh-macaw'

- name: Generate pet name with separator
  ansible.builtin.debug:
    var: lookup('community.general.random_pet', separator="_")
  # Example result: 'causal_snipe'

- name: Generate pet name with length
  ansible.builtin.debug:
    var: lookup('community.general.random_pet', length=7)
  # Example result: 'natural-peacock'
"""

RETURN = r"""
_raw:
  description: A one-element list containing a random pet name.
  type: list
  elements: str
"""

try:
    import petname

    HAS_PETNAME = True
except ImportError:
    HAS_PETNAME = False

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        if not HAS_PETNAME:
            raise AnsibleError('Python petname library is required. '
                               'Please install using "pip install petname"')

        self.set_options(var_options=variables, direct=kwargs)
        words = self.get_option('words')
        length = self.get_option('length')
        prefix = self.get_option('prefix')
        separator = self.get_option('separator')

        values = petname.Generate(words=words, separator=separator, letters=length)
        if prefix:
            values = f"{prefix}{separator}{values}"

        return [values]
