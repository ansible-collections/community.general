#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Jose Angel Munoz (@imjoseangel)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
module: docker_stack_info
author: "Jose Angel Munoz (@imjoseangel)"
short_description: Return information on a docker stack
description:
  - Retrieve information on docker stacks using the C(docker stack) command
    on the target node (see examples).
version_added: "1.0.0"
'''

RETURN = '''
results:
    description: |
        dictionary containing the list of stacks or tasks associated
        to a stack name.
    sample: >
        "results": [{"name":"grafana","namespace":"default","orchestrator":"Kubernetes","services":"2"}]
    returned: always
    type: list
'''

EXAMPLES = '''
  - name: Shows stack info
    docker_stack_info:
'''

import ast
import json
from ansible.module_utils.basic import AnsibleModule


def docker_stack_list(module):
    docker_bin = module.get_bin_path('docker', required=True)
    rc, out, err = module.run_command(
        [docker_bin, "stack", "ls", "--format='{{json .}}'"])

    return rc, out.strip(), err.strip()


def main():
    module = AnsibleModule(
        argument_spec={
            'name': dict(type='str', required=False),
            'action': dict(type='str', choices=['list', 'tasks'], default="list"),
        },
        supports_check_mode=False
    )

    rc, out, err = docker_stack_list(module)

    if rc != 0:
        module.fail_json(msg="Error running docker stack module",
                         rc=rc, out=out, stdout=out, stderr=err)
    else:
        if out:
            ret = list(
                json.loads(ast.literal_eval(outitem))
                for outitem in out.split("\n"))

        else:
            ret = []

        module.exit_json(changed=False,
                         msg=out,
                         rc=rc,
                         stdout=out,
                         stderr=err,
                         stack_facts=ret)


if __name__ == "__main__":
    main()
