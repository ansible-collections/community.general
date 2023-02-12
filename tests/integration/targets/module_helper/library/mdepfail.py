#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: mdepfail
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
from ansible.module_utils.basic import missing_required_lib

with ModuleHelper.dependency("nopackagewiththisname", missing_required_lib("nopackagewiththisname")):
    import nopackagewiththisname  # noqa: F401, pylint: disable=unused-import


class MSimple(ModuleHelper):
    output_params = ('a', 'b', 'c')
    module = dict(
        argument_spec=dict(
            a=dict(type='int'),
            b=dict(type='str'),
            c=dict(type='str'),
        ),
    )

    def __init_module__(self):
        self.vars.set('value', None)
        self.vars.set('abc', "abc", diff=True)

    def __run__(self):
        if (0 if self.vars.a is None else self.vars.a) >= 100:
            raise Exception("a >= 100")
        if self.vars.c == "abc change":
            self.vars['abc'] = "changed abc"
        if self.vars.get('a', 0) == 2:
            self.vars['b'] = str(self.vars.b) * 2
            self.vars['c'] = str(self.vars.c) * 2


def main():
    msimple = MSimple()
    msimple.run()


if __name__ == '__main__':
    main()
