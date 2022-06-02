#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: dummy_module
author: "Alexei Znamensky (@russoz)"
short_description: Dummy module for testing DestFileModuleHelper.
description:
  - Dummy module for testing DestFileModuleHelper.
options:
  path:
    description:
      - Absolute path of the file.
    type: path
    required: true
    aliases: [ dest ]
  create:
    description:
      - If set to C(no), the module will fail if the JSON file not exists.
        Else, the JSON file will be created.
    type: bool
    default: false
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: false
  value:
    description:
      - Value to put in the dest file.
    type: str
    required: true
'''

EXAMPLES = ""

RETURN = ""

import os
from ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file import DestFileModuleHelper


class DummyModule(DestFileModuleHelper):

    module = dict(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['dest']),
            allow_creation=dict(type='bool', default=True),
            backup=dict(type='bool', default=True),
            value=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )

    def __write_temp__(self, *args, **kwargs):
        """impement abstract DestFileModuleHelper.__write_temp__"""
        self._tmpfile = self._write_in_tempfile(self.vars[self.var_result_data])

    def __load_result_data__(self):
        """impement abstract DestFileModuleHelper.__load_result_data__"""
        content = ''
        try:
            with open(self.vars.path, 'r') as file:
                content = ''.join(file.readlines())
        except FileNotFoundError:
            pass
        self.vars.set(self.var_result_data, content, diff=True)

    def __run__(self):
        self.vars.set(self.var_result_data, self.vars.value)


def main():
    DummyModule().execute()


if __name__ == '__main__':
    main()
