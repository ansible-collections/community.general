#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: mstate
author: "Alexei Znamensky (@russoz)"
short_description: State-based module for testing
description:
  - State-based module test description.
options:
  a:
    description: aaaa
    type: int
    required: yes
  b:
    description: bbbb
    type: str
  c:
    description: cccc
    type: str
  trigger_depr_attr:
    description: tries to access VarDict
    type: bool
    default: false
  state:
    description: test states
    type: str
    choices: [join, b_x_a, c_x_a, both_x_a]
    default: join
'''

EXAMPLES = ""

RETURN = ""

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


class MState(StateModuleHelper):
    output_params = ('a', 'b', 'c', 'state')
    module = dict(
        argument_spec=dict(
            a=dict(type='int', required=True),
            b=dict(type='str'),
            c=dict(type='str'),
            trigger_depr_attr=dict(type='bool', default=False),
            state=dict(type='str', choices=['join', 'b_x_a', 'c_x_a', 'both_x_a', 'nop'], default='join'),
        ),
    )

    def __init_module__(self):
        self.vars.set('result', "abc", diff=True)
        if self.vars.trigger_depr_attr:
            dummy = self.VarDict

    def state_join(self):
        self.vars['result'] = "".join([str(self.vars.a), str(self.vars.b), str(self.vars.c)])

    def state_b_x_a(self):
        self.vars['result'] = str(self.vars.b) * self.vars.a

    def state_c_x_a(self):
        self.vars['result'] = str(self.vars.c) * self.vars.a

    def state_both_x_a(self):
        self.vars['result'] = (str(self.vars.b) + str(self.vars.c)) * self.vars.a

    def state_nop(self):
        pass


def main():
    mstate = MState()
    mstate.run()


if __name__ == '__main__':
    main()
