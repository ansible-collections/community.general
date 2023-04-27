#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Ted Trask <ttrask01@yahoo.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: awall
short_description: Manage awall policies
author: Ted Trask (@tdtrask) <ttrask01@yahoo.com>
description:
  - This modules allows for enable/disable/activate of C(awall) policies.
  - Alpine Wall (I(awall)) generates a firewall configuration from the enabled policy files
    and activates the configuration on the system.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - One or more policy names.
    type: list
    elements: str
  state:
    description:
      - Whether the policies should be enabled or disabled.
    type: str
    choices: [ disabled, enabled ]
    default: enabled
  activate:
    description:
      - Activate the new firewall rules.
      - Can be run with other steps or on its own.
      - Idempotency is affected if I(activate=true), as the module will always report a changed state.
    type: bool
    default: false
notes:
    - At least one of I(name) and I(activate) is required.
'''

EXAMPLES = r'''
- name: Enable "foo" and "bar" policy
  community.general.awall:
    name: [ foo bar ]
    state: enabled

- name: Disable "foo" and "bar" policy and activate new rules
  community.general.awall:
    name:
    - foo
    - bar
    state: disabled
    activate: false

- name: Activate currently enabled firewall rules
  community.general.awall:
    activate: true
'''

RETURN = ''' # '''

import re
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.mh.deco import check_mode_skip


class AWall(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='enabled', choices=['disabled', 'enabled']),
            name=dict(type='list', elements='str'),
            activate=dict(type='bool', default=False),
        ),
        required_one_of=[['name', 'activate']],
        supports_check_mode=True,
    )

    def __init_module__(self):
        state_map = dict(
            enabled="enable",
            disabled="disable",
        )

        self.runner = CmdRunner(
            self.module,
            command="awall",
            arg_formats=dict(
                activate=cmd_runner_fmt.as_fixed(["activate", "--force"]),
                list=cmd_runner_fmt.as_fixed("list"),
                state=cmd_runner_fmt.as_map(state_map),
                name=cmd_runner_fmt.as_list(),
            ),
            required_one_of=[["name", "activate"]],
            check_rc=True,
        )

        self.vars.set("changed_policies", [], output=False, change=True)

    @check_mode_skip
    def activate(self):
        with self.runner("activate") as ctx:
            ctx.run()
        return True

    def is_policy_enabled(self, name):
        def process(rc, out, err):
            return bool(re.search(r"^%s\s+enabled" % name, out, re.MULTILINE))

        with self.runner("list", output_process=process) as ctx:
            return ctx.run()

    def state_enabled(self):
        self.vars.changed_policies = [name
                                      for name in self.vars.names
                                      if not self.is_policy_enabled(name)]

        if not self.vars.changed_policies:
            return

        if self.check_mode:
            with self.runner("list") as ctx:
                ctx.run()
        else:
            with self.runner("state name") as ctx:
                ctx.run(name=self.vars.changed_policies)

    def state_disabled(self):
        self.vars.changed_policies = [name
                                      for name in self.vars.names
                                      if self.is_policy_enabled(name)]

        if not self.vars.changed_policies:
            return

        if self.check_mode:
            with self.runner("list") as ctx:
                ctx.run()
        else:
            with self.runner("state name") as ctx:
                ctx.run(name=self.vars.changed_policies)

    def __state_fallback__(self):
        # if state is not passed
        pass

    def __quit_module__(self):
        if self.vars.activate:
            self.activate()
        if self.vars.changed_policies:
            self.vars.meta("changed_policies", output=True)


def main():
    AWall.execute()


if __name__ == '__main__':
    main()
