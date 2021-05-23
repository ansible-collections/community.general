#!/usr/bin/python
# Copyright: (c) 2019, Saranya Sridharan
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
module: pids
description: "Retrieves a list of PIDs of given process name in Ansible controller/controlled machines.Returns an empty list if no process in that name exists."
short_description: "Retrieves process IDs list if the process is running otherwise return empty list"
author:
  - Saranya Sridharan (@saranyasridharan)
requirements:
  - psutil(python module)
options:
  name:
    description: The name of the process(es) you want to get PID(s) for.
    type: str
  pattern:
    description: The pattern (regular expression) to match the process(es) you want to get PID(s) for.
    type: str
    version_added: 3.0.0
  ignore_case:
    description: Ignore case in pattern if using the I(pattern) option.
    type: bool
    default: false
    version_added: 3.0.0
'''

EXAMPLES = r'''
# Pass the process name
- name: Getting process IDs of the process
  community.general.pids:
      name: python
  register: pids_of_python

- name: Printing the process IDs obtained
  ansible.builtin.debug:
    msg: "PIDS of python:{{pids_of_python.pids|join(',')}}"

- name: Getting process IDs of processes matching pattern
  community.general.pids:
    pattern: python(2(\.7)?|3(\.6)?)?\s+myapp\.py
  register: myapp_pids
'''

RETURN = '''
pids:
  description: Process IDs of the given process
  returned: list of none, one, or more process IDs
  type: list
  sample: [100,200]
'''

import re
from os.path import basename

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def compare_lower(a, b):
    if a is None or b is None:
        # this could just be "return False" but would lead to surprising behavior if both a and b are None
        return a == b

    return a.lower() == b.lower()


def get_pid(name):
    pids = []

    for proc in psutil.process_iter(attrs=['name', 'cmdline']):
        if compare_lower(proc.info['name'], name) or \
                proc.info['cmdline'] and compare_lower(proc.info['cmdline'][0], name):
            pids.append(proc.pid)

    return pids


def get_matching_command_pids(pattern, ignore_case):
    flags = 0
    if ignore_case:
        flags |= re.I

    regex = re.compile(pattern, flags)
    # See https://psutil.readthedocs.io/en/latest/#find-process-by-name for more information
    return [p.pid for p in psutil.process_iter(["name", "exe", "cmdline"])
            if regex.search(to_native(p.info["name"]))
            or (p.info["exe"] and regex.search(basename(to_native(p.info["exe"]))))
            or (p.info["cmdline"] and regex.search(to_native(' '.join(p.cmdline()))))
            ]


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            pattern=dict(type="str"),
            ignore_case=dict(type="bool", default=False),
        ),
        required_one_of=[
            ('name', 'pattern')
        ],
        mutually_exclusive=[
            ('name', 'pattern')
        ],
        supports_check_mode=True,
    )

    if not HAS_PSUTIL:
        module.fail_json(msg=missing_required_lib('psutil'))

    name = module.params["name"]
    pattern = module.params["pattern"]
    ignore_case = module.params["ignore_case"]

    if name:
        response = dict(pids=get_pid(name))
    else:
        try:
            response = dict(pids=get_matching_command_pids(pattern, ignore_case))
        except re.error as e:
            module.fail_json(msg="'%s' is not a valid regular expression: %s" % (pattern, to_native(e)))

    module.exit_json(**response)


if __name__ == '__main__':
    main()
