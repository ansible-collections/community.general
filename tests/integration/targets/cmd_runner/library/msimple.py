#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

DOCUMENTATION = '''
module: msimple
author: "Alexei Znamensky (@russoz)"
short_description: Simple module for testing
description:
  - Simple module test description.
options:
  command:
    description: aaa
    type: list
    elements: str
    required: true
  arg_formats:
    description: bbb
    type: dict
    required: true
  arg_order:
    description: ccc
    type: list
    required: true
  arg_values:
    description: ddd
    type: list
    required: true
  aa:
    description: eee
    type: raw
'''

EXAMPLES = ""

RETURN = ""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type="list", elements="str", required=True),
            arg_formats=dict(type="dict", required=True),
            arg_order=dict(type="list", required=True),
            arg_values=dict(type="list", required=True),
            aa=dict(type="raw"),
        ),
    )
    p = module.params

    arg_formats = {}
    for arg, fmt in p['arg_formats'].items():
        func = getattr(sys.modules["ansible_collections.community.general.plugins.module_utils.cmd_runner"], fmt['func'])
        args = fmt.get("args", [])

        arg_formats[arg] = func(*args)

    runner = CmdRunner(module, p['command'], arg_formats=arg_formats)

    with runner.context(p['arg_order']) as ctx:
        result = ctx.run(*p['arg_values'])
    rc, out, err = result

    module.exit_json(rc=rc, out=out, err=err)


if __name__ == '__main__':
    main()
