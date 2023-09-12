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
version_added: 7.4.0
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
    support: none
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of the Jenkins node to manage.
    required: true
    type: str
  url:
    description:
      - URL of the Jenkins server.
    default: http://localhost:8080
    type: str
  user:
    description:
      - User to authenticate with the Jenkins server.
    type: str
  password:
    description:
      - Password to authenticate with the Jenkins server.
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
    type: str
    choices:
      - enabled
      - disabled
      - present
      - absent
  description:
    description:
      - When specified, sets the Jenkins node description.
    type: str
  num_executors:
    description:
      - When specified, sets the Jenkins node executor count.
    type: int
  remote_fs:
    description:
      - When specified, sets the Jenkins node remote root directory.
    type: path
  labels:
    description:
      - When specified, sets the Jenkins node labels.
    type: list
    elements: str
  mode:
    description:
      - When specified, sets the Jenkins node usage policy.
      - V(normal) means use node as much as possible.
      - V(exclusive) means only build jobs with label expressions that match the node.
    type: str
    choices:
      - normal
      - exclusive
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
          - True
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
              - Key type e.g. V(ssh-rsa).
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
  launch_jnlp:
    description:
      - When specified, sets the Jenkins node to launch by JNLP.
    type: dict
    suboptions:
      data_dir:
        description:
          - When specified, sets the work directory.
        type: path
      work_dir:
        description:
          - When specified, sets the internal data directory.
        type: path
      disable_work_dir:
        description:
          - When specified, disables or enables the work directory.
        type: bool
      assert_work_dir:
        description:
          - When specified, enables or disables failing at startup if the target work
            directory is missing.
        type: bool
      use_web_socket:
        description:
          - When specified, enables or disables using a WebSocket to connect to the
            Jenkins master.
        type: bool
  defer_wipeout:
    description:
      - When specified, enables or disables the Jenkins node improved workspace cleanup
        deferred wipeout method.
    type: bool
  environment:
    description:
      - When specified, sets the Jenkins node environment variables.
      - Environment variables are specified as name-value pairs.
    type: dict
  tools:
    description:
      - When specified, sets the Jenkins node tool locations.
    type: list
    elements: dict
    suboptions:
      type:
        description:
          - Jenkins tool class name e.g. "hudson.plugins.git.GitTool$DescriptorImpl" for
            Git.
        type: str
        required: true
      name:
         description:
           - Jenkins tool instance name.
         type: str
         required: true
      home:
        description:
          - Jenkins tool home directory.
        type: path
        required: true
  offline_message:
    description:
      - Specifies the offline reason message to be set when setting a Jenkins node state
        to V(disabled) (offline).
    type: str
    default: ''
'''

EXAMPLES = '''
- name: Create a Jenkins node using basic authentication
  community.general.jenkins_node:
    url: http://localhost:8080
    user: jenkins
    password: asdfg
    name: my-agent
    state: present

- name: Delete a Jenkins node using token authentication
  community.general.jenkins_node:
    url: http://localhost:8080
    name: my-agent
    state: absent

- name: Enable (online) a Jenkins node anonymously using the default Jenkins server
  community.general.jenkins_node:
    name: my-agent
    state: enabled

- name: Disable (offline) a Jenkins node and set an offline reason message
  community.general.jenkins_node:
    name: my-agent
    state: disabled
    offline_message: Because :)

- name: Set a Jenkins node to launch using SSH and specify a credential
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: ssh
      args:
        host: my-agent.test
        port: 22
        credentials_id: 0bf9599f-b551-4afe-abae-cde7b14a406c

- name: >
    Require manual approval of host keys when connecting to a node by SSH for the first
    time
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: ssh
      args:
        host_key_verify:
          type: approve
          args:
            allow_initial: no

- name: Specify the host key expected when connecting to a node by SSH for the first time
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: ssh
      args:
        host_key_verify:
          type: content
          args:
            algorithm: ssh-rsa
            key: AAAAB3NzaC1yc2EAAAADAQABAAABgQC...

- name: Disable host key verification when connecting to a node by SSH
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: ssh
      args:
        host_key_verify:
          type: none

- name: Use known hosts file for host key verification when connecting to a node by SSH
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: ssh
      args:
        host_key_verify:
          type: known_hosts

- name: Set Jenkins node to launch by connecting it to the controller
  community.general.jenkins_node:
    name: my-agent
    launcher:
      type: jnlp
      args:
        data_dir: remoting
        work_dir: custom
        disable_work_dir: true
        assert_work_dir: no
        use_web_socket: no

- name: Disable deferred wipeout on a Jenkins node
  community.general.jenkins_node:
    name: my-agent
    defer_wipeout: no

- name: Set the Jenkins node environment variables
  community.general.jenkins_node:
    name: my-agent
    environment:
      MY_VAR: My value!
      ANOTHER_VAR: "42"  # Should use only strings

- name: Set the Jenkins node tool locations
  community.general.jenkins_node:
    name: my-agent
    tools:
      - type: hudson.plugins.git.GitTool$DescriptorImpl
        name: Default
        home: /my/git/home
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
  sample: my-agent
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

import traceback
from abc import abstractmethod
from itertools import islice, chain
from xml.etree import ElementTree

JENKINS_IMP_ERR = None
try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    JENKINS_IMP_ERR = traceback.format_exc()
    python_jenkins_installed = False


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator


def bool_to_text(value):
    return {
        True: "true",
        False: "false",
    }[value]


class XMLWrapper:
    def __init__(self, root):
        self.root = root

    @property
    def class_(self):
        if self.root is None:
            return None
        return self.root.get('class')

    @class_.setter
    def class_(self, value):
        if self.root is None:
            raise ValueError('no root element')
        self.root.set('class', value)


class LauncherXMLWrapper(XMLWrapper):
    TAG = 'launcher'
    CLASS = None

    def ensure_class(self):
        if not isinstance(self.CLASS, str):
            raise TypeError('class is not str: got {0}'.format(type(self.CLASS)))
        self.class_ = self.CLASS


class Launcher:
    XMLWrapper = LauncherXMLWrapper

    validator = ArgumentSpecValidator(dict())

    @abstractmethod
    def init_elem(self):
        pass

    @abstractmethod
    def update_elem(self, root):
        pass


class JNLPLauncherXMLWrapper(LauncherXMLWrapper):
    CLASS = 'hudson.slaves.JNLPLauncher'

    @property
    def work_dir_settings(self):
        return self.root.find('workDirSettings')

    @property
    def disable_work_dir(self):
        if self.work_dir_settings is None:
            return None
        return self.work_dir_settings.find('disabled')

    @property
    def work_dir_path(self):
        if self.work_dir_settings is None:
            return None
        return self.work_dir_settings.find('workDirPath')

    def ensure_work_dir_path(self):
        if self.work_dir_settings is None:
            return ElementTree.SubElement(self.root, 'workDirPath')
        return self.work_dir_settings

    @property
    def internal_dir(self):
        if self.work_dir_settings is None:
            return None
        return self.work_dir_settings.find('internalDir')

    @property
    def fail_if_work_dir_is_missing(self):
        if self.work_dir_settings is None:
            return None
        return self.work_dir_settings.find('failIfWorkDirIsMissing')

    @property
    def web_socket(self):
        return self.root.find('webSocket')


class JNLPLauncher(Launcher):
    XMLWrapper = JNLPLauncherXMLWrapper

    def __init__(
        self,
        data_dir=None,
        work_dir=None,
        disable_work_dir=None,
        assert_work_dir=None,
        use_web_socket=None,
    ):
        self.data_dir = data_dir
        self.work_dir = work_dir
        self.disable_work_dir = disable_work_dir
        self.assert_work_dir = assert_work_dir
        self.use_web_socket = use_web_socket

    XML_TEMPLATE = """
<launcher class="hudson.slaves.JNLPLauncher">
    <workDirSettings>
        <disabled>false</disabled>
        <internalDir>remoting</internalDir>
        <failIfWorkDirIsMissing>false</failIfWorkDirIsMissing>
    </workDirSettings>
    <webSocket>false</webSocket>
</launcher>
    """

    def init_elem(self):
        return ElementTree.fromstring(self.XML_TEMPLATE)

    def update_elem(self, root):
        updated = False
        wrapper = JNLPLauncherXMLWrapper(root)

        if self.data_dir is not None:
            if wrapper.internal_dir.text != self.data_dir:
                wrapper.internal_dir.text = self.data_dir
                updated = True

        if self.work_dir is not None:
            if wrapper.work_dir_path is None:
                wrapper.ensure_work_dir_path()
                updated = True
            if wrapper.work_dir_path.text != self.work_dir:
                wrapper.work_dir_path.text = self.work_dir
                updated = True

        if self.disable_work_dir is not None:
            if wrapper.disable_work_dir.text != bool_to_text(self.disable_work_dir):
                wrapper.disable_work_dir.text = bool_to_text(self.disable_work_dir)
                updated = True

        if self.assert_work_dir is not None:
            if wrapper.fail_if_work_dir_is_missing.text != bool_to_text(self.assert_work_dir):
                wrapper.fail_if_work_dir_is_missing.text = bool_to_text(self.assert_work_dir)
                updated = True

        if self.use_web_socket is not None:
            if wrapper.web_socket.text != bool_to_text(self.use_web_socket):
                wrapper.web_socket.text = bool_to_text(self.use_web_socket)
                updated = True

        return updated


class SSHHostKeyVerifyXMLWrapper(XMLWrapper):
    TAG = 'sshHostKeyVerificationStrategy'


class SSHHostKeyVerify:
    CLASS = None

    validator = ArgumentSpecValidator(dict())

    def init(self):
        root = ElementTree.Element(SSHHostKeyVerifyXMLWrapper.TAG)
        SSHHostKeyVerifyXMLWrapper(root).class_ = self.CLASS
        return root

    def update(self, root):
        class_ = SSHHostKeyVerifyXMLWrapper(root).class_
        if class_ != self.CLASS:
            raise ValueError('unexpected class {0}: expected {1}'.format(class_, self.CLASS))


class KnownHostsSSHHostKeyVerify(SSHHostKeyVerify):
    CLASS = 'hudson.plugins.sshslaves.verifiers.KnownHostsFileKeyVerificationStrategy'


class NoneSSHHostKeyVerify(SSHHostKeyVerify):
    CLASS = 'hudson.plugins.sshslaves.verifiers.NonVerifyingKeyVerificationStrategy'


class TrustedSSHHostKeyVerifyXMLWrapper(SSHHostKeyVerifyXMLWrapper):
    @property
    def allow_initial(self):
        return self.root.find('requireInitialManualTrust')


class TrustedSSHHostKeyVerify(SSHHostKeyVerify):
    CLASS = 'hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy'

    XML_TEMPLATE = """
<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyTrustedKeyVerificationStrategy">
    <requireInitialManualTrust>false</requireInitialManualTrust>
</sshHostKeyVerificationStrategy>
    """

    def __init__(self, allow_initial=None):
        self.allow_initial = allow_initial

    def init(self):
        return ElementTree.fromstring(self.XML_TEMPLATE)

    def update(self, root):
        super(TrustedSSHHostKeyVerify, self).update(root)

        updated = False
        wrapper = TrustedSSHHostKeyVerifyXMLWrapper(root)

        if self.allow_initial is not None:
            if wrapper.allow_initial.text != bool_to_text(self.allow_initial):
                wrapper.allow_initial.text = bool_to_text(self.allow_initial)
                updated = True

        return updated


class ProvidedSSHHostKeyVerifyXMLWrapper(SSHHostKeyVerifyXMLWrapper):
    @property
    def container(self):
        return self.root.find('key')

    @property
    def algorithm(self):
        return self.container.find('algorithm')

    @property
    def key(self):
        return self.container.find('key')


class ProvidedSSHHostKeyVerify(SSHHostKeyVerify):
    CLASS = 'hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy'

    XML_TEMPLATE = """
<sshHostKeyVerificationStrategy class="hudson.plugins.sshslaves.verifiers.ManuallyProvidedKeyVerificationStrategy">
    <key>
        <algorithm/>
        <key/>
    </key>
</sshHostKeyVerificationStrategy>
    """

    def __init__(self, algorithm, key):
        self.algorithm = algorithm
        self.key = key

    def init(self):
        return ElementTree.fromstring(self.XML_TEMPLATE)

    def update(self, root):
        super(ProvidedSSHHostKeyVerify, self).update(root)

        updated = False
        wrapper = ProvidedSSHHostKeyVerifyXMLWrapper(root)

        if wrapper.algorithm.text != self.algorithm:
            wrapper.algorithm.text = self.algorithm
            updated = True

        if wrapper.key.text != self.key:
            wrapper.key.text = self.key
            updated = True

        return updated


class SSHLauncherXMLWrapper(LauncherXMLWrapper):
    CLASS = 'hudson.plugins.sshslaves.SSHLauncher'

    @property
    def host(self):
        return self.root.find('host')

    @host.setter
    def host(self, elem):
        if self.host is not None:
            self.root.remove(self.host)
        self.root.append(elem)

    def ensure_host(self):
        if self.host is None:
            return ElementTree.SubElement(self.root, 'host')
        return self.host

    @property
    def port(self):
        return self.root.find('port')

    @property
    def credentials_id(self):
        return self.root.find('credentialsId')

    def ensure_credentials_id(self):
        if self.credentials_id is None:
            return ElementTree.SubElement(self.root, 'credentialsId')
        return self.credentials_id

    @property
    def host_key_verify(self):
        return self.root.find(SSHHostKeyVerifyXMLWrapper.TAG)

    @host_key_verify.setter
    def host_key_verify(self, elem):
        if self.host_key_verify is not None:
            self.root.remove(self.host_key_verify)
        self.root.append(elem)


class SSHLauncher(Launcher):
    XMLWrapper = SSHLauncherXMLWrapper

    def __init__(
        self,
        host=None,
        port=None,
        credentials_id=None,
        host_key_verify=None,
    ):
        self.host = host
        self.port = port
        self.credentials_id = credentials_id
        self.host_key_verify = host_key_verify

    XML_TEMPLATE = """
<launcher class="hudson.plugins.sshslaves.SSHLauncher">
    <port>22</port>
    <credentialsId/>
    <launchTimeoutSeconds>60</launchTimeoutSeconds>
    <maxNumRetries>10</maxNumRetries>
    <retryWaitTime>15</retryWaitTime>
    <tcpNoDelay>true</tcpNoDelay>
</launcher>
    """

    def init_elem(self):
        root = ElementTree.fromstring(self.XML_TEMPLATE)

        wrapper = self.XMLWrapper(root)
        wrapper.host_key_verify = self.host_key_verify.init()

        return root

    def update_elem(self, root):
        updated = False
        wrapper = self.XMLWrapper(root)

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
            if SSHHostKeyVerifyXMLWrapper(wrapper.host_key_verify).class_ != self.host_key_verify.CLASS:
                wrapper.host_key_verify = self.host_key_verify.init()
                updated = True
            if self.host_key_verify.update(wrapper.host_key_verify):
                updated = True

        return updated


class TreeMapXMLWrapper(XMLWrapper):
    TAG = 'tree-map'

    @property
    def comparator(self):
        elem = self.root.find('default')
        if elem is None:
            return None
        return elem.find('comparator')

    @property
    def int(self):
        return self.root.find('int')

    @property
    def strings(self):
        return self.root.findall('string')

    @strings.setter
    def strings(self, strings):
        for string in self.strings:
            self.root.remove(string)
        for string in strings:
            self.root.append(string)


class TreeMap:
    def __init__(self, items, comparator):
        self.items = items
        self.comparator = comparator

    @classmethod
    def from_elem(cls, root):
        wrapper = TreeMapXMLWrapper(root)

        items = []
        strings = iter(wrapper.strings)
        while True:
            pair = tuple(islice(strings, 2))
            if len(pair) != 2:
                break
            items.append((pair[0].text, pair[1].text))

        return TreeMap(items, wrapper.comparator.get('class'))

    XML_TEMPLATE = """
<tree-map>
    <default>
        <comparator class="java.lang.String$CaseInsensitiveComparator"/>
    </default>
    <int>0</int>
</tree-map>
    """

    def to_elem(self):
        root = ElementTree.fromstring(self.XML_TEMPLATE)
        wrapper = TreeMapXMLWrapper(root)

        wrapper.comparator.set('class', self.comparator)
        wrapper.int.text = str(len(self.items))

        def string(value):
            elem = ElementTree.Element('string')
            elem.text = str(value)
            return elem

        wrapper.strings = map(string, chain(*self.items))

        return root


class EnvironmentVariablesXMLWrapper:
    TAG = 'hudson.slaves.EnvironmentVariablesNodeProperty'

    def __init__(self, root):
        self.root = root

    @property
    def envvars(self):
        return self.root.find('envVars')

    @property
    def tree_map(self):
        if self.envvars is None:
            return None
        return self.envvars.find(TreeMapXMLWrapper.TAG)

    @tree_map.setter
    def tree_map(self, elem):
        prev = self.envvars.find(TreeMapXMLWrapper.TAG)
        if prev is not None:
            self.envvars.remove(prev)
        self.envvars.append(elem)


class EnvironmentVariables:
    @classmethod
    def from_elem(cls, root):
        wrapper = EnvironmentVariablesXMLWrapper(root)
        items = TreeMap.from_elem(wrapper.tree_map).items
        return dict(items)

    XML_TEMPLATE = """
<hudson.slaves.EnvironmentVariablesNodeProperty>
    <envVars serialization="custom">
        <unserializable-parents/>
        <!--tree-map goes here-->
    </envVars>
</hudson.slaves.EnvironmentVariablesNodeProperty>
    """

    @classmethod
    def to_elem(cls, items):
        root = ElementTree.fromstring(cls.XML_TEMPLATE)

        wrapper = EnvironmentVariablesXMLWrapper(root)
        wrapper.tree_map = TreeMap(
            list(items.items()),
            'java.lang.String$CaseInsensitiveComparator'
        ).to_elem()

        return root


class ToolLocationsItemXMLWrapper:
    TAG = 'hudson.tools.ToolLocationNodeProperty_-ToolLocation'

    def __init__(self, root):
        self.root = root

    @property
    def type(self):
        return self.root.find('type')

    @property
    def name(self):
        return self.root.find('name')

    @property
    def home(self):
        return self.root.find('home')


class ToolLocationsItem:
    def __init__(self, type, name, home):
        self.type = type
        self.name = name
        self.home = home

    @classmethod
    def from_dict(cls, item):
        return ToolLocationsItem(
            item['type'],
            item['name'],
            item['home'],
        )

    def to_dict(self):
        return {
            'type': self.type,
            'name': self.name,
            'home': self.home,
        }

    @classmethod
    def from_elem(cls, root):
        elem = root.find('type')
        if elem is None:
            raise KeyError('type')
        type = elem.text

        elem = root.find('name')
        if elem is None:
            raise KeyError('name')
        name = elem.text

        elem = root.find('home')
        if elem is None:
            raise KeyError('home')
        home = elem.text

        return ToolLocationsItem(type, name, home)

    def to_elem(self):
        root = ElementTree.Element(ToolLocationsItemXMLWrapper.TAG)

        elem = ElementTree.SubElement(root, 'type')
        elem.text = self.type

        elem = ElementTree.SubElement(root, 'name')
        elem.text = self.name

        elem = ElementTree.SubElement(root, 'home')
        elem.text = self.home

        return root


class ToolLocationsXMLWrapper:
    TAG = 'hudson.tools.ToolLocationNodeProperty'

    def __init__(self, root):
        self.root = root

    @property
    def container(self):
        return self.root.find('locations')

    @property
    def items(self):
        return self.container.findall(ToolLocationsItemXMLWrapper.TAG)

    @items.setter
    def items(self, items):
        for item in self.container:
            self.container.remove(item)
        for item in items:
            self.container.append(item)


class ToolLocations:
    @classmethod
    def from_elem(cls, root):
        wrapper = ToolLocationsXMLWrapper(root)

        return [
            ToolLocationsItem.from_elem(elem).to_dict() for elem in wrapper.items
        ]

    XML_TEMPLATE = """
<hudson.tools.ToolLocationNodeProperty>
    <locations>
        <!--items go here-->
    </locations>
</hudson.tools.ToolLocationNodeProperty>
    """

    @classmethod
    def to_elem(cls, items):
        root = ElementTree.fromstring(cls.XML_TEMPLATE)

        wrapper = ToolLocationsXMLWrapper(root)
        wrapper.items = (
            ToolLocationsItem.from_dict(item).to_elem() for item in items
        )

        return root


class JenkinsNode:
    def get_server(self):
        try:
            if self.user and self.password:
                return jenkins.Jenkins(self.url, self.user, self.password)
            elif self.user and self.token:
                return jenkins.Jenkins(self.url, self.user, self.token)
            elif self.user and not (self.password or self.token):
                return jenkins.Jenkins(self.url, self.user)
            else:
                return jenkins.Jenkins(self.url)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e))

    @staticmethod
    def get_ssh_launcher(args):
        if args.get('host_key_verify_none'):
            host_key_verify = NoneSSHHostKeyVerify()
        elif args.get('host_key_verify_known_hosts'):
            host_key_verify = KnownHostsSSHHostKeyVerify()
        elif args.get('host_key_verify_provided'):
            host_key_verify = ProvidedSSHHostKeyVerify(
                args['host_key_verify_provided']['algorithm'],
                args['host_key_verify_provided']['key'],
            )
        elif args.get('host_key_verify_trusted'):
            host_key_verify = TrustedSSHHostKeyVerify(
                allow_initial=args['host_key_verify_trusted'].get('allow_initial')
            )
        else:
            host_key_verify = None

        return SSHLauncher(
            host=args.get('host'),
            port=args.get('port'),
            credentials_id=args.get('credentials_id'),
            host_key_verify=host_key_verify,
        )

    def __init__(self, module):
        self.module = module

        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.state = module.params.get('state')
        self.token = module.params.get('token')
        self.user = module.params.get('user')
        self.url = module.params.get('url')
        self.num_executors = module.params.get('num_executors')
        self.description = module.params.get('description')
        self.labels = module.params.get('labels')
        self.environment = module.params.get('environment')
        self.remote_fs = module.params.get('remote_fs')
        self.mode = module.params.get('mode')
        self.defer_wipeout = module.params.get('defer_wipeout')
        self.tools = module.params.get('tools')
        self.offline_message = module.params.get('offline_message')

        if module.params.get('launch_ssh') is not None:
            self.launcher = self.get_ssh_launcher(module.params['launch_ssh'])
        elif module.params.get('launch_jnlp') is not None:
            args = module.params['launch_jnlp']
            self.launcher = JNLPLauncher(
                data_dir=args.get('data_dir'),
                work_dir=args.get('work_dir'),
                disable_work_dir=args.get('disable_work_dir'),
                assert_work_dir=args.get('assert_work_dir'),
                use_web_socket=args.get('use_web_socket'),
            )
        else:
            self.launcher = None

        self.server = self.get_server()

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
        }

    def configure_node(self):
        self.server.assert_node_exists(self.name)

        configured = False
        data = self.server.get_node_config(self.name)
        root = ElementTree.fromstring(data)

        if self.launcher is not None:
            elem = root.find(LauncherXMLWrapper.TAG)
            if LauncherXMLWrapper(elem).class_ != self.launcher.XMLWrapper.CLASS:
                if elem is not None:
                    root.remove(elem)
                elem = self.launcher.init_elem()
                root.append(elem)
                configured = True
            if self.launcher.update_elem(elem):
                configured = True

        if self.description is not None:
            elem = root.find('description')
            if elem is None:
                elem = ElementTree.SubElement(root, 'description')
            if elem.text != self.description:
                elem.text = self.description
                configured = True

        if self.num_executors is not None:
            elem = root.find('numExecutors')
            if elem is None:
                elem = ElementTree.SubElement(root, 'numExecutors')
            if int(elem.text) != self.num_executors:
                elem.text = str(self.num_executors)
                configured = True

        if self.labels is not None:
            elem = root.find('label')
            if elem is None:
                elem = ElementTree.SubElement(root, 'label')
            labels = []
            if elem.text:
                labels = elem.text.split()
            if labels != self.labels:
                elem.text = " ".join(self.labels)
                configured = True

        if self.remote_fs is not None:
            elem = root.find('remoteFS')
            if elem is None:
                elem = ElementTree.SubElement(root, 'remoteFS')
            if elem.text != self.remote_fs:
                elem.text = self.remote_fs
                configured = True

        if self.mode is not None:
            elem = root.find('mode')
            if elem is None:
                elem = ElementTree.SubElement(root, 'mode')
            if elem.text.lower() != self.mode:
                elem.text = self.mode.upper()
                configured = True

        props_elem = root.find('nodeProperties')
        if props_elem is None:
            props_elem = ElementTree.SubElement(root, 'nodeProperties')

        if self.defer_wipeout is not None:
            tag = 'hudson.plugins.ws__cleanup.DisableDeferredWipeoutNodeProperty'
            elem = props_elem.find(tag)
            if self.defer_wipeout:
                if elem is not None:
                    props_elem.remove(elem)
                    configured = True
            else:
                if elem is None:
                    ElementTree.SubElement(props_elem, tag)
                    configured = True

        if self.environment is not None:
            msg = 'environment variable "{0}" {1} modified by str: result will always be "changed"'
            for name, value in self.environment.items():
                if str(name) != name:
                    self.module.warn(msg.format(name, 'name'))
                if str(value) != value:
                    self.module.warn(msg.format(name, 'value'))

            elem = props_elem.find(EnvironmentVariablesXMLWrapper.TAG)
            environment = None if elem is None else EnvironmentVariables.from_elem(elem)

            if environment != self.environment:
                if elem is not None:
                    props_elem.remove(elem)
                elem = EnvironmentVariables.to_elem(self.environment)
                props_elem.append(elem)
                configured = True

        if self.tools is not None:
            elem = props_elem.find(ToolLocationsXMLWrapper.TAG)
            tools = None if elem is None else ToolLocations.from_elem(elem)

            if tools != self.tools:
                if elem is not None:
                    props_elem.remove(elem)
                elem = ToolLocations.to_elem(self.tools)
                props_elem.append(elem)
                configured = True

        if configured:
            data = ElementTree.tostring(root, encoding='unicode')
            if not self.module.check_mode:
                self.server.reconfig_node(self.name, data)

        self.result['configured'] = configured
        if configured:
            self.result['changed'] = True

    def present_node(self):
        present = self.server.node_exists(self.name)
        created = False

        if not present:
            if not self.module.check_mode:
                self.server.create_node(self.name)
                present = True
            created = True

        if present:
            self.configure_node()

        self.result['created'] = created
        if created:
            self.result['changed'] = True

        return present

    def absent_node(self):
        present = self.server.node_exists(self.name)
        deleted = False

        if present:
            if not self.module.check_mode:
                self.server.delete_node(self.name)
            deleted = True

        self.result['deleted'] = deleted
        if deleted:
            self.result['changed'] = True

    def enabled_node(self):
        present = self.present_node()
        enabled = False

        if present:
            info = self.server.get_node_info(self.name)
            if info['offline']:
                if not self.module.check_mode:
                    self.server.enable_node(self.name)
                enabled = True

        self.result['enabled'] = enabled
        if enabled:
            self.result['changed'] = True

    def disabled_node(self):
        present = self.present_node()
        disabled = False

        if present:
            info = self.server.get_node_info(self.name)
            if (
                not info['offline']
                or info['offlineCauseReason'] != self.offline_message
            ):
                if not self.module.check_mode:
                    self.server.disable_node(self.name, self.offline_message)
                disabled = True

        self.result['disabled'] = disabled
        if disabled:
            self.result['changed'] = True


def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(
            msg=missing_required_lib("python-jenkins",
                                     url="https://python-jenkins.readthedocs.io/en/latest/install.html"),
            exception=JENKINS_IMP_ERR)


def main():
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=dict(
            name=dict(type='str', required=True),
            url=dict(default='http://localhost:8080'),
            user=dict(),
            password=dict(no_log=True),
            token=dict(no_log=True),
            state=dict(
                choices=['enabled', 'disabled', 'present', 'absent'],
                default='present',
            ),
            description=dict(type='str'),
            num_executors=dict(type='int'),
            remote_fs=dict(type='path'),
            labels=dict(type='list', elements='str'),
            mode=dict(choices=['normal', 'exclusive']),
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
                            key=dict(type='str', required=True),
                        ),
                    ),
                    host_key_verify_trusted=dict(
                        type='dict',
                        options=dict(
                            allow_initial=dict(type='bool'),
                        ),
                    ),
                ),
                mutually_exclusive=[
                    'host_key_verify_none',
                    'host_key_verify_known_hosts',
                    'host_key_verify_provided',
                    'host_key_verify_trusted',
                ]
            ),
            launch_jnlp=dict(
                type='dict',
                options=dict(
                    data_dir=dict(type='path'),
                    work_dir=dict(type='path'),
                    disable_work_dir=dict(type='bool'),
                    assert_work_dir=dict(type='bool'),
                    use_web_socket=dict(type='bool'),
                ),
            ),
            defer_wipeout=dict(type='bool'),
            environment=dict(type='dict'),
            tools=dict(
                type='list',
                elements='dict',
                options=dict(
                    type=dict(type='str', required=True),
                    name=dict(type='str', required=True),
                    home=dict(type='path', required=True),
                )
            ),
            offline_message=dict(type='str', default=''),
        ),
        mutually_exclusive=[
            ['password', 'token'],
            ['launch_ssh', 'launch_jnlp'],
        ],
    )

    test_dependencies(module)
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
