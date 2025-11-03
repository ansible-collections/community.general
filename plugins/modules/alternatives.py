#!/usr/bin/python

# Copyright (c) 2014, Gabe Mulley <gabe.mulley@gmail.com>
# Copyright (c) 2015, David Wittman <dwittman@gmail.com>
# Copyright (c) 2022, Marius Rieder <marius.rieder@scs.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: alternatives
short_description: Manages alternative programs for common commands
description:
  - Manages symbolic links using the C(update-alternatives) tool.
  - Useful when multiple programs are installed but provide similar functionality (for example, different editors).
author:
  - Marius Rieder (@jiuka)
  - David Wittman (@DavidWittman)
  - Gabe Mulley (@mulby)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  name:
    description:
      - The generic name of the link.
    type: str
    required: true
  path:
    description:
      - The path to the real executable that the link should point to.
    type: path
  family:
    description:
      - The family groups similar alternatives. This option is available only on RHEL-based distributions.
    type: str
    version_added: 10.1.0
  link:
    description:
      - The path to the symbolic link that should point to the real executable.
      - This option is always required on RHEL-based distributions. On Debian-based distributions this option is required
        when the alternative O(name) is unknown to the system.
    type: path
  priority:
    description:
      - The priority of the alternative. If no priority is given for creation V(50) is used as a fallback.
    type: int
  state:
    description:
      - V(present) - install the alternative (if not already installed), but do not set it as the currently selected alternative
        for the group.
      - V(selected) - install the alternative (if not already installed), and set it as the currently selected alternative
        for the group.
      - V(auto) - install the alternative (if not already installed), and set the group to auto mode. Added in community.general
        5.1.0.
      - V(absent) - removes the alternative. Added in community.general 5.1.0.
    choices: [present, selected, auto, absent]
    default: selected
    type: str
    version_added: 4.8.0
  subcommands:
    description:
      - A list of subcommands.
      - Each subcommand needs a name, a link and a path parameter.
      - Subcommands are also named C(slaves) or C(followers), depending on the version of C(alternatives).
    type: list
    elements: dict
    aliases: ['slaves']
    suboptions:
      name:
        description:
          - The generic name of the subcommand.
        type: str
        required: true
      path:
        description:
          - The path to the real executable that the subcommand should point to.
        type: path
        required: true
      link:
        description:
          - The path to the symbolic link that should point to the real subcommand executable.
        type: path
        required: true
    version_added: 5.1.0
requirements: [update-alternatives]
"""

EXAMPLES = r"""
- name: Correct java version selected
  community.general.alternatives:
    name: java
    path: /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java

- name: Select java-11-openjdk.x86_64 family
  community.general.alternatives:
    name: java
    family: java-11-openjdk.x86_64
  when: ansible_os_family == 'RedHat'

- name: Alternatives link created
  community.general.alternatives:
    name: hadoop-conf
    link: /etc/hadoop/conf
    path: /etc/hadoop/conf.ansible

- name: Make java 32 bit an alternative with low priority
  community.general.alternatives:
    name: java
    path: /usr/lib/jvm/java-7-openjdk-i386/jre/bin/java
    priority: -10

- name: Install Python 3.5 but do not select it
  community.general.alternatives:
    name: python
    path: /usr/bin/python3.5
    link: /usr/bin/python
    state: present

- name: Install Python 3.5 and reset selection to auto
  community.general.alternatives:
    name: python
    path: /usr/bin/python3.5
    link: /usr/bin/python
    state: auto

- name: keytool is a subcommand of java
  community.general.alternatives:
    name: java
    link: /usr/bin/java
    path: /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
    subcommands:
      - name: keytool
        link: /usr/bin/keytool
        path: /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/keytool
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule


class AlternativeState:
    PRESENT = "present"
    SELECTED = "selected"
    ABSENT = "absent"
    AUTO = "auto"

    @classmethod
    def to_list(cls):
        return [cls.PRESENT, cls.SELECTED, cls.ABSENT, cls.AUTO]


class AlternativesModule:
    _UPDATE_ALTERNATIVES = None

    def __init__(self, module):
        self.module = module
        self.result = dict(changed=False, diff=dict(before=dict(), after=dict()))
        self.module.run_command_environ_update = {"LC_ALL": "C"}
        self.messages = []
        self.run()

    @property
    def mode_present(self):
        return self.module.params.get("state") in [
            AlternativeState.PRESENT,
            AlternativeState.SELECTED,
            AlternativeState.AUTO,
        ]

    @property
    def mode_selected(self):
        return self.module.params.get("state") == AlternativeState.SELECTED

    @property
    def mode_auto(self):
        return self.module.params.get("state") == AlternativeState.AUTO

    def run(self):
        self.parse()

        if self.mode_present:
            # Check if we need to (re)install
            subcommands_parameter = self.module.params["subcommands"]
            priority_parameter = self.module.params["priority"]
            if self.path is not None and (
                self.path not in self.current_alternatives
                or (
                    priority_parameter is not None
                    and self.current_alternatives[self.path].get("priority") != priority_parameter
                )
                or (
                    subcommands_parameter is not None
                    and (
                        not all(
                            s in subcommands_parameter for s in self.current_alternatives[self.path].get("subcommands")
                        )
                        or not all(
                            s in self.current_alternatives[self.path].get("subcommands") for s in subcommands_parameter
                        )
                    )
                )
            ):
                self.install()

            # Check if we need to set the preference
            is_same_path = self.path is not None and self.current_path == self.path
            is_same_family = False
            if self.current_path is not None and self.current_path in self.current_alternatives:
                current_alternative = self.current_alternatives[self.current_path]
                is_same_family = current_alternative.get("family") == self.family

            if self.mode_selected and not (is_same_path or is_same_family):
                self.set()

            # Check if we need to reset to auto
            if self.mode_auto and self.current_mode == "manual":
                self.auto()
        else:
            # Check if we need to uninstall
            if self.path in self.current_alternatives:
                self.remove()

        self.result["msg"] = " ".join(self.messages)
        self.module.exit_json(**self.result)

    def install(self):
        if not os.path.exists(self.path):
            self.module.fail_json(msg=f"Specified path {self.path} does not exist")
        if not self.link:
            self.module.fail_json(
                msg="Needed to install the alternative, but unable to do so as we are missing the link"
            )

        cmd = [self.UPDATE_ALTERNATIVES, "--install", self.link, self.name, self.path, str(self.priority)]
        if self.family is not None:
            cmd.extend(["--family", self.family])

        if self.module.params["subcommands"] is not None:
            subcommands = [["--slave", subcmd["link"], subcmd["name"], subcmd["path"]] for subcmd in self.subcommands]
            cmd += [item for sublist in subcommands for item in sublist]

        self.result["changed"] = True
        self.messages.append(f"Install alternative '{self.path}' for '{self.name}'.")

        if not self.module.check_mode:
            self.module.run_command(cmd, check_rc=True)

        if self.module._diff:
            self.result["diff"]["after"] = dict(
                state=AlternativeState.PRESENT,
                path=self.path,
                family=self.family,
                priority=self.priority,
                link=self.link,
            )
            if self.subcommands:
                self.result["diff"]["after"].update(dict(subcommands=self.subcommands))

    def remove(self):
        cmd = [self.UPDATE_ALTERNATIVES, "--remove", self.name, self.path]
        self.result["changed"] = True
        self.messages.append(f"Remove alternative '{self.path}' from '{self.name}'.")

        if not self.module.check_mode:
            self.module.run_command(cmd, check_rc=True)

        if self.module._diff:
            self.result["diff"]["after"] = dict(state=AlternativeState.ABSENT)

    def set(self):
        # Path takes precedence over family as it is more specific
        if self.path is None:
            arg = self.family
        else:
            arg = self.path

        cmd = [self.UPDATE_ALTERNATIVES, "--set", self.name, arg]
        self.result["changed"] = True
        self.messages.append(f"Set alternative '{arg}' for '{self.name}'.")

        if not self.module.check_mode:
            self.module.run_command(cmd, check_rc=True)

        if self.module._diff:
            self.result["diff"]["after"]["state"] = AlternativeState.SELECTED

    def auto(self):
        cmd = [self.UPDATE_ALTERNATIVES, "--auto", self.name]
        self.messages.append(f"Set alternative to auto for '{self.name}'.")
        self.result["changed"] = True

        if not self.module.check_mode:
            self.module.run_command(cmd, check_rc=True)

        if self.module._diff:
            self.result["diff"]["after"]["state"] = AlternativeState.PRESENT

    @property
    def name(self):
        return self.module.params.get("name")

    @property
    def path(self):
        return self.module.params.get("path")

    @property
    def family(self):
        return self.module.params.get("family")

    @property
    def link(self):
        return self.module.params.get("link") or self.current_link

    @property
    def priority(self):
        if self.module.params.get("priority") is not None:
            return self.module.params.get("priority")
        return self.current_alternatives.get(self.path, {}).get("priority", 50)

    @property
    def subcommands(self):
        if self.module.params.get("subcommands") is not None:
            return self.module.params.get("subcommands")
        elif self.path in self.current_alternatives and self.current_alternatives[self.path].get("subcommands"):
            return self.current_alternatives[self.path].get("subcommands")
        return None

    @property
    def UPDATE_ALTERNATIVES(self):
        if self._UPDATE_ALTERNATIVES is None:
            self._UPDATE_ALTERNATIVES = self.module.get_bin_path("update-alternatives", True)
        return self._UPDATE_ALTERNATIVES

    def parse(self):
        self.current_mode = None
        self.current_path = None
        self.current_link = None
        self.current_alternatives = {}

        # Run `update-alternatives --display <name>` to find existing alternatives
        (rc, display_output, dummy) = self.module.run_command([self.UPDATE_ALTERNATIVES, "--display", self.name])

        if rc != 0:
            self.module.debug(f"No current alternative found. '{self.UPDATE_ALTERNATIVES}' exited with {rc}")
            return

        current_mode_regex = re.compile(r"\s-\s(?:status\sis\s)?(\w*)(?:\smode|.)$", re.MULTILINE)
        current_path_regex = re.compile(r"^\s*link currently points to (.*)$", re.MULTILINE)
        current_link_regex = re.compile(r"^\s*link \w+ is (.*)$", re.MULTILINE)
        subcmd_path_link_regex = re.compile(r"^\s*(?:slave|follower) (\S+) is (.*)$", re.MULTILINE)

        alternative_regex = re.compile(
            r"^(\/.*)\s-\s(?:family\s(\S+)\s)?priority\s(\d+)((?:\s+(?:slave|follower).*)*)", re.MULTILINE
        )
        subcmd_regex = re.compile(r"^\s+(?:slave|follower) (.*): (.*)$", re.MULTILINE)

        match = current_mode_regex.search(display_output)
        if not match:
            self.module.debug("No current mode found in output")
            return
        self.current_mode = match.group(1)

        match = current_path_regex.search(display_output)
        if not match:
            self.module.debug("No current path found in output")
        else:
            self.current_path = match.group(1)

        match = current_link_regex.search(display_output)
        if not match:
            self.module.debug("No current link found in output")
        else:
            self.current_link = match.group(1)

        subcmd_path_map = dict(subcmd_path_link_regex.findall(display_output))
        if not subcmd_path_map and self.subcommands:
            subcmd_path_map = {s["name"]: s["link"] for s in self.subcommands}

        for path, family, prio, subcmd in alternative_regex.findall(display_output):
            self.current_alternatives[path] = dict(
                priority=int(prio),
                family=family,
                subcommands=[
                    dict(name=name, path=spath, link=subcmd_path_map.get(name))
                    for name, spath in subcmd_regex.findall(subcmd)
                    if spath != "(null)"
                ],
            )

        if self.module._diff:
            if self.path in self.current_alternatives:
                self.result["diff"]["before"].update(
                    dict(
                        state=AlternativeState.PRESENT,
                        path=self.path,
                        priority=self.current_alternatives[self.path].get("priority"),
                        link=self.current_link,
                    )
                )
                if self.current_alternatives[self.path].get("subcommands"):
                    self.result["diff"]["before"].update(
                        dict(subcommands=self.current_alternatives[self.path].get("subcommands"))
                    )
                if self.current_mode == "manual" and self.current_path != self.path:
                    self.result["diff"]["before"].update(dict(state=AlternativeState.SELECTED))
            else:
                self.result["diff"]["before"].update(dict(state=AlternativeState.ABSENT))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            path=dict(type="path"),
            family=dict(type="str"),
            link=dict(type="path"),
            priority=dict(type="int"),
            state=dict(
                type="str",
                choices=AlternativeState.to_list(),
                default=AlternativeState.SELECTED,
            ),
            subcommands=dict(
                type="list",
                elements="dict",
                aliases=["slaves"],
                options=dict(
                    name=dict(type="str", required=True),
                    path=dict(type="path", required=True),
                    link=dict(type="path", required=True),
                ),
            ),
        ),
        supports_check_mode=True,
        required_one_of=[("path", "family")],
    )

    AlternativesModule(module)


if __name__ == "__main__":
    main()
