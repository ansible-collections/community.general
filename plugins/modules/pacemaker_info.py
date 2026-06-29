#!/usr/bin/python

# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: pacemaker_info
short_description: Gather information about Pacemaker cluster
author:
  - Dexter Le (@munchtoast)
version_added: 11.2.0
description:
  - Gather information about a Pacemaker cluster.
requirements:
  - pcs
notes:
  - On C(pcs) >= 0.11.6, the module invokes C(pcs <subcommand> config --output-format=json) and
    returns parsed dictionaries under each C(*_info) key. On older C(pcs) versions that do not
    support JSON output, the raw plaintext C(pcs) output is returned as a string under each
    C(*_info) key instead. Consumers can distinguish shapes at run time with a
    C({{ cluster_info is mapping }}) guard.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
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
  description:
    - Cluster information such as the name, UUID, and nodes.
    - Structured dictionary on C(pcs) >= 0.11.6; raw C(pcs) stdout string on older versions.
  returned: always
  type: raw
resource_info:
  description:
    - All resources available on the cluster and their status.
    - Structured dictionary on C(pcs) >= 0.11.6; raw C(pcs) stdout string on older versions.
  returned: success
  type: raw
stonith_info:
  description:
    - All STONITH information on the cluster.
    - Structured dictionary on C(pcs) >= 0.11.6; raw C(pcs) stdout string on older versions.
  returned: success
  type: raw
constraint_info:
  description:
    - All cluster resource constraints on the cluster.
    - Structured dictionary on C(pcs) >= 0.11.6; raw C(pcs) stdout string on older versions.
  returned: success
  type: raw
property_info:
  description:
    - All properties present on the cluster.
    - Structured dictionary on C(pcs) >= 0.11.6; raw C(pcs) stdout string on older versions.
  returned: success
  type: raw
"""

import json

from ansible_collections.community.general.plugins.module_utils._module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils._pacemaker import pacemaker_runner


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
        "property_info": "property",
    }
    output_params = list(info_vars.keys())

    def __init_module__(self):
        self.runner = pacemaker_runner(self.module)
        self.vars.version = self.runner.raw_version

    def _process_command_output(self, cli_action=""):
        supports_json = self.runner.supports_json

        def process(rc, out, err):
            if rc != 0:
                self.do_raise(f"pcs {cli_action} config failed with error (rc={rc}): {err}")
            if supports_json:
                parsed = json.loads(out) if out else None
                return parsed if parsed else None
            stripped = out.strip() if out else ""
            return stripped or None

        return process

    def _get_info(self, cli_action):
        spec = "cli_action config output_format" if self.runner.supports_json else "cli_action config"
        with self.runner(spec, output_process=self._process_command_output(cli_action)) as ctx:
            return ctx.run(cli_action=cli_action)

    def __run__(self):
        for key, cli_action in sorted(self.info_vars.items()):
            self.vars.set(key, self._get_info(cli_action))


def main():
    PacemakerInfo.execute()


if __name__ == "__main__":
    main()
