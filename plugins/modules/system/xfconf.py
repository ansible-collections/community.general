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
  - This module allows for the manipulation of Xfce 4 Configuration with the help of
    xfconf-query.  Please see the xfconf-query(1) man pages for more details.
seealso:
  - name: C(xfconf-query) man page
    description: Manual page of the C(xfconf-query) tool at the XFCE documentation site.
    link: 'https://docs.xfce.org/xfce/xfconf/xfconf-query'

  - name: xfconf - Configuration Storage System
    description: XFCE documentation for the Xfconf configuration system.
    link: 'https://docs.xfce.org/xfce/xfconf/start'

options:
  channel:
    description:
      - A Xfconf preference channel is a top-level tree key, inside of the
        Xfconf repository that corresponds to the location for which all
        application properties/keys are stored. See man xfconf-query(1)
    required: true
    type: str
  property:
    description:
      - A Xfce preference key is an element in the Xfconf repository
        that corresponds to an application preference. See man xfconf-query(1)
    required: true
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
      - State C(get) is deprecated and will be removed in community.general 5.0.0. Please use the module M(community.general.xfconf_info) instead.
    choices: [ get, present, absent ]
    default: "present"
  force_array:
    description:
      - Force array even if only one element
    type: bool
    default: 'no'
    aliases: ['array']
    version_added: 1.0.0
  disable_facts:
    description:
      - The value C(false) is no longer allowed since community.general 4.0.0.
      - This option will be deprecated in a future version, and eventually be removed.
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
      - The type of the value that was changed (C(none) for C(get) and C(reset)
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
      - The value of the preference key before executing the module (C(none) for
        C(get) state). Either a single string value or a list of strings for array
        types.
      - This is a string or a list of strings.
    returned: success
    type: any
    sample: '"96" or ["red", "blue", "green"]'
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdStateModuleHelper, ArgFormat, ModuleHelperException
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
        result.extend(['--type', '{0}'.format(value_type), '--set', '{0}'.format(value)])
    return result


class XFConfException(Exception):
    pass


class XFConfProperty(CmdStateModuleHelper):
    change_params = 'value',
    diff_params = 'value',
    output_params = ('property', 'channel', 'value')
    facts_params = ('property', 'channel', 'value')
    module = dict(
        argument_spec=dict(
            state=dict(type='str', choices=("present", "get", "absent"), default="present"),
            channel=dict(type='str', required=True),
            property=dict(type='str', required=True),
            value_type=dict(type='list', elements='str',
                            choices=('string', 'int', 'double', 'bool', 'uint', 'uchar', 'char', 'uint64', 'int64', 'float')),
            value=dict(type='list', elements='raw'),
            force_array=dict(type='bool', default=False, aliases=['array']),
            disable_facts=dict(type='bool', default=True),
        ),
        required_if=[('state', 'present', ['value', 'value_type'])],
        required_together=[('value', 'value_type')],
        supports_check_mode=True,
    )

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
        self.update_vars(meta={"output": True, "fact": True}, **kwargs)

    def __init_module__(self):
        self.does_not = 'Property "{0}" does not exist on channel "{1}".'.format(self.module.params['property'],
                                                                                 self.module.params['channel'])
        self.vars.set('previous_value', self._get(), fact=True)
        self.vars.set('type', self.vars.value_type, fact=True)
        self.vars.meta('value').set(initial_value=self.vars.previous_value)

        if self.module.params['disable_facts'] is False:
            raise ModuleHelperException('Returning results as facts has been removed. Stop using disable_facts=false.')

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

    def _get(self):
        return self.run_command(params=('channel', 'property'))

    def state_get(self):
        self.vars.value = self.vars.previous_value
        self.vars.previous_value = None
        self.module.deprecate(
            msg="State 'get' is deprecated. Please use the module community.general.xfconf_info instead",
            version="5.0.0", collection_name="community.general"
        )

    def state_absent(self):
        if not self.module.check_mode:
            self.run_command(params=('channel', 'property', {'reset': True}))
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
            raise XFConfException('Number of elements in "value" and "value_type" must be the same')

        # fix boolean values
        self.vars.value = [fix_bool(v[0]) if v[1] == 'bool' else v[0] for v in zip(self.vars.value, value_type)]

        # calculates if it is an array
        self.vars.is_array = \
            bool(self.vars.force_array) or \
            isinstance(self.vars.previous_value, list) or \
            values_len > 1

        params = ['channel', 'property', {'create': True}]
        if self.vars.is_array:
            params.append('is_array')
        params.append({'values_and_types': (self.vars.value, value_type)})

        if not self.module.check_mode:
            self.run_command(params=params)

        if not self.vars.is_array:
            self.vars.value = self.vars.value[0]
            self.vars.type = value_type[0]
        else:
            self.vars.type = value_type


def main():
    XFConfProperty.execute()


if __name__ == '__main__':
    main()
