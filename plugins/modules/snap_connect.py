#!/usr/bin/python

# Copyright (c) 2026, Alexei Znamensky (russoz) <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: snap_connect
short_description: Manages snap interface connections
version_added: "12.6.0"
description:
  - Manages connections between snap plugs and slots.
  - Snaps run in a sandbox and need explicit interface connections to access system resources
    or communicate with other snaps.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  state:
    description:
      - Desired state of the connection.
    type: str
    choices: [absent, present]
    default: present
  plug:
    description:
      - The plug endpoint in the format C(<snap>:<plug>).
    type: str
    required: true
  slot:
    description:
      - The slot endpoint in the format C(<snap>:<slot>) or C(:<slot>) for system slots.
      - If not specified, snapd will attempt to find a matching slot automatically.
    type: str
notes:
  - Privileged operations require root privileges.
author:
  - Alexei Znamensky (@russoz) <russoz@gmail.com>
seealso:
  - module: community.general.snap
  - module: community.general.snap_alias
"""

EXAMPLES = r"""
- name: Connect firefox camera plug to system camera slot
  community.general.snap_connect:
    plug: firefox:camera
    slot: ":camera"

- name: Connect snap plug (slot resolved automatically by snapd)
  community.general.snap_connect:
    plug: my-app:network

- name: Disconnect a specific connection
  community.general.snap_connect:
    plug: firefox:camera
    slot: ":camera"
    state: absent
"""

RETURN = r"""
snap_connections:
  description: The list of snap connections after execution.
  type: list
  elements: dict
  returned: always
  contains:
    interface:
      description: The interface name.
      type: str
    plug:
      description: The plug endpoint.
      type: str
    slot:
      description: The slot endpoint.
      type: str
version:
  description: Versions of snap components as reported by C(snap version).
  type: dict
  returned: always
"""

import re

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.snap import get_version, snap_runner


class SnapConnect(StateModuleHelper):
    _RE_CONNECTIONS = re.compile(r"^(?P<interface>\S+)\s+(?P<plug>\S+)\s+(?P<slot>\S+)\s+.*$")

    module = dict(
        argument_spec={
            "state": dict(type="str", choices=["absent", "present"], default="present"),
            "plug": dict(type="str", required=True),
            "slot": dict(type="str"),
        },
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = snap_runner(self.module)
        self.vars.version = get_version(self.runner)
        self.vars.set("snap_connections", self._get_connections(), change=True, diff=True)

    def __quit_module__(self):
        self.vars.snap_connections = self._get_connections()

    def _get_connections(self):
        def process(rc, out, err):
            if rc != 0:
                return []
            connections = []
            for line in out.splitlines()[1:]:
                match = self._RE_CONNECTIONS.match(line.strip())
                if match:
                    connections.append(
                        dict(
                            interface=match.group("interface"),
                            plug=match.group("plug"),
                            slot=match.group("slot"),
                        )
                    )
            return connections

        with self.runner("_connections", output_process=process) as ctx:
            return ctx.run()

    def _is_connected(self):
        plug = self.vars.plug
        slot = self.vars.slot
        return any(
            conn["slot"] != "-" and conn["plug"] == plug and (slot is None or conn["slot"] == slot)
            for conn in self.vars.snap_connections
        )

    def state_present(self):
        if not self._is_connected():
            self.changed = True
            if self.check_mode:
                return
            with self.runner("_connect slot") as ctx:
                rc, dummy, err = ctx.run(_connect=self.vars.plug, slot=self.vars.slot)
            if rc != 0:
                self.do_raise(msg=f"snap connect failed: {err}")

    def state_absent(self):
        if self._is_connected():
            self.changed = True
            if self.check_mode:
                return
            with self.runner("_disconnect slot") as ctx:
                rc, dummy, err = ctx.run(_disconnect=self.vars.plug, slot=self.vars.slot)
            if rc != 0:
                self.do_raise(msg=f"snap disconnect failed: {err}")


def main():
    SnapConnect.execute()


if __name__ == "__main__":
    main()
