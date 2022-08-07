# -*- coding: utf-8 -*-
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: random_mac
  short_description: Generate a random MAC address
  description:
    - Generates random networking interfaces MAC addresses for a given prefix.
  options:
    _input:
      description: A string prefix to use as a basis for the random MAC generated.
      type: string
      required: true
    seed:
      description:
        - A randomization seed to initialize the process, used to get repeatable results.
        - If no seed is provided, a system random source such as C(/dev/urandom) is used.
      required: false
      type: string
'''

EXAMPLES = '''
- name: Random MAC given a prefix
  ansible.builtin.debug:
    msg: "{{ '52:54:00' | community.general.random_mac }}"
    # => '52:54:00:ef:1c:03'

- name: With a seed
  ansible.builtin.debug:
    msg: "{{ '52:54:00' | community.general.random_mac(seed=inventory_hostname) }}"
'''

RETURN = '''
  _value:
    description: The generated MAC.
    type: string
'''

import re
from random import Random, SystemRandom

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types


def random_mac(value, seed=None):
    ''' takes string prefix, and return it completed with random bytes
        to get a complete 6 bytes MAC address '''

    if not isinstance(value, string_types):
        raise AnsibleFilterError('Invalid value type (%s) for random_mac (%s)' %
                                 (type(value), value))

    value = value.lower()
    mac_items = value.split(':')

    if len(mac_items) > 5:
        raise AnsibleFilterError('Invalid value (%s) for random_mac: 5 colon(:) separated'
                                 ' items max' % value)

    err = ""
    for mac in mac_items:
        if not mac:
            err += ",empty item"
            continue
        if not re.match('[a-f0-9]{2}', mac):
            err += ",%s not hexa byte" % mac
    err = err.strip(',')

    if err:
        raise AnsibleFilterError('Invalid value (%s) for random_mac: %s' % (value, err))

    if seed is None:
        r = SystemRandom()
    else:
        r = Random(seed)
    # Generate random int between x1000000000 and xFFFFFFFFFF
    v = r.randint(68719476736, 1099511627775)
    # Select first n chars to complement input prefix
    remain = 2 * (6 - len(mac_items))
    rnd = ('%x' % v)[:remain]
    return value + re.sub(r'(..)', r':\1', rnd)


class FilterModule:
    ''' Ansible jinja2 filters '''
    def filters(self):
        return {
            'random_mac': random_mac,
        }
