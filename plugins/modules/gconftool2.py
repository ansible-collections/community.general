#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Kenneth D. Evensen <kevensen@redhat.com>
# Copyright (c) 2017, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gconftool2
author:
  - Kenneth D. Evensen (@kevensen)
short_description: Edit GNOME Configurations
description:
  - This module allows for the manipulation of GNOME 2 Configuration using C(gconftool-2). Please see the gconftool-2(1) man
    pages for more details.
seealso:
  - name: C(gconftool-2) command manual page
    description: Manual page for the command.
    link: https://help.gnome.org/admin//system-admin-guide/2.32/gconf-6.html.en

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
      - A GConf preference key is an element in the GConf repository that corresponds to an application preference.
    required: true
  value:
    type: str
    description:
      - Preference keys typically have simple values such as strings, integers, or lists of strings and integers. This is
        ignored unless O(state=present).
  value_type:
    type: str
    description:
      - The type of value being set. This is ignored unless O(state=present).
    choices: [bool, float, int, string]
  state:
    type: str
    description:
      - The action to take upon the key/value.
    required: true
    choices: [absent, present]
  config_source:
    type: str
    description:
      - Specify a configuration source to use rather than the default path.
  direct:
    description:
      - Access the config database directly, bypassing server. If O(direct) is specified then the O(config_source) must be
        specified as well.
    type: bool
    default: false
"""

EXAMPLES = r"""
- name: Change the widget font to "Serif 12"
  community.general.gconftool2:
    key: "/desktop/gnome/interface/font_name"
    value_type: "string"
    value: "Serif 12"
"""

RETURN = r"""
key:
  description: The key specified in the module parameters.
  returned: success
  type: str
  sample: /desktop/gnome/interface/font_name
value_type:
  description: The type of the value that was changed.
  returned: success
  type: str
  sample: string
value:
  description:
    - The value of the preference key after executing the module or V(null) if key is removed.
    - From community.general 7.0.0 onwards it returns V(null) for a non-existent O(key), and returned V("") before that.
  returned: success
  type: str
  sample: "Serif 12"
previous_value:
  description:
    - The value of the preference key before executing the module.
    - From community.general 7.0.0 onwards it returns V(null) for a non-existent O(key), and returned V("") before that.
  returned: success
  type: str
  sample: "Serif 12"
version:
  description: Version of gconftool-2.
  type: str
  returned: always
  sample: "3.2.6"
  version_added: 10.0.0
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.gconftool2 import gconftool2_runner


class GConftool(StateModuleHelper):
    diff_params = ('value', )
    output_params = ('key', 'value_type')
    facts_params = ('key', 'value_type')
    facts_name = 'gconftool2'
    module = dict(
        argument_spec=dict(
            key=dict(type='str', required=True, no_log=False),
            value_type=dict(type='str', choices=['bool', 'float', 'int', 'string']),
            value=dict(type='str'),
            state=dict(type='str', required=True, choices=['absent', 'present']),
            direct=dict(type='bool', default=False),
            config_source=dict(type='str'),
        ),
        required_if=[
            ('state', 'present', ['value', 'value_type']),
            ('direct', True, ['config_source']),
        ],
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = gconftool2_runner(self.module, check_rc=True)
        if not self.vars.direct and self.vars.config_source is not None:
            self.do_raise('If the "config_source" is specified then "direct" must be "true"')

        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()

        self.vars.set('previous_value', self._get(), fact=True)
        self.vars.set('value_type', self.vars.value_type)
        self.vars.set('_value', self.vars.previous_value, output=False, change=True)
        self.vars.set_meta('value', initial_value=self.vars.previous_value)
        self.vars.set('playbook_value', self.vars.value, fact=True)

    def _make_process(self, fail_on_err):
        def process(rc, out, err):
            if err and fail_on_err:
                self.do_raise('gconftool-2 failed with error:\n%s' % err.strip())
            out = out.rstrip()
            self.vars.value = None if out == "" else out
            return self.vars.value
        return process

    def _get(self):
        return self.runner("state key", output_process=self._make_process(False)).run(state="get")

    def state_absent(self):
        with self.runner("state key", output_process=self._make_process(False)) as ctx:
            ctx.run()
            self.vars.set('run_info', ctx.run_info, verbosity=4)
        self.vars.set('new_value', None, fact=True)
        self.vars._value = None

    def state_present(self):
        with self.runner("direct config_source value_type state key value", output_process=self._make_process(True)) as ctx:
            ctx.run()
            self.vars.set('run_info', ctx.run_info, verbosity=4)
        self.vars.set('new_value', self._get(), fact=True)
        self.vars._value = self.vars.new_value


def main():
    GConftool.execute()


if __name__ == '__main__':
    main()
