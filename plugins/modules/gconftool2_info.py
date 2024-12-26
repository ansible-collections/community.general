#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gconftool2_info
author:
  - "Alexei Znamensky (@russoz)"
short_description: Retrieve GConf configurations
version_added: 5.1.0
description:
  - This module allows retrieving application preferences from the GConf database, with the help of C(gconftool-2).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  key:
    description:
      - The key name for an element in the GConf database.
    type: str
    required: true
seealso:
  - name: C(gconftool-2) command manual page
    description: Manual page for the command.
    link: https://help.gnome.org/admin//system-admin-guide/2.32/gconf-6.html.en
  - name: gconf repository (archived)
    description: Git repository for the project. It is an archived project, so the repository is read-only.
    link: https://gitlab.gnome.org/Archive/gconf
"""

EXAMPLES = r"""
- name: Get value for a certain key in the database.
  community.general.gconftool2_info:
    key: /desktop/gnome/background/picture_filename
  register: result
"""

RETURN = r"""
value:
  description:
    - The value of the property.
  returned: success
  type: str
  sample: Monospace 10
version:
  description: Version of gconftool-2.
  type: str
  returned: always
  sample: "3.2.6"
  version_added: 10.0.0
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.gconftool2 import gconftool2_runner


class GConftoolInfo(ModuleHelper):
    output_params = ['key']
    module = dict(
        argument_spec=dict(
            key=dict(type='str', required=True, no_log=False),
        ),
        supports_check_mode=True,
    )
    use_old_vardict = False

    def __init_module__(self):
        self.runner = gconftool2_runner(self.module, check_rc=True)
        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()

    def __run__(self):
        with self.runner.context(args_order=["state", "key"]) as ctx:
            rc, out, err = ctx.run(state="get")
            self.vars.value = None if err and not out else out.rstrip()


def main():
    GConftoolInfo.execute()


if __name__ == '__main__':
    main()
