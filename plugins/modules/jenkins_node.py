#!/usr/bin/python
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: jenkins_node
short_description: Manage Jenkins nodes
version_added: 10.0.0
description:
  - Manage Jenkins nodes with Jenkins REST API.
requirements:
  - "python-jenkins >= 0.4.12"
author:
  - Connor Newton (@phyrwork)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: partial
    details:
      - Check mode is unable to show configuration changes for a node that is not yet present.
  diff_mode:
    support: none
options:
  url:
    description:
      - URL of the Jenkins server.
    default: http://localhost:8080
    type: str
  name:
    description:
      - Name of the Jenkins node to manage.
    required: true
    type: str
  user:
    description:
      - User to authenticate with the Jenkins server.
    type: str
  token:
    description:
      - API token to authenticate with the Jenkins server.
    type: str
  state:
    description:
      - Specifies whether the Jenkins node should be V(present) (created), V(absent) (deleted), V(enabled) (online) or V(disabled)
        (offline).
    default: present
    choices: ['enabled', 'disabled', 'present', 'absent']
    type: str
  num_executors:
    description:
      - When specified, sets the Jenkins node executor count.
    type: int
  labels:
    description:
      - When specified, sets the Jenkins node labels.
    type: list
    elements: str
  offline_message:
    description:
      - Specifies the offline reason message to be set when configuring the Jenkins node state.
      - If O(offline_message) is given and requested O(state) is not V(disabled), an error is raised.
      - Internally O(offline_message) is set using the V(toggleOffline) API, so updating the message when the node is already
        offline (current state V(disabled)) is not possible. In this case, a warning is issued.
    type: str
    version_added: 10.0.0
"""

EXAMPLES = r"""
- name: Create a Jenkins node using token authentication
  community.general.jenkins_node:
    url: http://localhost:8080
    user: jenkins
    token: 11eb751baabb66c4d1cb8dc4e0fb142cde
    name: my-node
    state: present

- name: Set number of executors on Jenkins node
  community.general.jenkins_node:
    name: my-node
    state: present
    num_executors: 4

- name: Set labels on Jenkins node
  community.general.jenkins_node:
    name: my-node
    state: present
    labels:
      - label-1
      - label-2
      - label-3

- name: Set Jenkins node offline with offline message.
  community.general.jenkins_node:
    name: my-node
    state: disabled
    offline_message: >-
      This node is offline for some reason.
"""

RETURN = r"""
url:
  description: URL used to connect to the Jenkins server.
  returned: success
  type: str
  sample: https://jenkins.mydomain.com
user:
  description: User used for authentication.
  returned: success
  type: str
  sample: jenkins
name:
  description: Name of the Jenkins node.
  returned: success
  type: str
  sample: my-node
state:
  description: State of the Jenkins node.
  returned: success
  type: str
  sample: present
created:
  description: Whether or not the Jenkins node was created by the task.
  returned: success
  type: bool
deleted:
  description: Whether or not the Jenkins node was deleted by the task.
  returned: success
  type: bool
disabled:
  description: Whether or not the Jenkins node was disabled by the task.
  returned: success
  type: bool
enabled:
  description: Whether or not the Jenkins node was enabled by the task.
  returned: success
  type: bool
configured:
  description: Whether or not the Jenkins node was configured by the task.
  returned: success
  type: bool
"""

import traceback
from xml.etree import ElementTree as et

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare(
    "python-jenkins",
    reason="python-jenkins is required to interact with Jenkins",
    url="https://opendev.org/jjb/python-jenkins",
):
    import jenkins


class JenkinsNode:
    def __init__(self, module: AnsibleModule) -> None:
        self.module = module

        self.name = module.params["name"]
        self.state = module.params["state"]
        self.token = module.params["token"]
        self.user = module.params["user"]
        self.url = module.params["url"]
        self.num_executors = module.params["num_executors"]
        self.labels = module.params["labels"]
        self.offline_message: str | None = module.params["offline_message"]

        if self.offline_message is not None:
            self.offline_message = self.offline_message.strip()

            if self.state != "disabled":
                self.module.fail_json("can not set offline message when state is not disabled")

        if self.labels is not None:
            for label in self.labels:
                if " " in label:
                    self.module.fail_json(f"labels must not contain spaces: got invalid label {label}")

        self.instance = self.get_jenkins_instance()
        self.result = {
            "changed": False,
            "url": self.url,
            "user": self.user,
            "name": self.name,
            "state": self.state,
            "created": False,
            "deleted": False,
            "disabled": False,
            "enabled": False,
            "configured": False,
            "warnings": [],
        }

    def get_jenkins_instance(self):
        try:
            if self.user and self.token:
                return jenkins.Jenkins(self.url, self.user, self.token)
            elif self.user and not self.token:
                return jenkins.Jenkins(self.url, self.user)
            else:
                return jenkins.Jenkins(self.url)
        except Exception as e:
            self.module.fail_json(msg=f"Unable to connect to Jenkins server, {e}")

    def configure_node(self, present):
        if not present:
            # Node would only not be present if in check mode and if not present there
            # is no way to know what would and would not be changed.
            if not self.module.check_mode:
                raise Exception("configure_node present is False outside of check mode")
            return

        configured = False

        data = self.instance.get_node_config(self.name)
        root = et.fromstring(data)

        if self.num_executors is not None:
            elem = root.find("numExecutors")
            if elem is None:
                elem = et.SubElement(root, "numExecutors")
            if elem.text is None or int(elem.text) != self.num_executors:
                elem.text = str(self.num_executors)
                configured = True

        if self.labels is not None:
            elem = root.find("label")
            if elem is None:
                elem = et.SubElement(root, "label")
            labels = []
            if elem.text:
                labels = elem.text.split()
            if labels != self.labels:
                elem.text = " ".join(self.labels)
                configured = True

        if configured:
            data = et.tostring(root, encoding="unicode")

            self.instance.reconfig_node(self.name, data)

        self.result["configured"] = configured
        if configured:
            self.result["changed"] = True

    def present_node(self, configure=True):  # type: (bool) -> bool
        """Assert node present.

        Args:
            configure: If True, run node configuration after asserting node present.

        Returns:
            True if the node is present, False otherwise (i.e. is check mode).
        """

        def create_node():
            try:
                self.instance.create_node(self.name, launcher=jenkins.LAUNCHER_SSH)
            except jenkins.JenkinsException as e:
                # Some versions of python-jenkins < 1.8.3 has an authorization bug when
                # handling redirects returned when posting to resources. If the node is
                # created OK then can ignore the error.
                if not self.instance.node_exists(self.name):
                    self.module.fail_json(msg=f"Create node failed: {e}", exception=traceback.format_exc())

                # TODO: Remove authorization workaround.
                self.result["warnings"].append(
                    "suppressed 401 Not Authorized on redirect after node created: see https://review.opendev.org/c/jjb/python-jenkins/+/931707"
                )

        present = self.instance.node_exists(self.name)
        created = False
        if not present:
            if not self.module.check_mode:
                create_node()
                present = True

            created = True

        if configure:
            self.configure_node(present)

        self.result["created"] = created
        if created:
            self.result["changed"] = True

        return present  # Used to gate downstream queries when in check mode.

    def absent_node(self):
        def delete_node():
            try:
                self.instance.delete_node(self.name)
            except jenkins.JenkinsException as e:
                # Some versions of python-jenkins < 1.8.3 has an authorization bug when
                # handling redirects returned when posting to resources. If the node is
                # deleted OK then can ignore the error.
                if self.instance.node_exists(self.name):
                    self.module.fail_json(msg=f"Delete node failed: {e}", exception=traceback.format_exc())

                # TODO: Remove authorization workaround.
                self.result["warnings"].append(
                    "suppressed 401 Not Authorized on redirect after node deleted: see https://review.opendev.org/c/jjb/python-jenkins/+/931707"
                )

        present = self.instance.node_exists(self.name)
        deleted = False
        if present:
            if not self.module.check_mode:
                delete_node()

            deleted = True

        self.result["deleted"] = deleted
        if deleted:
            self.result["changed"] = True

    def enabled_node(self):
        def get_offline():  # type: () -> bool
            return self.instance.get_node_info(self.name)["offline"]

        present = self.present_node()

        enabled = False

        if present:

            def enable_node():
                try:
                    self.instance.enable_node(self.name)
                except jenkins.JenkinsException as e:
                    # Some versions of python-jenkins < 1.8.3 has an authorization bug when
                    # handling redirects returned when posting to resources. If the node is
                    # disabled OK then can ignore the error.
                    offline = get_offline()

                    if offline:
                        self.module.fail_json(msg=f"Enable node failed: {e}", exception=traceback.format_exc())

                    # TODO: Remove authorization workaround.
                    self.result["warnings"].append(
                        "suppressed 401 Not Authorized on redirect after node enabled: see https://review.opendev.org/c/jjb/python-jenkins/+/931707"
                    )

            offline = get_offline()

            if offline:
                if not self.module.check_mode:
                    enable_node()

                enabled = True
        else:
            # Would have created node with initial state enabled therefore would not have
            # needed to enable therefore not enabled.
            if not self.module.check_mode:
                raise Exception("enabled_node present is False outside of check mode")
            enabled = False

        self.result["enabled"] = enabled
        if enabled:
            self.result["changed"] = True

    def disabled_node(self):
        def get_offline_info():
            info = self.instance.get_node_info(self.name)

            offline = info["offline"]
            offline_message = info["offlineCauseReason"]

            return offline, offline_message

        # Don't configure until after disabled, in case the change in configuration
        # causes the node to pick up a job.
        present = self.present_node(False)

        disabled = False
        changed = False

        if present:
            offline, offline_message = get_offline_info()

            if self.offline_message is not None and self.offline_message != offline_message:
                if offline:
                    # n.b. Internally disable_node uses toggleOffline gated by a not
                    # offline condition. This means that disable_node can not be used to
                    # update an offline message if the node is already offline.
                    #
                    # Toggling the node online to set the message when toggling offline
                    # again is not an option as during this transient online time jobs
                    # may be scheduled on the node which is not acceptable.
                    self.result["warnings"].append("unable to change offline message when already offline")
                else:
                    offline_message = self.offline_message
                    changed = True

            def disable_node():
                try:
                    self.instance.disable_node(self.name, offline_message)
                except jenkins.JenkinsException as e:
                    # Some versions of python-jenkins < 1.8.3 has an authorization bug when
                    # handling redirects returned when posting to resources. If the node is
                    # disabled OK then can ignore the error.
                    offline, _offline_message = get_offline_info()

                    if not offline:
                        self.module.fail_json(msg=f"Disable node failed: {e}", exception=traceback.format_exc())

                    # TODO: Remove authorization workaround.
                    self.result["warnings"].append(
                        "suppressed 401 Not Authorized on redirect after node disabled: see https://review.opendev.org/c/jjb/python-jenkins/+/931707"
                    )

            if not offline:
                if not self.module.check_mode:
                    disable_node()

                disabled = True

        else:
            # Would have created node with initial state enabled therefore would have
            # needed to disable therefore disabled.
            if not self.module.check_mode:
                raise Exception("disabled_node present is False outside of check mode")
            disabled = True

        if disabled:
            changed = True

        self.result["disabled"] = disabled

        if changed:
            self.result["changed"] = True

        self.configure_node(present)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type="str"),
            url=dict(default="http://localhost:8080"),
            user=dict(),
            token=dict(no_log=True),
            state=dict(choices=["enabled", "disabled", "present", "absent"], default="present"),
            num_executors=dict(type="int"),
            labels=dict(type="list", elements="str"),
            offline_message=dict(type="str"),
        ),
        supports_check_mode=True,
    )

    deps.validate(module)

    jenkins_node = JenkinsNode(module)

    state = module.params.get("state")
    if state == "enabled":
        jenkins_node.enabled_node()
    elif state == "disabled":
        jenkins_node.disabled_node()
    elif state == "present":
        jenkins_node.present_node()
    else:
        jenkins_node.absent_node()

    module.exit_json(**jenkins_node.result)


if __name__ == "__main__":
    main()
