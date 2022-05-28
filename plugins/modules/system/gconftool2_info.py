#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: gconftool2_info
author:
    - "Alexei Znamensky (@russoz)"
short_description: Retrieve GConf configurations
version_added: 5.1.0
description:
  - This module allows retrieving application preferences from the GConf database, with the help of C(gconftool-2).
options:
  key:
    description:
    - >
      The key name for an element in the GConf database.
    type: str
notes:
  - See man gconftool-2(1) for more details.
seealso:
  - name: gconf repository (archived)
    description: Git repository for the project. It is an archived project, so the repository is read-only.
    link: https://gitlab.gnome.org/Archive/gconf
'''

EXAMPLES = """
- name: Get value for a certain key in the database.
  community.general.gconftool2_info:
    key: /desktop/gnome/background/picture_filename
  register: result
"""

RETURN = '''
  value:
    description:
    - The value of the property.
    returned: success
    type: str
    sample: Monospace 10
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.gconftool2 import gconftool2_runner


class GConftoolInfo(ModuleHelper):
    output_params = ['key']
    module = dict(
        argument_spec=dict(
            key=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = gconftool2_runner(self.module, check_rc=True)

    def process_command_output(self, rc, out, err):
        return out.rstrip()

    def __run__(self):
        with self.runner.context(args_order=["get", "key"], output_process=self.process_command_output) as ctx:
            self.vars.value = ctx.run(get=True)


def main():
    GConftoolInfo.execute()


if __name__ == '__main__':
    main()
