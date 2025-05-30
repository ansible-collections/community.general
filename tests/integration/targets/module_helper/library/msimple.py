#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: msimple
author: "Alexei Znamensky (@russoz)"
short_description: Simple module for testing
description:
  - Simple module test description.
options:
  a:
    description: aaaa
    type: int
  b:
    description: bbbb
    type: str
  c:
    description: cccc
    type: str
'''

EXAMPLES = ""

RETURN = ""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.mh.deco import check_mode_skip


class MSimple(ModuleHelper):
    output_params = ('a', 'b', 'c', 'm')
    module = dict(
        argument_spec=dict(
            a=dict(type='int', default=0),
            b=dict(type='str'),
            c=dict(type='str'),
            m=dict(type='str'),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.vars.set('value', None)
        self.vars.set('abc', "abc", diff=True)

    @check_mode_skip
    def process_a3_bc(self):
        if self.vars.a == 3:
            self.vars['b'] = str(self.vars.b) * 3
            self.vars['c'] = str(self.vars.c) * 3

    def __run__(self):
        if self.vars.m:
            self.vars.msg = self.vars.m
        if self.vars.a >= 100:
            raise Exception("a >= 100")
        if self.vars.c == "abc change":
            self.vars['abc'] = "changed abc"
        if self.vars.a == 2:
            self.vars['b'] = str(self.vars.b) * 2
            self.vars['c'] = str(self.vars.c) * 2
        self.process_a3_bc()


def main():
    msimple = MSimple()
    msimple.run()


if __name__ == '__main__':
    main()
