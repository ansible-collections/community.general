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
        (deleted), enabled (online) or disabled (offline).
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


IS_PYTHON_2 = sys.version_info[0] <= 2


class JenkinsNode:
    def __init__(self, module):
        self.module = module

        self.name = module.params.get('name')
        self.state = module.params.get('state')
        self.token = module.params.get('token')
        self.user = module.params.get('user')
        self.url = module.params.get('url')
        self.num_executors = module.params.get('num_executors')
        self.labels = module.params.get('labels')

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

    def configure_node(self, present):
        if not present:
            # Node would only not be present if in check mode and if not present there
            # is no way to know what would and would not be changed.
            if not self.module.check_mode:
                raise Exception("configure_node present is False outside of check mode")
            return

        configured = False

        data = self.instance.get_node_config(self.name)
        root = ElementTree.fromstring(data)

        if self.num_executors is not None:
            elem = root.find('numExecutors')
            if elem is None:
                elem = ElementTree.SubElement(root, 'numExecutors')
            if elem.text is None or int(elem.text) != self.num_executors:
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

        if configured:
            if IS_PYTHON_2:
                data = ElementTree.tostring(root)
            else:
                data = ElementTree.tostring(root, encoding="unicode")

            self.instance.reconfig_node(self.name, data)

        self.result['configured'] = configured
        if configured:
            self.result['changed'] = True

    def present_node(self):
        def create_node():
            try:
                self.instance.create_node(self.name, launcher=jenkins.LAUNCHER_SSH)
            except jenkins.JenkinsException as e:
                # Some versions of python-jenkins < 1.8.3 has an authorization bug when
                # handling redirects returned when posting new resources. If the node is
                # created OK then can ignore the error.
                if not self.instance.node_exists(self.name):
                    raise e

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
                # handling redirects returned when posting new resources. If the node is
                # deleted OK then can ignore the error.
                if self.instance.node_exists(self.name):
                    raise e

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
        present = self.present_node()

        enabled = False

        if present:
            info = self.instance.get_node_info(self.name)

            if info['offline']:
                if not self.module.check_mode:
                    self.instance.enable_node(self.name)

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
        present = self.present_node()

        disabled = False

        if present:
            info = self.instance.get_node_info(self.name)

            if not info['offline']:
                if not self.module.check_mode:
                    self.instance.disable_node(self.name)

                disabled = True
        else:
            # Would have created node with initial state enabled therefore would have
            # needed to disable therefore disabled.
            if not self.module.check_mode:
                raise Exception("disabled_node present is False outside of check mode")
            disabled = True

        self.result['disabled'] = disabled
        if disabled:
            self.result['changed'] = True


def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(
            msg=missing_required_lib("python-jenkins", url="https://python-jenkins.readthedocs.io/en/latest/install.html"),
            exception=JENKINS_IMP_ERR
        )


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
        ),
        supports_check_mode=True,
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
