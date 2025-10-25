# Copyright (c) 2025 Stéphane Graber <stgraber@stgraber.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: incus
short_description: Incus inventory source
version_added: 12.0.0
author:
  - Stéphane Graber (@stgraber)
requirements:
  - Incus CLI (C(incus))
description:
  - Get inventory hosts from the Incus container and virtual-machine manager.
options:
  plugin:
    description:
      - The name of this plugin, it should always be set to community.general.incus for this plugin to work.
    required: true
    choices: ['community.general.incus']
    type: str
  filters:
    description:
      - Filter expression as supported by C(incus list).
    type: list
    elements: string
    default: []
  host_domain:
    description:
      - Domain to append to the host FQDN.
    type: string
  host_fqdn:
    description:
      - Whether to generate a FQDN for the host name.
      - This will use the INSTANCE.PROJECT.REMOTE syntax.
    type: bool
    default: true
  remotes:
    description:
      - The names of the Incus remotes to use (per C(incus remote list)).
      - Remotes are used to access multiple servers from a single client.
      - By default the inventory will go over all projects for each remote.
      - It is possible to specify a specific project using V(remote:project).
    type: list
    elements: string
    default: ["local"]
"""

EXAMPLES = r"""
---
# Pull instances from all projects on the local remote.
plugin: community.general.incus

---
# Pull running VMs from all projects on the local remote.
plugin: community.general.incus
filters:
  - type=virtual-machine
  - status=running

---
# Pull instances from two different remotes
plugin: community.general.incus
remotes:
  - remote-1
  - remote-2

---
# Pull instances from two different remotes
# Limiting the second to the default project
plugin: community.general.incus
remotes:
  - remote-1
  - remote-2:default
"""

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display
from json import loads
from subprocess import check_output

display = Display()


class InventoryModule(BaseInventoryPlugin):
    """Host inventory parser for Incus."""

    NAME = "community.general.incus"

    def __init__(self):
        super(InventoryModule, self).__init__()

    def verify_file(self, path):
        valid = False

        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("incus.yaml", "incus.yml")):
                valid = True
            else:
                self.display.vvv(
                    'Skipping due to inventory source not ending in "incus.yaml" nor "incus.yml"'
                )

        return valid

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)

        self.populate()

    def populate(self):
        # Create top-level "incus" group if missing.
        self.inventory.add_group("incus")

        for remote in self.get_option("remotes"):
            # Split the remote name from the project name (if specified).
            remote_name = ""
            project_name = ""

            fields = remote.split(":", 1)
            if len(fields) == 2:
                remote_name = fields[0]
                project_name = fields[1]
            else:
                remote_name = fields[0]

            # Create the remote-specific group if missing.
            group_remote = f"incus_{remote_name}"
            self.inventory.add_group(group_remote)
            self.inventory.add_child("incus", group_remote)

            # Get a list of projects.
            projects = []
            if project_name:
                projects = [project_name]
            else:
                projects = [
                    entry["name"]
                    for entry in self._run_incus("project", "list", f"{remote_name}:")
                ]

            # Get a list of instances.
            for project in projects:
                # Create the project-specific group if missing.
                group_project = f"{group_remote}_{project}"
                self.inventory.add_group(group_project)
                self.inventory.add_child(group_remote, group_project)

                # List the instances.
                list_cmd = [
                    "list",
                    f"{remote_name}:",
                    "--project",
                    project,
                ] + self.get_option("filters")
                for instance in self._run_incus(*list_cmd):
                    # Compute the host name.
                    host_name = instance["name"]
                    if self.get_option("host_fqdn"):
                        host_name = f"{host_name}.{project}.{remote_name}"

                        domain = self.get_option("host_domain")
                        if domain:
                            host_name = f"{host_name}.{domain}"

                    # Add the host to the inventory.
                    self.inventory.add_host(host_name, group_project)

                    # Add soem extra variables.
                    self.inventory.set_variable(
                        host_name, "ansible_incus_remote", remote_name
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_project", project
                    )

                    self.inventory.set_variable(
                        host_name,
                        "ansible_incus_architecture",
                        instance["architecture"],
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_config", instance["config"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_devices", instance["devices"]
                    )
                    self.inventory.set_variable(
                        host_name,
                        "ansible_incus_expanded_config",
                        instance["expanded_config"],
                    )
                    self.inventory.set_variable(
                        host_name,
                        "ansible_incus_expanded_devices",
                        instance["expanded_devices"],
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_description", instance["description"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_ephemeral", instance["ephemeral"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_location", instance["location"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_profiles", instance["profiles"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_status", instance["status"]
                    )
                    self.inventory.set_variable(
                        host_name, "ansible_incus_type", instance["type"]
                    )

    def _run_incus(self, *args):
        local_cmd = ["incus"] + list(args) + ["--format=json"]
        stdout = check_output(local_cmd)
        return loads(stdout)
