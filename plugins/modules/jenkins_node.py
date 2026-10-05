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
  - community.general._attributes
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
  remote_root_dir:
    description:
      - Remote agent root directory (remoteFS).
    type: str
    aliases:
      - remote_fs
    version_added: 13.5.0
  description:
    description:
      - Description of the Jenkins node.
    type: str
    version_added: 13.5.0
  mode:
    description:
      - Controls how Jenkins schedules builds on this node.
      - V(normal) utilizes this node as much as possible.
      - V(exclusive) only builds jobs with label expressions matching this node.
    type: str
    choices:
      - normal
      - exclusive
    version_added: 13.5.0
  launcher:
    description:
      - Launcher method for the Jenkins node.
      - V(ssh) configures the node to be launched by SSH from the controller.
      - V(inbound) (or V(jnlp)) configures an inbound agent connecting to the controller.
      - V(command) configures launching an agent by running a command on the controller.
      - If not specified, defaults to V(ssh) when creating a new node.
    type: str
    choices:
      - ssh
      - inbound
      - jnlp
      - command
    version_added: 13.5.0
  launch_ssh:
    description:
      - When specified, sets the SSH launcher options.
      - If specified without O(launcher), O(launcher) defaults to V(ssh).
    type: dict
    suboptions:
      host:
        description:
          - When specified, sets the SSH host name.
        type: str
      port:
        description:
          - When specified, sets the SSH port number.
        type: int
      credentials_id:
        description:
          - When specified, sets the Jenkins credential used for SSH authentication by its ID.
        type: str
      host_key_verify_none:
        description:
          - When set to V(true), sets the SSH host key non-verifying strategy.
        type: bool
      host_key_verify_known_hosts:
        description:
          - When set to V(true), sets the SSH host key known hosts file verification strategy.
        type: bool
      host_key_verify_provided:
        description:
          - When specified, sets the SSH host key manually provided verification strategy.
        type: dict
        suboptions:
          algorithm:
            description:
              - Key type, for example V(ssh-rsa).
            type: str
            required: true
          key:
            description:
              - Key value.
            type: str
            required: true
      host_key_verify_trusted:
        description:
          - When specified, sets the SSH host key manually trusted verification strategy.
        type: dict
        suboptions:
          allow_initial:
            description:
              - When specified, enables or disables requiring manual verification of the first connected host for this node.
            type: bool
    version_added: 13.5.0
  launch_command:
    description:
      - Command to run on the controller when O(launcher=command).
    type: dict
    suboptions:
      command:
        description:
          - Command to execute on the controller to launch the agent.
        type: str
        required: true
    version_added: 13.5.0
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

- name: Set Jenkins node offline with offline message
  community.general.jenkins_node:
    name: my-node
    state: disabled
    offline_message: >-
      This node is offline for some reason.

- name: Create an agent node with SSH launcher and custom remote root directory
  community.general.jenkins_node:
    name: ssh-worker
    state: present
    remote_root_dir: /home/jenkins/agent
    description: Linux build worker
    mode: exclusive
    launcher: ssh
    launch_ssh:
      host: worker.example.com
      credentials_id: jenkins-ssh-key
      host_key_verify_trusted:
        allow_initial: true

- name: Create an inbound agent node
  community.general.jenkins_node:
    name: inbound-worker
    state: present
    remote_root_dir: /home/jenkins
    launcher: inbound
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

from ansible_collections.community.general.plugins.module_utils import _deps as deps

with deps.declare(
    "python-jenkins",
    reason="python-jenkins is required to interact with Jenkins",
    url="https://opendev.org/jjb/python-jenkins",
):
    import jenkins


def bool_to_text(value: bool) -> str:
    return "true" if value else "false"


class Element:
    def __init__(self, root: et.Element | None) -> None:
        self.root = root

    def get(self, key: str) -> str | None:
        return None if self.root is None else self.root.get(key)

    def set(self, key: str, value: str) -> None:
        if self.root is not None:
            self.root.set(key, value)

    def find(self, path: str) -> et.Element | None:
        return None if self.root is None else self.root.find(path)

    def remove(self, element: et.Element) -> None:
        if self.root is not None:
            self.root.remove(element)

    def append(self, element: et.Element) -> None:
        if self.root is not None:
            self.root.append(element)

    @property
    def class_(self) -> str | None:
        return self.get("class")

    @class_.setter
    def class_(self, value: str) -> None:
        self.set("class", value)


class LauncherElement(Element):
    TAG = "launcher"


class LauncherConfig:
    CLASS = ""

    def init(self) -> et.Element:
        raise NotImplementedError

    def update(self, root: et.Element) -> bool:
        raise NotImplementedError


class SSHHostKeyVerifyElement(Element):
    TAG = "sshHostKeyVerificationStrategy"


class SSHHostKeyVerifyConfig:
    CLASS = ""

    def init(self) -> et.Element:
        root = et.Element(SSHHostKeyVerifyElement.TAG)
        Element(root).class_ = self.CLASS
        return root

    def update(self, root: et.Element) -> bool:
        class_ = Element(root).class_
        if class_ != self.CLASS:
            raise ValueError(f"unexpected class {class_}: expected {self.CLASS}")
        return False


class KnownHostsSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy"


class NoneSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"


class TrustedSSHHostKeyVerifyElement(SSHHostKeyVerifyElement):
    @property
    def allow_initial(self) -> et.Element | None:
        return self.find("requireInitialManualTrust")


class TrustedSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy"

    TEMPLATE = (
        '<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">\n'
        "    <requireInitialManualTrust>false</requireInitialManualTrust>\n"
        "</sshHostKeyVerificationStrategy>"
    )

    def __init__(self, allow_initial: bool | None = None) -> None:
        self.allow_initial = allow_initial

    def init(self) -> et.Element:
        return et.fromstring(self.TEMPLATE)

    def update(self, root: et.Element) -> bool:
        super().update(root)
        wrapper = TrustedSSHHostKeyVerifyElement(root)
        updated = False

        if self.allow_initial is not None:
            if wrapper.allow_initial is None:
                wrapper.append(et.Element("requireInitialManualTrust"))
            if wrapper.allow_initial is not None and wrapper.allow_initial.text != bool_to_text(self.allow_initial):
                wrapper.allow_initial.text = bool_to_text(self.allow_initial)
                updated = True

        return updated


class ProvidedSSHHostKeyVerifyElement(SSHHostKeyVerifyElement):
    class Key(Element):
        TAG = "key"

        @property
        def algorithm(self) -> et.Element | None:
            return self.find("algorithm")

        @property
        def key(self) -> et.Element | None:
            return self.find("key")

    @property
    def key(self) -> ProvidedSSHHostKeyVerifyElement.Key | None:
        root = self.find("key")
        if root is None:
            return None
        return ProvidedSSHHostKeyVerifyElement.Key(root)


class ProvidedSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy"

    TEMPLATE = (
        '<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">\n'
        "    <key>\n"
        "        <algorithm/>\n"
        "        <key/>\n"
        "    </key>\n"
        "</sshHostKeyVerificationStrategy>"
    )

    def __init__(self, algorithm: str, key: str) -> None:
        self.algorithm = algorithm
        self.key = key

    def init(self) -> et.Element:
        return et.fromstring(self.TEMPLATE)

    def update(self, root: et.Element) -> bool:
        super().update(root)
        wrapper = ProvidedSSHHostKeyVerifyElement(root)
        updated = False

        if wrapper.key is not None:
            if wrapper.key.algorithm is not None and wrapper.key.algorithm.text != self.algorithm:
                wrapper.key.algorithm.text = self.algorithm
                updated = True

            if wrapper.key.key is not None and wrapper.key.key.text != self.key:
                wrapper.key.key.text = self.key
                updated = True

        return updated


class SSHLauncherElement(LauncherElement):
    @property
    def host(self) -> et.Element | None:
        return self.find("host")

    @host.setter
    def host(self, element: et.Element) -> None:
        if self.host is not None:
            self.remove(self.host)
        self.append(element)

    def ensure_host(self) -> et.Element:
        if self.host is None:
            return et.SubElement(self.root, "host")
        return self.host

    @property
    def port(self) -> et.Element | None:
        return self.find("port")

    def ensure_port(self) -> et.Element:
        if self.port is None:
            return et.SubElement(self.root, "port")
        return self.port

    @property
    def credentials_id(self) -> et.Element | None:
        return self.find("credentialsId")

    def ensure_credentials_id(self) -> et.Element:
        if self.credentials_id is None:
            return et.SubElement(self.root, "credentialsId")
        return self.credentials_id

    @property
    def host_key_verify(self) -> et.Element | None:
        return self.find(SSHHostKeyVerifyElement.TAG)

    @host_key_verify.setter
    def host_key_verify(self, element: et.Element) -> None:
        if self.host_key_verify is not None:
            self.remove(self.host_key_verify)
        self.append(element)


class SSHLauncherConfig(LauncherConfig):
    CLASS = "hudson.plugins.sshslaves.SSHLauncher"

    TEMPLATE = (
        '<launcher class="hudson.plugins.sshslaves.SSHLauncher">\n'
        "    <port>22</port>\n"
        "    <credentialsId/>\n"
        "    <launchTimeoutSeconds>60</launchTimeoutSeconds>\n"
        "    <maxNumRetries>10</maxNumRetries>\n"
        "    <retryWaitTime>15</retryWaitTime>\n"
        "    <tcpNoDelay>true</tcpNoDelay>\n"
        "</launcher>"
    )

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        credentials_id: str | None = None,
        host_key_verify: SSHHostKeyVerifyConfig | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.credentials_id = credentials_id
        self.host_key_verify = host_key_verify

    def init(self) -> et.Element:
        root = et.fromstring(self.TEMPLATE)
        wrapper = SSHLauncherElement(root)

        if self.host_key_verify is not None:
            wrapper.host_key_verify = self.host_key_verify.init()

        return root

    def update(self, root: et.Element) -> bool:
        wrapper = SSHLauncherElement(root)
        updated = False

        if self.host is not None:
            host_elem = wrapper.ensure_host()
            if host_elem.text != self.host:
                host_elem.text = self.host
                updated = True

        if self.port is not None:
            port_elem = wrapper.ensure_port()
            if port_elem.text != str(self.port):
                port_elem.text = str(self.port)
                updated = True

        if self.credentials_id is not None:
            cred_elem = wrapper.ensure_credentials_id()
            if cred_elem.text != self.credentials_id:
                cred_elem.text = self.credentials_id
                updated = True

        if self.host_key_verify is not None:
            if wrapper.host_key_verify is None or Element(wrapper.host_key_verify).class_ != self.host_key_verify.CLASS:
                wrapper.host_key_verify = self.host_key_verify.init()
                updated = True

            if self.host_key_verify.update(wrapper.host_key_verify):
                updated = True

        return updated


class InboundLauncherConfig(LauncherConfig):
    CLASS = "hudson.slaves.JNLPLauncher"

    TEMPLATE = (
        '<launcher class="hudson.slaves.JNLPLauncher">\n'
        "    <workDirSettings>\n"
        "        <disabled>false</disabled>\n"
        "        <internalDir>remoting</internalDir>\n"
        "        <failIfWorkDirIsMissing>false</failIfWorkDirIsMissing>\n"
        "    </workDirSettings>\n"
        "    <webSocket>false</webSocket>\n"
        "</launcher>"
    )

    def init(self) -> et.Element:
        return et.fromstring(self.TEMPLATE)

    def update(self, root: et.Element) -> bool:
        return False


class CommandLauncherElement(LauncherElement):
    @property
    def agent_command(self) -> et.Element | None:
        return self.find("agentCommand")

    def ensure_agent_command(self) -> et.Element:
        if self.agent_command is None:
            return et.SubElement(self.root, "agentCommand")
        return self.agent_command


class CommandLauncherConfig(LauncherConfig):
    CLASS = "hudson.slaves.CommandLauncher"

    TEMPLATE = '<launcher class="hudson.slaves.CommandLauncher">\n    <agentCommand/>\n</launcher>'

    def __init__(self, command: str | None = None) -> None:
        self.command = command

    def init(self) -> et.Element:
        return et.fromstring(self.TEMPLATE)

    def update(self, root: et.Element) -> bool:
        wrapper = CommandLauncherElement(root)
        updated = False

        if self.command is not None:
            cmd_elem = wrapper.ensure_agent_command()
            if cmd_elem.text != self.command:
                cmd_elem.text = self.command
                updated = True

        return updated


def ssh_host_key_verify_config(args: dict) -> SSHHostKeyVerifyConfig | None:
    if args.get("host_key_verify_none"):
        return NoneSSHHostKeyVerifyConfig()
    if args.get("host_key_verify_known_hosts"):
        return KnownHostsSSHHostKeyVerifyConfig()
    if args.get("host_key_verify_provided"):
        return ProvidedSSHHostKeyVerifyConfig(
            args["host_key_verify_provided"]["algorithm"],
            args["host_key_verify_provided"]["key"],
        )
    if args.get("host_key_verify_trusted"):
        return TrustedSSHHostKeyVerifyConfig(
            allow_initial=args["host_key_verify_trusted"].get("allow_initial"),
        )
    return None


def ssh_launcher_args_config(args: dict) -> SSHLauncherConfig:
    return SSHLauncherConfig(
        host=args.get("host"),
        port=args.get("port"),
        credentials_id=args.get("credentials_id"),
        host_key_verify=ssh_host_key_verify_config(args),
    )


def command_launcher_args_config(args: dict) -> CommandLauncherConfig:
    return CommandLauncherConfig(command=args.get("command"))


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
        self.remote_root_dir: str | None = module.params.get("remote_root_dir")
        self.node_description: str | None = module.params.get("description")
        self.mode: str | None = module.params.get("mode")
        self.launcher_type: str | None = module.params.get("launcher")

        self.launch: LauncherConfig | None = None
        if module.params.get("launch_ssh") or self.launcher_type == "ssh":
            self.launch = ssh_launcher_args_config(module.params.get("launch_ssh") or {})
        elif self.launcher_type in ("inbound", "jnlp"):
            self.launch = InboundLauncherConfig()
        elif self.launcher_type == "command" or module.params.get("launch_command"):
            self.launch = command_launcher_args_config(module.params.get("launch_command") or {})

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

    def configure_launch(self, config: et.Element) -> bool:
        configured = False
        launcher = config.find(LauncherElement.TAG)

        if launcher is None or Element(launcher).class_ != self.launch.CLASS:
            if launcher is not None:
                config.remove(launcher)
            launcher = self.launch.init()
            config.append(launcher)
            configured = True

        if self.launch.update(launcher):
            configured = True

        return configured

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

        if self.launch is not None:
            if self.configure_launch(root):
                configured = True

        if self.remote_root_dir is not None:
            elem = root.find("remoteFS")
            if elem is None:
                elem = et.SubElement(root, "remoteFS")
            if elem.text != self.remote_root_dir:
                elem.text = self.remote_root_dir
                configured = True

        if self.node_description is not None:
            elem = root.find("description")
            if elem is None:
                elem = et.SubElement(root, "description")
            if elem.text != self.node_description:
                elem.text = self.node_description
                configured = True

        if self.mode is not None:
            elem = root.find("mode")
            if elem is None:
                elem = et.SubElement(root, "mode")
            target_mode = self.mode.upper()
            if elem.text != target_mode:
                elem.text = target_mode
                configured = True

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
                launcher = jenkins.LAUNCHER_SSH
                if self.launcher_type in ("inbound", "jnlp"):
                    launcher = jenkins.LAUNCHER_JNLP
                elif self.launcher_type == "command":
                    launcher = jenkins.LAUNCHER_COMMAND

                self.instance.create_node(self.name, launcher=launcher)
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
            remote_root_dir=dict(type="str", aliases=["remote_fs"]),
            description=dict(type="str"),
            mode=dict(type="str", choices=["normal", "exclusive"]),
            launcher=dict(type="str", choices=["ssh", "inbound", "jnlp", "command"]),
            launch_ssh=dict(
                type="dict",
                options=dict(
                    host=dict(type="str"),
                    port=dict(type="int"),
                    credentials_id=dict(type="str"),
                    host_key_verify_none=dict(type="bool"),
                    host_key_verify_known_hosts=dict(type="bool"),
                    host_key_verify_provided=dict(
                        type="dict",
                        options=dict(
                            algorithm=dict(type="str", required=True),
                            key=dict(type="str", required=True, no_log=False),
                        ),
                        no_log=False,
                    ),
                    host_key_verify_trusted=dict(
                        type="dict",
                        options=dict(
                            allow_initial=dict(type="bool"),
                        ),
                        no_log=False,
                    ),
                ),
                mutually_exclusive=[
                    [
                        "host_key_verify_none",
                        "host_key_verify_known_hosts",
                        "host_key_verify_provided",
                        "host_key_verify_trusted",
                    ]
                ],
            ),
            launch_command=dict(
                type="dict",
                options=dict(
                    command=dict(type="str", required=True),
                ),
            ),
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
