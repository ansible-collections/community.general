#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
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
      - Check mode is unable to show configuration changes for a node that is not yet
        present.
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
      - Specifies whether the Jenkins node should be V(present) (created), V(absent)
        (deleted), V(enabled) (online) or V(disabled) (offline).
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
      - Specifies the offline reason message to be set when configuring the Jenkins node
        state.
      - If O(offline_message) is given and requested O(state) is not V(disabled), an
        error will be raised.
      - Internally O(offline_message) is set via the V(toggleOffline) API, so updating
        the message when the node is already offline (current state V(disabled)) is not
        possible. In this case, a warning will be issued.
    type: str
    version_added: 10.0.0
  launch_ssh:
    description:
      - When specified, sets the Jenkins node to launch by SSH.
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
          - When specified, sets the Jenkins credential used for SSH authentication by
            its ID.
        type: str
      host_key_verify_none:
        description:
          - When set, sets the SSH host key non-verifying strategy.
        type: bool
        choices:
          - true
      host_key_verify_known_hosts:
        description:
          - When set, sets the SSH host key known hosts file verification strategy.
        type: bool
        choices:
          - True
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
              - When specified, enables or disables the requiring manual verification of
                the first connected host for this node.
            type: bool
    version_added: 10.1.0
'''

EXAMPLES = '''
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
    offline_message: >
      This node is offline for some reason.

- name: >
    Set Jenkins node to launch via SSH using stored credential and trust host key on
    initial connection
  community.general.jenkins_node:
    name: my-node
    launch_ssh:
      host: my-node.test
      credentials_id: deaddead-dead-dead-dead-deaddeaddead
      host_key_verify_trusted:
        allow_initial: yes
'''

RETURN = '''
---
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
'''

import sys
import traceback
from abc import abstractmethod
from xml.etree import ElementTree as et

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare(
    "python-jenkins",
    reason="python-jenkins is required to interact with Jenkins",
    url="https://opendev.org/jjb/python-jenkins",
):
    import jenkins


IS_PYTHON_2 = sys.version_info[0] <= 2


if sys.version_info[0] <= 3 or sys.version_info[1] < 8:
    class cached_property(object):  # noqa
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, cls):
            if instance is None:
                return self

            value = self.func(instance)
            setattr(instance, self.func.__name__, value)

            return value
else:
    from functools import cached_property


def bool_to_text(value):  # type: (bool) -> str
    return "true" if value else "false"


def text_to_bool(text):  # type: (str) -> bool
    if text == "true":
        return True

    if text == "false":
        return False

    raise ValueError("unexpected boolean text value '{}'".format(text))


class Element:
    def __init__(self, root):  # type: (et.Element | None) -> None
        self.root = root

    def get(self, key):  # type: (str) -> str | None
        return None if self.root is None else self.root.get(key)

    def set(self, key, value):  # type: (str, str) -> None
        self.root.set(key, value)

    def find(self, path):  # type: (str) -> et.Element | None
        return None if self.root is None else self.root.find(path)

    def remove(self, element):  # type: (et.Element) -> None
        self.root.remove(element)

    def append(self, element):  # type: (et.Element) -> None
        self.root.append(element)

    @property
    def class_(self):  # type: () -> str | None
        return self.get("class")

    @class_.setter
    def class_(self, value):  # (str) -> None
        self.set("class", value)


class Config:
    @abstractmethod
    def init(self):  # type: () -> et.Element
        """Initialize XML element from config.

        Returns:
            Initialized XML element.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, root):  # (et.Element) -> bool
        """Update XML element with config.

        Args:
            root: XML element to update.

        Returns:
            True if was updated, False otherwise.
        """
        raise NotImplementedError


class LauncherElement(Element):
    TAG = "launcher"


class LauncherConfig(Config):
    CLASS = ""


class SSHHostKeyVerifyElement(Element):
    TAG = "sshHostKeyVerificationStrategy"


class SSHHostKeyVerifyConfig(Config):
    CLASS = ""

    def init(self):  # type: () -> et.Element
        root = et.Element(SSHHostKeyVerifyElement.TAG)

        Element(root).class_ = self.CLASS

        return root

    def update(self, root):  # type: (et.Element) -> bool
        class_ = Element(root).class_

        if class_ != self.CLASS:
            raise ValueError("unexpected class {}: expected {}".format(class_, self.CLASS))

        return False


class KnownHostsSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy"


class NoneSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy"


class TrustedSSHHostKeyVerifyElement(SSHHostKeyVerifyElement):
    @property
    def allow_initial(self):  # type: () -> et.Element | None
        return self.find("requireInitialManualTrust")


class TrustedSSHHostKeyVerifyConfig(SSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy"

    TEMPLATE = """
<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">
    <requireInitialManualTrust>false</requireInitialManualTrust>
</sshHostKeyVerificationStrategy>
""".strip()

    def __init__(self, allow_initial=None):  # type: (bool | None) -> None
        self.allow_initial = allow_initial

    def init(self):  # type: () -> et.Element
        return et.fromstring(self.TEMPLATE)

    def update(self, root):  # type: (et.Element) -> bool
        super(TrustedSSHHostKeyVerifyConfig, self).update(root)

        wrapper = TrustedSSHHostKeyVerifyElement(root)
        updated = False

        if self.allow_initial is not None:
            if wrapper.allow_initial.text != bool_to_text(self.allow_initial):
                wrapper.allow_initial.text = bool_to_text(self.allow_initial)
                updated = True

        return updated


class ProvidedSSHHostKeyVerifyElement(SSHHostKeyVerifyElement):
    class Key(Element):
        TAG = "key"

        @property
        def algorithm(self):  # type: () -> et.Element | None
            return self.find("algorithm")

        @property
        def key(self):  # type: () -> et.Element | None
            return self.find("key")

    @property
    def key(self):  # type: () -> ProvidedSSHHostKeyVerifyElement.Key | None
        root = self.find('key')

        if root is None:
            return None

        return ProvidedSSHHostKeyVerifyElement.Key(root)


class ProvidedSSHHostKeyVerifyConfig(KnownHostsSSHHostKeyVerifyConfig):
    CLASS = "hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy"

    TEMPLATE = """
<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
    <key>
        <algorithm/>
        <key/>
    </key>
</sshHostKeyVerificationStrategy>
""".strip()

    def __init__(self, algorithm, key):  # type: (str, str) -> None
        self.algorithm = algorithm
        self.key = key

    def init(self):  # type: () -> et.Element
        return et.fromstring(self.TEMPLATE)

    def update(self, root):  # type: (et.Element) -> bool
        super(ProvidedSSHHostKeyVerifyConfig, self).update(root)

        wrapper = ProvidedSSHHostKeyVerifyElement(root)
        updated = False

        if wrapper.key.algorithm.text != self.algorithm:
            wrapper.key.algorithm.text = self.algorithm
            updated = True

        if wrapper.key.key.text != self.key:
            wrapper.key.key.text = self.key
            updated = True

        return updated


class SSHLauncherElement(LauncherElement):
    @property
    def host(self):  # type: () -> et.Element | None
        return self.find("host")

    @host.setter
    def host(self, element):
        if self.host is not None:
            self.remove(self.host)

        self.append(element)

    def ensure_host(self):
        if self.host is None:
            return et.SubElement(self.root, "host")

        return self.host

    @property
    def port(self):
        return self.find("port")

    @property
    def credentials_id(self):
        return self.find("credentialsId")

    def ensure_credentials_id(self):
        if self.credentials_id is None:
            return et.SubElement(self.root, "credentialsId")

        return self.credentials_id

    @property
    def host_key_verify(self):
        return self.find(SSHHostKeyVerifyElement.TAG)

    @host_key_verify.setter
    def host_key_verify(self, element):
        if self.host_key_verify is not None:
            self.remove(self.host_key_verify)

        self.append(element)


class SSHLauncherConfig(Config):
    CLASS = "hudson.plugins.sshslaves.SSHLauncher"

    def __init__(
        self,
        host=None,
        port=None,
        credentials_id=None,
        host_key_verify=None,
    ):  # type: (str | None, int | None, str | None, SSHHostKeyVerifyConfig | None) -> None
        self.host = host
        self.port = port
        self.credentials_id = credentials_id
        self.host_key_verify = host_key_verify

    TEMPLATE = """
<launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <port>22</port>
    <credentialsId/>
    <launchTimeoutSeconds>60</launchTimeoutSeconds>
    <maxNumRetries>10</maxNumRetries>
    <retryWaitTime>15</retryWaitTime>
    <tcpNoDelay>true</tcpNoDelay>
</launcher>
""".strip()

    def init(self):  # type: () -> et.Element
        root = et.fromstring(self.TEMPLATE)

        wrapper = SSHLauncherElement(root)

        if self.host_key_verify is not None:
            wrapper.host_key_verify = self.host_key_verify.init()

        return root

    def update(self, root):  # type: (et.Element) -> bool
        wrapper = SSHLauncherElement(root)
        updated = False

        if self.host is not None:
            if wrapper.host is None:
                wrapper.ensure_host()
                updated = True

            if wrapper.host.text != self.host:
                wrapper.host.text = self.host
                updated = True

        if self.port is not None:
            if wrapper.port.text != str(self.port):
                wrapper.port.text = str(self.port)
                updated = True

        if self.credentials_id is not None:
            if wrapper.credentials_id is None:
                wrapper.ensure_credentials_id()
                updated = True

            if wrapper.credentials_id.text != self.credentials_id:
                wrapper.credentials_id.text = self.credentials_id
                updated = True

        if self.host_key_verify is not None:
            if Element(wrapper.host_key_verify).class_ != self.host_key_verify.CLASS:
                wrapper.host_key_verify = self.host_key_verify.init()
                updated = True

            if self.host_key_verify.update(wrapper.host_key_verify):
                updated = True

        return updated


def ssh_host_key_verify_config(args):  # type: (dict) -> SSHHostKeyVerifyConfig | None
    """Get SSH host key verify config from args.

    Args:
        args: SSH launcher args.

    Returns:
        SSH host key verify config.
    """
    if args.get("host_key_verify_none"):
        return NoneSSHHostKeyVerifyConfig()

    if args.get('host_key_verify_known_hosts'):
        return KnownHostsSSHHostKeyVerifyConfig()

    if args.get("host_key_verify_provided"):
        return ProvidedSSHHostKeyVerifyConfig(
            args["host_key_verify_provided"]["algorithm"],
            args["host_key_verify_provided"]["key"],
        )

    if args.get("host_key_verify_trusted"):
        return TrustedSSHHostKeyVerifyConfig(
            allow_initial=args["host_key_verify_trusted"].get("allow_initial")
        )

    return None


def ssh_launcher_args_config(args):  # type: (dict) -> SSHLauncherConfig
    return SSHLauncherConfig(
        host=args.get("host"),
        port=args.get("port"),
        credentials_id=args.get("credentials_id"),
        host_key_verify=ssh_host_key_verify_config(args),
    )


class JenkinsNode:
    def __init__(self, module):
        self.module = module

        self.name = module.params['name']
        self.state = module.params['state']
        self.token = module.params['token']
        self.user = module.params['user']
        self.url = module.params['url']
        self.num_executors = module.params['num_executors']
        self.labels = module.params['labels']
        self.offline_message = module.params['offline_message']  # type: str | None

        if self.offline_message is not None:
            self.offline_message = self.offline_message.strip()

            if self.state != "disabled":
                self.module.fail_json("can not set offline message when state is not disabled")

        if self.labels is not None:
            for label in self.labels:
                if " " in label:
                    self.module.fail_json("labels must not contain spaces: got invalid label {}".format(label))

        self.instance = self.get_jenkins_instance()
        self.result = {
            'changed': False,
            'url': self.url,
            'user': self.user,
            'name': self.name,
            'state': self.state,
            'created': False,
            'deleted': False,
            'disabled': False,
            'enabled': False,
            'configured': False,
            'warnings': [],
        }

    @cached_property
    def launch(self):  # type: () -> LauncherConfig | None
        if self.module.params["launch_ssh"]:
            return ssh_launcher_args_config(self.module.params["launch_ssh"])

        return None

    def get_jenkins_instance(self):
        try:
            if self.user and self.token:
                return jenkins.Jenkins(self.url, self.user, self.token)
            elif self.user and not self.token:
                return jenkins.Jenkins(self.url, self.user)
            else:
                return jenkins.Jenkins(self.url)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e))

    def configure_launch(self, config):  # type: (et.Element) -> bool
        configured = False

        launcher = config.find(LauncherElement.TAG)

        if Element(launcher).class_ != self.launch.CLASS:
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

        if self.num_executors is not None:
            elem = root.find('numExecutors')
            if elem is None:
                elem = et.SubElement(root, 'numExecutors')
            if elem.text is None or int(elem.text) != self.num_executors:
                elem.text = str(self.num_executors)
                configured = True

        if self.labels is not None:
            elem = root.find('label')
            if elem is None:
                elem = et.SubElement(root, 'label')
            labels = []
            if elem.text:
                labels = elem.text.split()
            if labels != self.labels:
                elem.text = " ".join(self.labels)
                configured = True

        if configured:
            if IS_PYTHON_2:
                data = et.tostring(root)
            else:
                data = et.tostring(root, encoding="unicode")

            self.instance.reconfig_node(self.name, data)

        self.result['configured'] = configured
        if configured:
            self.result['changed'] = True

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
                    self.module.fail_json(msg="Create node failed: %s" % to_native(e), exception=traceback.format_exc())

                # TODO: Remove authorization workaround.
                self.result['warnings'].append(
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

        self.result['created'] = created
        if created:
            self.result['changed'] = True

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
                    self.module.fail_json(msg="Delete node failed: %s" % to_native(e), exception=traceback.format_exc())

                # TODO: Remove authorization workaround.
                self.result['warnings'].append(
                    "suppressed 401 Not Authorized on redirect after node deleted: see https://review.opendev.org/c/jjb/python-jenkins/+/931707"
                )

        present = self.instance.node_exists(self.name)
        deleted = False
        if present:
            if not self.module.check_mode:
                delete_node()

            deleted = True

        self.result['deleted'] = deleted
        if deleted:
            self.result['changed'] = True

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
                        self.module.fail_json(msg="Enable node failed: %s" % to_native(e), exception=traceback.format_exc())

                    # TODO: Remove authorization workaround.
                    self.result['warnings'].append(
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

        self.result['enabled'] = enabled
        if enabled:
            self.result['changed'] = True

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
                    self.result["warnings"].append(
                        "unable to change offline message when already offline"
                    )
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
                        self.module.fail_json(msg="Disable node failed: %s" % to_native(e), exception=traceback.format_exc())

                    # TODO: Remove authorization workaround.
                    self.result['warnings'].append(
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

        self.result['disabled'] = disabled

        if changed:
            self.result['changed'] = True

        self.configure_node(present)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            url=dict(default='http://localhost:8080'),
            user=dict(),
            token=dict(no_log=True),
            state=dict(choices=['enabled', 'disabled', 'present', 'absent'], default='present'),
            num_executors=dict(type='int'),
            labels=dict(type='list', elements='str'),
            offline_message=dict(type='str'),
            launch_ssh=dict(
                type='dict',
                options=dict(
                    host=dict(type='str'),
                    port=dict(type='int'),
                    credentials_id=dict(type='str'),
                    host_key_verify_none=dict(type='bool', choices=[True]),
                    host_key_verify_known_hosts=dict(type='bool', choices=[True]),
                    host_key_verify_provided=dict(
                        type='dict',
                        options=dict(
                            algorithm=dict(type='str', required=True),
                            key=dict(
                                type='str',
                                required=True,
                                no_log=False,  # Is public key.
                            ),
                        ),
                        no_log=False,  # Is not sensitive.
                    ),
                    host_key_verify_trusted=dict(
                        type='dict',
                        options=dict(
                            allow_initial=dict(type='bool'),
                        ),
                        no_log=False,  # Is not sensitive.
                    ),
                ),
                mutually_exclusive=[[
                    'host_key_verify_none',
                    'host_key_verify_known_hosts',
                    'host_key_verify_provided',
                    'host_key_verify_trusted',
                ]],
            ),
        ),
        supports_check_mode=True,
    )

    deps.validate(module)

    jenkins_node = JenkinsNode(module)

    state = module.params.get('state')
    if state == 'enabled':
        jenkins_node.enabled_node()
    elif state == 'disabled':
        jenkins_node.disabled_node()
    elif state == 'present':
        jenkins_node.present_node()
    else:
        jenkins_node.absent_node()

    module.exit_json(**jenkins_node.result)


if __name__ == '__main__':
    main()
