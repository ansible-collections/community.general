#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: ansible_galaxy_install
author:
    - "Alexei Znamensky (@russoz)"
short_description: Edit XFCE4 Configurations
description:
  - This module allows for the manipulation of Xfce 4 Configuration via
    xfconf-query.  Please see the xfconf-query(1) man pages for more details.
options:
  type:
    description:
    - The type of installation performed by C(ansible-galaxy).
    type: str
    choices: [collection, role]
    default: collection
'''

EXAMPLES = """
- name: Change the DPI to "192"
  xfconf:
    channel: "xsettings"
    property: "/Xft/DPI"
    value_type: "int"
    value: "192"

- name: Set workspace names (4)
  xfconf:
    channel: xfwm4
    property: /general/workspace_names
    value_type: string
    value: ['Main', 'Work1', 'Work2', 'Tmp']

- name: Set workspace names (1)
  xfconf:
    channel: xfwm4
    property: /general/workspace_names
    value_type: string
    value: ['Main']
    force_array: yes
"""

RETURN = '''
  channel:
    description: The channel specified in the module parameters
    returned: success
    type: str
    sample: "xsettings"
  property:
    description: The property specified in the module parameters
    returned: success
    type: str
    sample: "/Xft/DPI"
  value_type:
    description:
    - The type of the value that was changed (C(none) for C(get) and C(reset)
      state). Either a single string value or a list of strings for array
      types.
    returned: success
    type: string or list of strings
    sample: '"int" or ["str", "str", "str"]'
  value:
    description:
    - The value of the preference key after executing the module. Either a
      single string value or a list of strings for array types.
    returned: success
    type: string or list of strings
    sample: '"192" or ["orange", "yellow", "violet"]'
  previous_value:
    description:
    - The value of the preference key before executing the module (C(none) for
      C(get) state). Either a single string value or a list of strings for array
      types.
    returned: success
    type: string or list of strings
    sample: '"96" or ["red", "blue", "green"]'
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdModuleHelper, ArgFormat, ModuleHelperException
)


class AnsibleGalaxyInstall(CmdModuleHelper):
    output_params = ('type', 'name', 'value')
    module = dict(
        argument_spec=dict(
            type=dict(type='str', choices=('collection', 'role'), default='collection'),
            name=dict(type='str'),
            requirements_file=dict(type='path'),
            dest=dict(type='path'),
            force=dict(type='bool', default=False),
        ),
        mutually_exclusive=[('name', 'requirements_file')],
        required_one_of=[('name', 'requirements_file')],
        supports_check_mode=False,
    )

    command = 'ansible-galaxy'
    command_args_formats = dict(
        type=dict(fmt=('{0}', 'install')),
        requirements_file=dict(fmt=('-r', '{0}'),),
        dest=dict(fmt=('-p', '{0}'),),
        force=dict(fmt="--force", style=ArgFormat.BOOLEAN),
    )

    def __run__(self):
        params = ('type', 'force', 'dest', 'requirements_file', 'name')
        self.run_command(params=params)

    def process_command_output(self, rc, out, err):
        if rc != 0:
            raise ModuleHelperException(msg="Unable to install: {0}".format(err))

        if "was installed successfully" in out:
            self.changed = True
        elif "is already installed" in out:
            self.changed = False
        else:
            raise ModuleHelperException(msg="Unknown outcome from ansible-galaxy: {0}".format(err))


def main():
    galaxy = AnsibleGalaxyInstall()
    galaxy.run()


if __name__ == '__main__':
    main()
