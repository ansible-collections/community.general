#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

DOCUMENTATION = '''
module: cmd_echo
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
    type: raw
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
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, fmt


def main():
    module = AnsibleModule(
        argument_spec=dict(
            arg_formats=dict(type="dict", default={}),
            arg_order=dict(type="raw", required=True),
            arg_values=dict(type="dict", default={}),
            aa=dict(type="raw"),
        ),
    )
    p = module.params

    arg_formats = {}
    for arg, fmt_spec in p['arg_formats'].items():
        func = getattr(fmt, fmt_spec['func'])
        args = fmt_spec.get("args", [])

        arg_formats[arg] = func(*args)

    runner = CmdRunner(module, ['echo', '--'], arg_formats=arg_formats)

    info = None
    with runner.context(p['arg_order']) as ctx:
        result = ctx.run(**p['arg_values'])
        info = ctx.run_info
    rc, out, err = result

    module.exit_json(rc=rc, out=out, err=err, info=info)


if __name__ == '__main__':
    main()
