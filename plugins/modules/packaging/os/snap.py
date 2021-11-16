#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Alexei Znamensky (russoz) <russoz@gmail.com>
# Copyright: (c) 2018, Stanislas Lange (angristan) <angristan@pm.me>
# Copyright: (c) 2018, Victor Carceler <vcarceler@iespuigcastellar.xeill.net>

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: snap
short_description: Manages snaps
description:
    - "Manages snaps packages."
options:
    name:
        description:
            - Name of the snaps.
        required: true
        type: list
        elements: str
    state:
        description:
            - Desired state of the package.
        required: false
        default: present
        choices: [ absent, present, enabled, disabled ]
        type: str
    classic:
        description:
            - Confinement policy. The classic confinement allows a snap to have
              the same level of access to the system as "classic" packages,
              like those managed by APT. This option corresponds to the --classic argument.
              This option can only be specified if there is a single snap in the task.
        type: bool
        required: false
        default: no
    channel:
        description:
            - Define which release of a snap is installed and tracked for updates.
              This option can only be specified if there is a single snap in the task.
        type: str
        required: false
        default: stable

author:
    - Victor Carceler (@vcarceler) <vcarceler@iespuigcastellar.xeill.net>
    - Stanislas Lange (@angristan) <angristan@pm.me>
'''

EXAMPLES = '''
# Install "foo" and "bar" snap
- name: Install foo
  community.general.snap:
    name:
      - foo
      - bar

# Remove "foo" snap
- name: Remove foo
  community.general.snap:
    name: foo
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
classic:
    description: Whether or not the snaps were installed with the classic confinement
    type: bool
    returned: When snaps are installed
channel:
    description: The channel the snaps were installed from
    type: str
    returned: When snaps are installed
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

import re

from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdStateModuleHelper, ArgFormat, ModuleHelperException
)


__state_map = dict(
    present='install',
    absent='remove',
    enabled='enable',
    disabled='disable',
    info='info',  # not public
    list='list',  # not public
)


def _state_map(value):
    return [__state_map[value]]


class Snap(CmdStateModuleHelper):
    __disable_re = re.compile(r'(?:\S+\s+){5}(?P<notes>\S+)')
    module = dict(
        argument_spec={
            'name': dict(type='list', elements='str', required=True),
            'state': dict(type='str', default='present',
                          choices=['absent', 'present', 'enabled', 'disabled']),
            'classic': dict(type='bool', default=False),
            'channel': dict(type='str', default='stable'),
        },
        supports_check_mode=True,
    )
    command = "snap"
    command_args_formats = dict(
        actionable_snaps=dict(fmt=lambda v: v),
        state=dict(fmt=_state_map),
        classic=dict(fmt="--classic", style=ArgFormat.BOOLEAN),
        channel=dict(fmt=lambda v: [] if v == 'stable' else ['--channel', '{0}'.format(v)]),
    )
    check_rc = False

    @staticmethod
    def _first_non_zero(a):
        for elem in a:
            if elem != 0:
                return elem

        return 0

    def _run_multiple_commands(self, commands):
        outputs = [(c,) + self.run_command(params=c) for c in commands]
        results = ([], [], [], [])
        for output in outputs:
            for i in range(4):
                results[i].append(output[i])

        return [
            '; '.join([to_native(x) for x in results[0]]),
            self._first_non_zero(results[1]),
            '\n'.join(results[2]),
            '\n'.join(results[3]),
        ]

    def is_snap_installed(self, snap_name):
        return 0 == self.run_command(params=[{'state': 'list'}, {'name': snap_name}])[0]

    def is_snap_enabled(self, snap_name):
        rc, out, err = self.run_command(params=[{'state': 'list'}, {'name': snap_name}])
        if rc != 0:
            return None
        result = out.splitlines()[1]
        match = self.__disable_re.match(result)
        if not match:
            raise ModuleHelperException(msg="Unable to parse 'snap list {0}' output:\n{1}".format(snap_name, out))
        notes = match.group('notes')
        return "disabled" not in notes.split(',')

    def state_present(self):
        self.vars.meta('classic').set(output=True)
        self.vars.meta('channel').set(output=True)
        actionable_snaps = [s for s in self.vars.name if not self.is_snap_installed(s)]
        if not actionable_snaps:
            return
        self.changed = True
        self.vars.snaps_installed = actionable_snaps
        if self.module.check_mode:
            return
        params = ['state', 'classic', 'channel']  # get base cmd parts
        has_one_pkg_params = bool(self.vars.classic) or self.vars.channel != 'stable'
        has_multiple_snaps = len(actionable_snaps) > 1
        if has_one_pkg_params and has_multiple_snaps:
            commands = [params + [{'actionable_snaps': [s]}] for s in actionable_snaps]
        else:
            commands = [params + [{'actionable_snaps': actionable_snaps}]]
        self.vars.cmd, rc, out, err = self._run_multiple_commands(commands)
        if rc == 0:
            return

        classic_snap_pattern = re.compile(r'^error: This revision of snap "(?P<package_name>\w+)"'
                                          r' was published using classic confinement')
        match = classic_snap_pattern.match(err)
        if match:
            err_pkg = match.group('package_name')
            msg = "Couldn't install {name} because it requires classic confinement".format(name=err_pkg)
        else:
            msg = "Ooops! Snap installation failed while executing '{cmd}', please examine logs and " \
                  "error output for more details.".format(cmd=self.vars.cmd)
        raise ModuleHelperException(msg=msg)

    def _generic_state_action(self, actionable_func, actionable_var, params=None):
        actionable_snaps = [s for s in self.vars.name if actionable_func(s)]
        if not actionable_snaps:
            return
        self.changed = True
        self.vars[actionable_var] = actionable_snaps
        if self.module.check_mode:
            return
        if params is None:
            params = ['state']
        commands = [params + [{'actionable_snaps': actionable_snaps}]]
        self.vars.cmd, rc, out, err = self._run_multiple_commands(commands)
        if rc == 0:
            return
        msg = "Ooops! Snap operation failed while executing '{cmd}', please examine logs and " \
              "error output for more details.".format(cmd=self.vars.cmd)
        raise ModuleHelperException(msg=msg)

    def state_absent(self):
        self._generic_state_action(self.is_snap_installed, "snaps_removed", ['classic', 'channel', 'state'])

    def state_enabled(self):
        self._generic_state_action(lambda s: not self.is_snap_enabled(s), "snaps_enabled", ['classic', 'channel', 'state'])

    def state_disabled(self):
        self._generic_state_action(self.is_snap_enabled, "snaps_disabled", ['classic', 'channel', 'state'])


def main():
    snap = Snap()
    snap.run()


if __name__ == '__main__':
    main()
