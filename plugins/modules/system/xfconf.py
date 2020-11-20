#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2017, Joseph Benden <joe@benden.us>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: xfconf
author:
    - "Joseph Benden (@jbenden)"
    - "Alexei Znamensky (@russoz)"
short_description: Edit XFCE4 Configurations
description:
  - This module allows for the manipulation of Xfce 4 Configuration via
    xfconf-query.  Please see the xfconf-query(1) man pages for more details.
options:
  channel:
    description:
    - A Xfconf preference channel is a top-level tree key, inside of the
      Xfconf repository that corresponds to the location for which all
      application properties/keys are stored. See man xfconf-query(1)
    required: yes
    type: str
  property:
    description:
    - A Xfce preference key is an element in the Xfconf repository
      that corresponds to an application preference. See man xfconf-query(1)
    required: yes
    type: str
  value:
    description:
    - Preference properties typically have simple values such as strings,
      integers, or lists of strings and integers. This is ignored if the state
      is "get". For array mode, use a list of values. See man xfconf-query(1)
    type: list
    elements: raw
  value_type:
    description:
    - The type of value being set. This is ignored if the state is "get".
      For array mode, use a list of types.
    type: list
    elements: str
    choices: [ int, uint, bool, float, double, string ]
  state:
    type: str
    description:
    - The action to take upon the property/value.
    choices: [ get, present, absent ]
    default: "present"
  force_array:
    description:
    - Force array even if only one element
    type: bool
    default: 'no'
    aliases: ['array']
    version_added: 1.0.0
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
    description: The type of the value that was changed
    returned: success
    type: str
    sample: "int"
  value:
    description: The value of the preference key after executing the module
    returned: success
    type: str
    sample: "192"
  previous_value:
    description: The value of the preference key before executing the module (None for "get" state).
    returned: success
    type: str
    sample: "96"
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ModuleHelper, CmdMixin, StateMixin, ArgFormat
)


def fix_bool(value):
    vl = value.lower()
    return vl if vl in ("true", "false") else value


@ArgFormat.stars_deco(1)
def values_fmt(values, value_types):
    result = []
    for value, value_type in zip(values, value_types):
        if value_type == 'bool':
            value = fix_bool(value)
        result.append('--type')
        result.append('{0}'.format(value_type))
        result.append('--set')
        result.append('{0}'.format(value))
    return result


class XFConfException(Exception):
    pass


class XFConfProperty(CmdMixin, StateMixin, ModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(default="present",
                       choices=("present", "get", "absent"),
                       type='str'),
            channel=dict(required=True, type='str'),
            property=dict(required=True, type='str'),
            value_type=dict(required=False, type='list',
                            elements='str', choices=('int', 'uint', 'bool', 'float', 'double', 'string')),
            value=dict(required=False, type='list', elements='raw'),
            force_array=dict(default=False, type='bool', aliases=['array']),
        ),
        required_if=[('state', 'present', ['value', 'value_type'])],
        required_together=[('value', 'value_type')],
        supports_check_mode=True,
    )

    facts_name = "xfconf"
    default_state = 'present'
    command = 'xfconf-query'
    command_args_formats = dict(
        channel=dict(fmt=('--channel', '{0}'),),
        property=dict(fmt=('--property', '{0}'),),
        is_array=dict(fmt="--force-array", style=ArgFormat.BOOLEAN),
        reset=dict(fmt="--reset", style=ArgFormat.BOOLEAN),
        create=dict(fmt="--create", style=ArgFormat.BOOLEAN),
        values_and_types=dict(fmt=values_fmt)
    )

    def update_xfconf_output(self, **kwargs):
        self.update_output(**kwargs)
        self.update_facts(**kwargs)

    def __init_module__(self):
        self.does_not = 'Property "{0}" does not exist on channel "{1}".'.format(self.module.params['property'],
                                                                                 self.module.params['channel'])
        self.vars.previous_value = self._get()

    def process_command_output(self, rc, out, err):
        if err.rstrip() == self.does_not:
            return None
        if rc or len(err):
            raise XFConfException('xfconf-query failed with error (rc={0}): {1}'.format(rc, err))

        result = out.rstrip()
        if "Value is an array with" in result:
            result = result.split("\n")
            result.pop(0)
            result.pop(0)

        return result

    @property
    def changed(self):
        if self.vars.previous_value is None:
            return self.vars.value is not None
        elif self.vars.value is None:
            return self.vars.previous_value is not None
        else:
            return set(self.vars.previous_value) != set(self.vars.value)

    def _get(self):
        return self.run_command(params=('channel', 'property'))

    def state_get(self):
        self.vars.value = self.vars.previous_value

    def state_absent(self):
        self.vars.value = None
        self.run_command(params=('channel', 'property', 'reset'), extra_params={"reset": True})

    def state_present(self):
        # stringify all values - in the CLI they will all be happy strings anyway
        # and by doing this here the rest of the code can be agnostic to it
        self.vars.value = [str(v) for v in self.module.params['value']]
        value_type = self.module.params['value_type']

        values_len = len(self.vars.value)
        types_len = len(value_type)

        if types_len == 1:
            # use one single type for the entire list
            value_type = value_type * values_len
        elif types_len != values_len:
            # or complain if lists' lengths are different
            raise XFConfException('Number of elements in "value" and "value_type" must be the same')

        # fix boolean values
        self.vars.value = [fix_bool(v[0]) if v[1] == 'bool' else v[0] for v in zip(self.vars.value, value_type)]

        # calculates if it is an array
        self.vars.is_array = \
            bool(self.module.params['force_array']) or \
            isinstance(self.vars.previous_value, list) or \
            values_len > 1

        params = ['channel', 'property', 'create']
        if self.vars.is_array:
            params.append('is_array')
        params.append('values_and_types')

        extra_params = dict(values_and_types=(self.vars.value, value_type))
        extra_params['create'] = True
        extra_params['is_array'] = self.vars.is_array

        if not self.module.check_mode:
            self.run_command(params=params, extra_params=extra_params)

        if not self.vars.is_array:
            self.vars.value = self.vars.value[0]


def main():
    xfconf = XFConfProperty()
    xfconf.run()


if __name__ == '__main__':
    main()
