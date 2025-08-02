#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: pacemaker_info
short_description: Gather information about Pacemaker cluster
author:
  - Dexter Le (@munchtoast)
version_added: 11.2.0
description:
  - Gather information about a Pacemaker cluster.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
"""

EXAMPLES = r"""
- name: Gather Pacemaker cluster info
  community.general.pacemaker_info:
  register: result

- name: Debug cluster info
  ansible.builtin.debug:
    msg: "{{ result }}"
"""

RETURN = r"""
version:
  description: Pacemaker CLI version
  returned: always
  type: str
cluster_info:
  description: Cluster information such as the name, UUID, and nodes.
  returned: always
  type: dict
resource_info:
  description: All resources available on the cluster and their status.
  returned: success
  type: dict
stonith_info:
  description: All STONITH information on the cluster.
  returned: success
  type: dict
constraint_info:
  description: All cluster resource constraints on the cluster.
  returned: success
  type: dict
property_info:
  description: All properties present on the cluster.
  returned: success
  type: dict
"""

import json

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.pacemaker import pacemaker_runner


class PacemakerInfo(ModuleHelper):
    module = dict(
        argument_spec=dict(),
        supports_check_mode=True,
    )
    info_vars = {
        "cluster_info": "cluster",
        "resource_info": "resource",
        "stonith_info": "stonith",
        "constraint_info": "constraint",
        "property_info": "property"
    }
    output_params = info_vars.keys()

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()

    def _process_command_output(self, cli_action=""):
        def process(rc, out, err):
            if rc != 0:
                self.do_raise('pcs {0} config failed with error (rc={1}): {2}'.format(cli_action, rc, err))
            out = json.loads(out)
            return None if out == "" else out
        return process

    def _get_info(self, cli_action):
        with self.runner("cli_action config output_format", output_process=self._process_command_output(cli_action)) as ctx:
            return ctx.run(cli_action=cli_action, output_format="json")

    def __run__(self):
        for key, cli_action in sorted(self.info_vars.items()):
            self.vars.set(key, self._get_info(cli_action))


def main():
    PacemakerInfo.execute()


if __name__ == '__main__':
    main()
