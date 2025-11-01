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
  default_groups:
    description:
      - Whether to generate default groups based on remote and project.
    type: bool
    default: true
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
extends_documentation_fragment:
  - ansible.builtin.constructed
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

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.utils.display import Display
from json import loads
from subprocess import check_output

display = Display()


class InventoryModule(BaseInventoryPlugin, Constructable):
    """Host inventory parser for Incus."""

    NAME = "community.general.incus"

    def __init__(self):
        super().__init__()

    def verify_file(self, path):
        valid = False

        if super().verify_file(path):
            if path.endswith(("incus.yaml", "incus.yml")):
                valid = True
            else:
                self.display.vvv('Skipping due to inventory source not ending in "incus.yaml" nor "incus.yml"')

        return valid

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)

        self._read_config_data(path)

        self.populate()

    def populate(self):
        # Create top-level "incus" group if missing.
        default_groups = self.get_option("default_groups")
        if default_groups:
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
            if default_groups:
                self.inventory.add_group(group_remote)
                self.inventory.add_child("incus", group_remote)

            # Get a list of projects.
            projects = []
            if project_name:
                projects = [project_name]
            else:
                projects = [entry["name"] for entry in self._run_incus("project", "list", f"{remote_name}:")]

            # Get a list of instances.
            for project in projects:
                # Create the project-specific group if missing.
                group_project = f"{group_remote}_{project}"
                if default_groups:
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

                    # Add some extra variables.
                    host_vars = {}
                    host_vars["ansible_incus_remote"] = remote_name
                    host_vars["ansible_incus_project"] = project

                    for prop in (
                        "architecture",
                        "config",
                        "description",
                        "devices",
                        "ephemeral",
                        "expanded_config",
                        "expanded_devices",
                        "location",
                        "profiles",
                        "status",
                        "type",
                    ):
                        host_vars[f"ansible_incus_{prop}"] = instance[prop]

                    # Add the host to the inventory and constructed groups.
                    self._add_host(host_name, host_vars)

                    # Add the host to the built-in groups.
                    if default_groups:
                        self.inventory.add_host(host_name, group_project)

    def _add_host(self, hostname, host_vars):
        self.inventory.add_host(hostname, group="all")

        for var_name, var_value in host_vars.items():
            self.inventory.set_variable(hostname, var_name, var_value)

        strict = self.get_option("strict")

        # Add variables created by the user's Jinja2 expressions to the host
        self._set_composite_vars(self.get_option("compose"), host_vars, hostname, strict=True)

        # Create user-defined groups using variables and Jinja2 conditionals
        self._add_host_to_composed_groups(self.get_option("groups"), host_vars, hostname, strict=strict)
        self._add_host_to_keyed_groups(self.get_option("keyed_groups"), host_vars, hostname, strict=strict)

    def _run_incus(self, *args):
        local_cmd = ["incus"] + list(args) + ["--format=json"]
        stdout = check_output(local_cmd)
        return loads(stdout)
