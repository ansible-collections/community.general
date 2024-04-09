# -*- coding: utf-8 -*-

# Copyright (c) 2023, Steffen Scheib <steffen@scheib.me>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r'''
  name: to_ini
  short_description: Converts a dictionary to the INI file format
  version_added: 8.2.0
  author: Steffen Scheib (@sscheib)
  description:
    - Converts a dictionary to the INI file format.
  options:
    _input:
      description: The dictionary that should be converted to the INI format.
      type: dictionary
      required: true
'''

EXAMPLES = r'''
  - name: Define a dictionary
    ansible.builtin.set_fact:
      my_dict:
        section_name:
          key_name: 'key value'

        another_section:
          connection: 'ssh'

  - name: Write dictionary to INI file
    ansible.builtin.copy:
      dest: /tmp/test.ini
      content: '{{ my_dict | community.general.to_ini }}'

  # /tmp/test.ini will look like this:
  # [section_name]
  # key_name = key value
  #
  # [another_section]
  # connection = ssh
'''

RETURN = r'''
  _value:
    description: A string formatted as INI file.
    type: string
'''


__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six.moves import StringIO
from ansible.module_utils.six.moves.configparser import ConfigParser
from ansible.module_utils.common.text.converters import to_native


class IniParser(ConfigParser):
    ''' Implements a configparser which sets the correct optionxform '''

    def __init__(self):
        super().__init__(interpolation=None)
        self.optionxform = str


def to_ini(obj):
    ''' Read the given dict and return an INI formatted string '''

    if not isinstance(obj, Mapping):
        raise AnsibleFilterError(f'to_ini requires a dict, got {type(obj)}')

    ini_parser = IniParser()

    try:
        ini_parser.read_dict(obj)
    except Exception as ex:
        raise AnsibleFilterError('to_ini failed to parse given dict:'
                                 f'{to_native(ex)}', orig_exc=ex)

    # catching empty dicts
    if obj == dict():
        raise AnsibleFilterError('to_ini received an empty dict. '
                                 'An empty dict cannot be converted.')

    config = StringIO()
    ini_parser.write(config)

    # config.getvalue() returns two \n at the end
    # with the below insanity, we remove the very last character of
    # the resulting string
    return ''.join(config.getvalue().rsplit(config.getvalue()[-1], 1))


class FilterModule(object):
    ''' Query filter '''

    def filters(self):

        return {
            'to_ini': to_ini
        }
