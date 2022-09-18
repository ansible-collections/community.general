#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022,      DEMATEST Maxime <maxime@indelog.fr>
# Copyright: (c) 2022, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
module: mdestfile
author: "DEMAREST Maxime (@indelog)
short_description: Simple implementation of DestFileModuleHelper for testing
                   purpose.
description: Search if a line is present in a destination file and if not found
             add it to the end.
options:
    value:
        description: Line that to be added to destination if not found.
        type: str
        default: ''
extends_documentation_fragment: community.general.dest_file_module
version_added: 5.3.0
'''

EXAMPLES = ''

RETURN = ''

from ansible_collections.community.general.plugins.module_utils.mh.module_helper import DestFileModuleHelper


class MDestFile(DestFileModuleHelper):
    module = DestFileModuleHelper.with_default_params({
        'argument_spec': {
            'value': {'type': 'str', 'default': ''},
        },
    })

    def __process_data__(self):
        if self.raw_content is not None:
            str_content = self.raw_content.decode('utf-8')
        else:
            str_content = ''
        lines_content = str_content.splitlines()
        self.vars.set('result', lines_content, diff=True, change=True)
        if self.vars['value']:
            if self.vars['value'] not in lines_content:
                lines_content.append(self.vars['value'])
                self.vars.set('result', lines_content)
                self.raw_content = ('\n'.join(lines_content) + '\n').encode('utf-8')


def main():
    mdestfile = MDestFile()
    mdestfile.run()


if __name__ == '__main__':
    main()
