#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Joseph Benden <joe@benden.us>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: xfconf
author:
  - "Joseph Benden (@jbenden)"
  - "Alexei Znamensky (@russoz)"
short_description: Edit XFCE4 Configurations
description:
  - This module allows for the manipulation of Xfce 4 Configuration with the help of
    xfconf-query. Please see the xfconf-query(1) man page for more details.
seealso:
  - name: xfconf-query(1) man page
    description: Manual page of the C(xfconf-query) tool at the XFCE documentation site.
    link: 'https://docs.xfce.org/xfce/xfconf/xfconf-query'

  - name: xfconf - Configuration Storage System
    description: XFCE documentation for the Xfconf configuration system.
    link: 'https://docs.xfce.org/xfce/xfconf/start'

extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  channel:
    description:
      - A Xfconf preference channel is a top-level tree key, inside of the
        Xfconf repository that corresponds to the location for which all
        application properties/keys are stored. See man xfconf-query(1).
    required: true
    type: str
  property:
    description:
      - A Xfce preference key is an element in the Xfconf repository
        that corresponds to an application preference. See man xfconf-query(1).
    required: true
    type: str
  value:
    description:
      - Preference properties typically have simple values such as strings,
        integers, or lists of strings and integers. See man xfconf-query(1).
    type: list
    elements: raw
  value_type:
    description:
      - The type of value being set.
      - When providing more than one I(value_type), the length of the list must
        be equal to the length of I(value).
      - If only one I(value_type) is provided, but I(value) contains more than
        on element, that I(value_type) will be applied to all elements of I(value).
      - If the I(property) being set is an array and it can possibly have ony one
        element in the array, then I(force_array=true) must be used to ensure
        that C(xfconf-query) will interpret the value as an array rather than a
        scalar.
      - Support for C(uchar), C(char), C(uint64), and C(int64) has been added in community.general 4.8.0.
    type: list
    elements: str
    choices: [ string, int, double, bool, uint, uchar, char, uint64, int64, float ]
  state:
    type: str
    description:
      - The action to take upon the property/value.
      - The state C(get) has been removed in community.general 5.0.0. Please use the module M(community.general.xfconf_info) instead.
    choices: [ present, absent ]
    default: "present"
  force_array:
    description:
      - Force array even if only one element.
    type: bool
    default: false
    aliases: ['array']
    version_added: 1.0.0
  disable_facts:
    description:
      - The value C(false) is no longer allowed since community.general 4.0.0.
      - This option is deprecated, and will be removed in community.general 8.0.0.
    type: bool
    default: true
    version_added: 2.1.0
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
    force_array: true
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
      - The type of the value that was changed (C(none) for C(reset)
        state). Either a single string value or a list of strings for array
        types.
      - This is a string or a list of strings.
    returned: success
    type: any
    sample: '"int" or ["str", "str", "str"]'
  value:
    description:
      - The value of the preference key after executing the module. Either a
        single string value or a list of strings for array types.
      - This is a string or a list of strings.
    returned: success
    type: any
    sample: '"192" or ["orange", "yellow", "violet"]'
  previous_value:
    description:
      - The value of the preference key before executing the module.
        Either a single string value or a list of strings for array types.
      - This is a string or a list of strings.
    returned: success
    type: any
    sample: '"96" or ["red", "blue", "green"]'
  cmd:
    description:
      - A list with the resulting C(xfconf-query) command executed by the module.
    returned: success
    type: list
    elements: str
    version_added: 5.4.0
    sample:
      - /usr/bin/xfconf-query
      - --channel
      - xfce4-panel
      - --property
      - /plugins/plugin-19/timezone
      - --create
      - --type
      - string
      - --set
      - Pacific/Auckland
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.xfconf import xfconf_runner


class XFConfProperty(StateModuleHelper):
    change_params = ('value', )
    diff_params = ('value', )
    output_params = ('property', 'channel', 'value')
    module = dict(
        argument_spec=dict(
            state=dict(type='str', choices=("present", "absent"), default="present"),
            channel=dict(type='str', required=True),
            property=dict(type='str', required=True),
            value_type=dict(type='list', elements='str',
                            choices=('string', 'int', 'double', 'bool', 'uint', 'uchar', 'char', 'uint64', 'int64', 'float')),
            value=dict(type='list', elements='raw'),
            force_array=dict(type='bool', default=False, aliases=['array']),
            disable_facts=dict(
                type='bool', default=True,
                removed_in_version='8.0.0',
                removed_from_collection='community.general'
            ),
        ),
        required_if=[('state', 'present', ['value', 'value_type'])],
        required_together=[('value', 'value_type')],
        supports_check_mode=True,
    )

    default_state = 'present'

    def __init_module__(self):
        self.runner = xfconf_runner(self.module)
        self.does_not = 'Property "{0}" does not exist on channel "{1}".'.format(self.vars.property,
                                                                                 self.vars.channel)
        self.vars.set('previous_value', self._get())
        self.vars.set('type', self.vars.value_type)
        self.vars.meta('value').set(initial_value=self.vars.previous_value)

        if self.vars.disable_facts is False:
            self.do_raise('Returning results as facts has been removed. Stop using disable_facts=false.')

    def process_command_output(self, rc, out, err):
        if err.rstrip() == self.does_not:
            return None
        if rc or len(err):
            self.do_raise('xfconf-query failed with error (rc={0}): {1}'.format(rc, err))

        result = out.rstrip()
        if "Value is an array with" in result:
            result = result.split("\n")
            result.pop(0)
            result.pop(0)

        return result

    def _get(self):
        with self.runner('channel property', output_process=self.process_command_output) as ctx:
            return ctx.run()

    def state_absent(self):
        with self.runner('channel property reset', check_mode_skip=True) as ctx:
            ctx.run(reset=True)
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd
            if self.verbosity >= 4:
                self.vars.run_info = ctx.run_info
        self.vars.value = None

    def state_present(self):
        # stringify all values - in the CLI they will all be happy strings anyway
        # and by doing this here the rest of the code can be agnostic to it
        self.vars.value = [str(v) for v in self.vars.value]
        value_type = self.vars.value_type

        values_len = len(self.vars.value)
        types_len = len(value_type)

        if types_len == 1:
            # use one single type for the entire list
            value_type = value_type * values_len
        elif types_len != values_len:
            # or complain if lists' lengths are different
            self.do_raise('Number of elements in "value" and "value_type" must be the same')

        # calculates if it is an array
        self.vars.is_array = \
            bool(self.vars.force_array) or \
            isinstance(self.vars.previous_value, list) or \
            values_len > 1

        with self.runner('channel property create force_array values_and_types', check_mode_skip=True) as ctx:
            ctx.run(create=True, force_array=self.vars.is_array, values_and_types=(self.vars.value, value_type))
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd
            if self.verbosity >= 4:
                self.vars.run_info = ctx.run_info

        if not self.vars.is_array:
            self.vars.value = self.vars.value[0]
            self.vars.type = value_type[0]
        else:
            self.vars.type = value_type


def main():
    XFConfProperty.execute()


if __name__ == '__main__':
    main()
