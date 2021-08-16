#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2021, Alexei Znamensky (russoz) <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: snap_alias
short_description: Manages snap aliases
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
        required: true
    alias:
        description:
            - Aliases to be created or removed.
        type: list
        elements: str
        aliases: aliases

author:
    - Alexei Znamensky (@russoz) <russoz@gmail.com>
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
    aliases: [hw, hw2, hw3]
    state: present   # optional

- name: Remove one specific aliases
  community.general.snap_alias:
    name: hw
    state: absent

- name: Remove all aliases for snap
  community.general.snap_alias:
    name: hello-world
    state: absent

# Install a snap with classic confinement
- name: Install "foo" with option --classic
  community.general.snap:
    name: foo
    classic: yes

# Install a snap with from a specific channel
- name: Install "foo" with option --channel=latest/edge
  community.general.snap:
    name: foo
    channel: latest/edge
'''

RETURN = '''
cmd:
    description: The command that was executed on the host
    type: str
    returned: When changed is true
snaps_installed:
    description: The list of actually installed snaps
    type: list
    returned: When any snaps have been installed
snaps_removed:
    description: The list of actually removed snaps
    type: list
    returned: When any snaps have been removed
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdStateModuleHelper, ModuleHelperException
)


__state_map = dict(
    present='alias',
    absent='unalias',
    info='aliases',
)


def _state_map(value):
    return [__state_map[value]]


class SnapAlias(CmdStateModuleHelper):
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
    )
    command = "snap"
    command_args_formats = dict(
        snap_name={},
        snap_alias={},
        state=dict(fmt=_state_map),
    )

    def _get_aliases(self, name):
        rc, out, err = self.run_command(params=[{'state': 'info'}, {'snap_name': name}])
        if err:
            return []
        aliases = [a.split() for a in out.splitlines()[1:]]
        aliases = [a[1] for a in aliases if a[0] == name]
        return aliases

    def state_present(self):
        for alias in self.vars.alias:
            self.run_command(params=['state', {'snap_name': self.vars.name}, {'snap_alias': alias}])

    def state_absent(self):
        if self.vars.alias is None:
            self.run_command(params=['state', {'snap_name': self.vars.name}])
        elif self.vars.name is None:
            for alias in self.vars.alias:
                self.run_command(params=['state', {'snap_alias': alias}])
        else:
            existing = self._get_aliases(self.vars.name)
            non_existing = set(self.vars.alias) - set(existing)
            if non_existing:
                raise ModuleHelperException(msg="Snap {0} has not the aliases: {1}".format(self.vars.name, ", ".join(non_existing)))
            for alias in self.vars.alias:
                self.run_command(params=['state', {'snap_alias': alias}])


def main():
    SnapAlias().run()


if __name__ == '__main__':
    main()
