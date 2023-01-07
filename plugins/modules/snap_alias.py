#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Alexei Znamensky (russoz) <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: snap_alias
short_description: Manages snap aliases
version_added: 4.0.0
description:
    - "Manages snaps aliases."
options:
    state:
        description:
            - Desired state of the alias.
        type: str
        choices: [ absent, present ]
        default: present
    name:
        description:
            - Name of the snap.
        type: str
    alias:
        description:
            - Aliases to be created or removed.
        type: list
        elements: str
        aliases: [aliases]

author:
    - Alexei Znamensky (@russoz) <russoz@gmail.com>

seealso:
    - module: community.general.snap
'''

EXAMPLES = '''
# Install "foo" and "bar" snap
- name: Create snap alias
  community.general.snap_alias:
    name: hello-world
    alias: hw

- name: Create multiple aliases
  community.general.snap_alias:
    name: hello-world
    aliases:
      - hw
      - hw2
      - hw3
    state: present   # optional

- name: Remove one specific aliases
  community.general.snap_alias:
    name: hw
    state: absent

- name: Remove all aliases for snap
  community.general.snap_alias:
    name: hello-world
    state: absent
'''

RETURN = '''
snap_aliases:
    description: The snap aliases after execution. If called in check mode, then the list represents the state before execution.
    type: list
    elements: str
    returned: always
'''


import re

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


_state_map = dict(
    present='alias',
    absent='unalias',
    info='aliases',
)


class SnapAlias(StateModuleHelper):
    _RE_ALIAS_LIST = re.compile(r"^(?P<snap>[\w-]+)\s+(?P<alias>[\w-]+)\s+.*$")

    module = dict(
        argument_spec={
            'state': dict(type='str', choices=['absent', 'present'], default='present'),
            'name': dict(type='str'),
            'alias': dict(type='list', elements='str', aliases=['aliases']),
        },
        required_if=[
            ('state', 'present', ['name', 'alias']),
            ('state', 'absent', ['name', 'alias'], True),
        ],
        supports_check_mode=True,
    )

    command_args_formats = {
        "state": cmd_runner_fmt.as_map(_state_map),
        "name": cmd_runner_fmt.as_list(),
        "alias": cmd_runner_fmt.as_list(),
    }

    def _aliases(self):
        n = self.vars.name
        return {n: self._get_aliases_for(n)} if n else self._get_aliases()

    def __init_module__(self):
        self.runner = CmdRunner(self.module, "snap", self.command_args_formats, check_rc=False)
        self.vars.set("snap_aliases", self._aliases(), change=True, diff=True)

    def __quit_module__(self):
        self.vars.snap_aliases = self._aliases()

    def _get_aliases(self):
        def process(rc, out, err):
            if err:
                return {}
            aliases = [self._RE_ALIAS_LIST.match(a.strip()) for a in out.splitlines()[1:]]
            snap_alias_list = [(entry.group("snap"), entry.group("alias")) for entry in aliases]
            results = {}
            for snap, alias in snap_alias_list:
                results[snap] = results.get(snap, []) + [alias]
            return results

        with self.runner("state name", check_rc=True, output_process=process) as ctx:
            return ctx.run(state="info")

    def _get_aliases_for(self, name):
        return self._get_aliases().get(name, [])

    def _has_alias(self, name=None, alias=None):
        if name:
            if name not in self.vars.snap_aliases:
                return False
            if alias is None:
                return bool(self.vars.snap_aliases[name])
            return alias in self.vars.snap_aliases[name]

        return any(alias in aliases for aliases in self.vars.snap_aliases.values())

    def state_present(self):
        for alias in self.vars.alias:
            if not self._has_alias(self.vars.name, alias):
                # self.changed = True
                with self.runner("state name alias", check_mode_skip=True) as ctx:
                    ctx.run()
                    if self.verbosity >= 4:
                        self.vars.run_info = ctx.run_info

    def state_absent(self):
        if not self.vars.alias:
            if self._has_alias(self.vars.name):
                # self.changed = True
                with self.runner("state name", check_mode_skip=True) as ctx:
                    ctx.run()
                    if self.verbosity >= 4:
                        self.vars.run_info = ctx.run_info
        else:
            for alias in self.vars.alias:
                if self._has_alias(self.vars.name, alias):
                    # self.changed = True
                    with self.runner("state alias", check_mode_skip=True) as ctx:
                        ctx.run()
                        if self.verbosity >= 4:
                            self.vars.run_info = ctx.run_info


def main():
    SnapAlias.execute()


if __name__ == '__main__':
    main()
