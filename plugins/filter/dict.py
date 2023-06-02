# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
  name: dict
  short_description: Convert a list of tuples into a dictionary
  version_added: 3.0.0
  author: Felix Fontein (@felixfontein)
  description:
    - Convert a list of tuples into a dictionary. This is a filter version of the C(dict) function.
  options:
    _input:
      description: A list of tuples (with exactly two elements).
      type: list
      elements: tuple
      required: true
'''

EXAMPLES = '''
- name: Convert list of tuples into dictionary
  ansible.builtin.set_fact:
    dictionary: "{{ [[1, 2], ['a', 'b']] | community.general.dict }}"
    # Result is {1: 2, 'a': 'b'}

- name: Create a list of dictionaries with map and the community.general.dict filter
  ansible.builtin.debug:
    msg: >-
      {{ values | map('zip', ['k1', 'k2', 'k3'])
                | map('map', 'reverse')
                | map('community.general.dict') }}
  vars:
    values:
      - - foo
        - 23
        - a
      - - bar
        - 42
        - b
  # Produces the following list of dictionaries:
  #   {
  #     "k1": "foo",
  #     "k2": 23,
  #     "k3": "a"
  #   },
  #   {
  #     "k1": "bar",
  #     "k2": 42,
  #     "k3": "b"
  #   }
'''

RETURN = '''
  _value:
    description: The dictionary having the provided key-value pairs.
    type: boolean
'''


def dict_filter(sequence):
    '''Convert a list of tuples to a dictionary.

    Example: ``[[1, 2], ['a', 'b']] | community.general.dict`` results in ``{1: 2, 'a': 'b'}``
    '''
    return dict(sequence)


class FilterModule(object):
    '''Ansible jinja2 filters'''

    def filters(self):
        return {
            'dict': dict_filter,
        }
