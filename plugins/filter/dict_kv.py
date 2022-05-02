# -*- coding: utf-8 -*-
# Copyright (C) 2020 Stanislav German-Evtushenko (@giner) <ginermail@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: dict_kv
  short_description: Convert a value to a dictionary with a single key-value pair
  version_added: 1.3.0
  author: Stanislav German-Evtushenko (@giner)
  description:
    - Convert a value to a dictionary with a single key-value pair.
  positional: key
  options:
    _input:
      description: The value for the single key-value pair.
      type: any
      required: true
    key:
      description: The key for the single key-value pair.
      type: any
      required: true
'''

EXAMPLES = '''
- name: Create a one-element dictionary from a value
  ansible.builtin.debug:
    msg: "{{ 'myvalue' | dict_kv('mykey') }}"
    # Produces the dictionary {'mykey': 'myvalue'}
'''

RETURN = '''
  _value:
    description: A dictionary with a single key-value pair.
    type: dictionary
'''


def dict_kv(value, key):
    '''Return a dictionary with a single key-value pair

    Example:

        - hosts: localhost
          gather_facts: false
          vars:
            myvar: myvalue
          tasks:
          - debug:
              msg: "{{ myvar | dict_kv('thatsmyvar') }}"

        produces:

        ok: [localhost] => {
            "msg": {
                "thatsmyvar": "myvalue"
            }
        }

    Example 2:

        - hosts: localhost
          gather_facts: false
          vars:
            common_config:
              type: host
              database: all
            myservers:
            - server1
            - server2
          tasks:
          - debug:
              msg: "{{ myservers | map('dict_kv', 'server') | map('combine', common_config) }}"

        produces:

        ok: [localhost] => {
            "msg": [
                {
                    "database": "all",
                    "server": "server1",
                    "type": "host"
                },
                {
                    "database": "all",
                    "server": "server2",
                    "type": "host"
                }
            ]
        }
    '''
    return {key: value}


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'dict_kv': dict_kv
        }
