#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Kenneth D. Evensen <kevensen@redhat.com>
# Copyright (c) 2017, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gconftool2
author:
  - Kenneth D. Evensen (@kevensen)
short_description: Edit GNOME Configurations
description:
  - This module allows for the manipulation of GNOME 2 Configuration via
    gconftool-2.  Please see the gconftool-2(1) man pages for more details.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  key:
    type: str
    description:
    - A GConf preference key is an element in the GConf repository
      that corresponds to an application preference. See man gconftool-2(1).
    required: true
  value:
    type: str
    description:
    - Preference keys typically have simple values such as strings,
      integers, or lists of strings and integers. This is ignored if the state
      is "get". See man gconftool-2(1).
  value_type:
    type: str
    description:
    - The type of value being set. This is ignored if the state is "get".
    choices: [ bool, float, int, string ]
  state:
    type: str
    description:
    - The action to take upon the key/value.
    - State C(get) is deprecated and will be removed in community.general 8.0.0. Please use the module M(community.general.gconftool2_info) instead.
    required: true
    choices: [ absent, get, present ]
  config_source:
    type: str
    description:
    - Specify a configuration source to use rather than the default path.
      See man gconftool-2(1).
  direct:
    description:
    - Access the config database directly, bypassing server.  If direct is
      specified then the config_source must be specified as well.
      See man gconftool-2(1).
    type: bool
    default: false
'''

EXAMPLES = """
- name: Change the widget font to "Serif 12"
  community.general.gconftool2:
    key: "/desktop/gnome/interface/font_name"
    value_type: "string"
    value: "Serif 12"
"""

RETURN = '''
  key:
    description: The key specified in the module parameters
    returned: success
    type: str
    sample: /desktop/gnome/interface/font_name
  value_type:
    description: The type of the value that was changed
    returned: success
    type: str
    sample: string
  value:
    description: The value of the preference key after executing the module
    returned: success
    type: str
    sample: "Serif 12"
...
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.gconftool2 import gconftool2_runner


class GConftool(StateModuleHelper):
    change_params = ('value', )
    diff_params = ('value', )
    output_params = ('key', 'value_type')
    facts_params = ('key', 'value_type')
    facts_name = 'gconftool2'
    module = dict(
        argument_spec=dict(
            key=dict(type='str', required=True, no_log=False),
            value_type=dict(type='str', choices=['bool', 'float', 'int', 'string']),
            value=dict(type='str'),
            state=dict(type='str', required=True, choices=['absent', 'get', 'present']),
            direct=dict(type='bool', default=False),
            config_source=dict(type='str'),
        ),
        required_if=[
            ('state', 'present', ['value', 'value_type']),
            ('state', 'absent', ['value']),
            ('direct', True, ['config_source']),
        ],
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = gconftool2_runner(self.module, check_rc=True)
        if self.vars.state != "get":
            if not self.vars.direct and self.vars.config_source is not None:
                self.module.fail_json(msg='If the "config_source" is specified then "direct" must be "true"')

        self.vars.set('previous_value', self._get(), fact=True)
        self.vars.set('value_type', self.vars.value_type)
        self.vars.set_meta('value', initial_value=self.vars.previous_value)
        self.vars.set('playbook_value', self.vars.value, fact=True)

    def _make_process(self, fail_on_err):
        def process(rc, out, err):
            if err and fail_on_err:
                self.ansible.fail_json(msg='gconftool-2 failed with error: %s' % (str(err)))
            self.vars.value = out.rstrip()
            return self.vars.value
        return process

    def _get(self):
        return self.runner("state key", output_process=self._make_process(False)).run(state="get")

    def state_get(self):
        self.deprecate(
            msg="State 'get' is deprecated. Please use the module community.general.gconftool2_info instead",
            version="8.0.0", collection_name="community.general"
        )

    def state_absent(self):
        with self.runner("state key", output_process=self._make_process(False)) as ctx:
            ctx.run()
        self.vars.set('new_value', None, fact=True)

    def state_present(self):
        with self.runner("direct config_source value_type state key value", output_process=self._make_process(True)) as ctx:
            self.vars.set('new_value', ctx.run(), fact=True)


def main():
    GConftool.execute()


if __name__ == '__main__':
    main()
