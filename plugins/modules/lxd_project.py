#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: lxd_project
short_description: Manage LXD projects
version_added: 4.8.0
description:
  - Management of LXD projects.
author: "Raymond Chang (@we10710aa)"
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
      - Name of the project.
    required: true
    type: str
  description:
    description:
      - Description of the project.
    type: str
  config:
    description:
      - 'The config for the project (for example V({"features.profiles": "true"})).'
      - See U(https://documentation.ubuntu.com/lxd/en/latest/api/#/projects/project_get).
      - If the project already exists and its "config" value in metadata obtained from C(GET /1.0/projects/<name>)
        U(https://documentation.ubuntu.com/lxd/en/latest/api/#/projects/project_get)
        are different, then this module tries to apply the configurations U(https://documentation.ubuntu.com/lxd/en/latest/api/#/projects/project_put).
    type: dict
  new_name:
    description:
      - A new name of a project.
      - If this parameter is specified a project is renamed to this name.
      - See U(https://documentation.ubuntu.com/lxd/en/latest/api/#/projects/project_post).
    required: false
    type: str
  merge_project:
    description:
      - Merge the configuration of the present project with the new desired configuration, instead of replacing it. If configuration
        is the same after merged, no change is made.
    required: false
    default: false
    type: bool
  state:
    choices:
      - present
      - absent
    description:
      - Define the state of a project.
    required: false
    default: present
    type: str
  url:
    description:
      - The Unix domain socket path or the https URL for the LXD server.
    required: false
    default: unix:/var/lib/lxd/unix.socket
    type: str
  snap_url:
    description:
      - The Unix domain socket path when LXD is installed by snap package manager.
    required: false
    default: unix:/var/snap/lxd/common/lxd/unix.socket
    type: str
  client_key:
    description:
      - The client certificate key file path.
      - If not specified, it defaults to C($HOME/.config/lxc/client.key).
    required: false
    aliases: [key_file]
    type: path
  client_cert:
    description:
      - The client certificate file path.
      - If not specified, it defaults to C($HOME/.config/lxc/client.crt).
    required: false
    aliases: [cert_file]
    type: path
  trust_password:
    description:
      - The client trusted password.
      - 'You need to set this password on the LXD server before running this module using the following command: C(lxc config
        set core.trust_password <some random password>) See U(https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/).'
      - If O(trust_password) is set, this module send a request for authentication before sending any requests.
    required: false
    type: str
notes:
  - Projects must have a unique name. If you attempt to create a project with a name that already existed in the users namespace
    the module simply returns as "unchanged".
"""

EXAMPLES = r"""
# An example for creating a project
- hosts: localhost
  connection: local
  tasks:
    - name: Create a project
      community.general.lxd_project:
        name: ansible-test-project
        state: present
        config: {}
        description: my new project

# An example for renaming a project
- hosts: localhost
  connection: local
  tasks:
    - name: Rename ansible-test-project to ansible-test-project-new-name
      community.general.lxd_project:
        name: ansible-test-project
        new_name: ansible-test-project-new-name
        state: present
        config: {}
        description: my new project
"""

RETURN = r"""
old_state:
  description: The old state of the project.
  returned: success
  type: str
  sample: "absent"
logs:
  description: The logs of requests and responses.
  returned: when ansible-playbook is invoked with -vvvv.
  type: list
  elements: dict
  contains:
    type:
      description: Type of actions performed, currently only V(sent request).
      type: str
      sample: "sent request"
    request:
      description: HTTP request sent to LXD server.
      type: dict
      contains:
        method:
          description: Method of HTTP request.
          type: str
          sample: "GET"
        url:
          description: URL path of HTTP request.
          type: str
          sample: "/1.0/projects/test-project"
        json:
          description: JSON body of HTTP request.
          type: str
          sample: "(too long to be placed here)"
        timeout:
          description: Timeout of HTTP request, V(null) if unset.
          type: int
          sample: null
    response:
      description: HTTP response received from LXD server.
      type: dict
      contains:
        json:
          description: JSON of HTTP response.
          type: str
          sample: "(too long to be placed here)"
actions:
  description: List of actions performed for the project.
  returned: success
  type: list
  elements: str
  sample: ["create"]
"""

from ansible_collections.community.general.plugins.module_utils.lxd import (
    LXDClient, LXDClientException, default_key_file, default_cert_file
)
from ansible.module_utils.basic import AnsibleModule
import os

# ANSIBLE_LXD_DEFAULT_URL is a default value of the lxd endpoint
ANSIBLE_LXD_DEFAULT_URL = 'unix:/var/lib/lxd/unix.socket'

# PROJECTS_STATES is a list for states supported
PROJECTS_STATES = [
    'present', 'absent'
]

# CONFIG_PARAMS is a list of config attribute names.
CONFIG_PARAMS = [
    'config', 'description'
]


class LXDProjectManagement(object):
    def __init__(self, module):
        """Management of LXC projects via Ansible.

        :param module: Processed Ansible Module.
        :type module: ``object``
        """
        self.module = module
        self.name = self.module.params['name']
        self._build_config()
        self.state = self.module.params['state']
        self.new_name = self.module.params.get('new_name', None)

        self.key_file = self.module.params.get('client_key')
        if self.key_file is None:
            self.key_file = default_key_file()
        self.cert_file = self.module.params.get('client_cert')
        if self.cert_file is None:
            self.cert_file = default_cert_file()
        self.debug = self.module._verbosity >= 4

        try:
            if self.module.params['url'] != ANSIBLE_LXD_DEFAULT_URL:
                self.url = self.module.params['url']
            elif os.path.exists(self.module.params['snap_url'].replace('unix:', '')):
                self.url = self.module.params['snap_url']
            else:
                self.url = self.module.params['url']
        except Exception as e:
            self.module.fail_json(msg=e.msg)

        try:
            self.client = LXDClient(
                self.url, key_file=self.key_file, cert_file=self.cert_file,
                debug=self.debug
            )
        except LXDClientException as e:
            self.module.fail_json(msg=e.msg)
        self.trust_password = self.module.params.get('trust_password', None)
        self.actions = []

    def _build_config(self):
        self.config = {}
        for attr in CONFIG_PARAMS:
            param_val = self.module.params.get(attr, None)
            if param_val is not None:
                self.config[attr] = param_val

    def _get_project_json(self):
        return self.client.do(
            'GET', '/1.0/projects/{0}'.format(self.name),
            ok_error_codes=[404]
        )

    @staticmethod
    def _project_json_to_module_state(resp_json):
        if resp_json['type'] == 'error':
            return 'absent'
        return 'present'

    def _update_project(self):
        if self.state == 'present':
            if self.old_state == 'absent':
                if self.new_name is None:
                    self._create_project()
                else:
                    self.module.fail_json(
                        msg='new_name must not be set when the project does not exist and the state is present',
                        changed=False)
            else:
                if self.new_name is not None and self.new_name != self.name:
                    self._rename_project()
                if self._needs_to_apply_project_configs():
                    self._apply_project_configs()
        elif self.state == 'absent':
            if self.old_state == 'present':
                if self.new_name is None:
                    self._delete_project()
                else:
                    self.module.fail_json(
                        msg='new_name must not be set when the project exists and the specified state is absent',
                        changed=False)

    def _create_project(self):
        config = self.config.copy()
        config['name'] = self.name
        self.client.do('POST', '/1.0/projects', config)
        self.actions.append('create')

    def _rename_project(self):
        config = {'name': self.new_name}
        self.client.do('POST', '/1.0/projects/{0}'.format(self.name), config)
        self.actions.append('rename')
        self.name = self.new_name

    def _needs_to_change_project_config(self, key):
        if key not in self.config:
            return False
        old_configs = self.old_project_json['metadata'].get(key, None)
        return self.config[key] != old_configs

    def _needs_to_apply_project_configs(self):
        return (
            self._needs_to_change_project_config('config') or
            self._needs_to_change_project_config('description')
        )

    def _merge_dicts(self, source, destination):
        """ Return a new dict that merge two dict,
        with values in source dict overwrite destination dict

        Args:
            dict(source): source dict
            dict(destination): destination dict
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(destination): merged dict"""
        result = destination.copy()
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = result.setdefault(key, {})
                self._merge_dicts(value, node)
            else:
                result[key] = value
        return result

    def _apply_project_configs(self):
        """ Selection of the procedure: rebuild or merge

        The standard behavior is that all information not contained
        in the play is discarded.

        If "merge_project" is provides in the play and "True", then existing
        configurations from the project and new ones defined are merged.

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        old_config = dict()
        old_metadata = self.old_project_json['metadata'].copy()
        for attr in CONFIG_PARAMS:
            old_config[attr] = old_metadata[attr]

        if self.module.params['merge_project']:
            config = self._merge_dicts(self.config, old_config)
            if config == old_config:
                # no need to call api if merged config is the same
                # as old config
                return
        else:
            config = self.config.copy()
        # upload config to lxd
        self.client.do('PUT', '/1.0/projects/{0}'.format(self.name), config)
        self.actions.append('apply_projects_configs')

    def _delete_project(self):
        self.client.do('DELETE', '/1.0/projects/{0}'.format(self.name))
        self.actions.append('delete')

    def run(self):
        """Run the main method."""

        try:
            if self.trust_password is not None:
                self.client.authenticate(self.trust_password)

            self.old_project_json = self._get_project_json()
            self.old_state = self._project_json_to_module_state(
                self.old_project_json)
            self._update_project()

            state_changed = len(self.actions) > 0
            result_json = {
                'changed': state_changed,
                'old_state': self.old_state,
                'actions': self.actions
            }
            if self.client.debug:
                result_json['logs'] = self.client.logs
            self.module.exit_json(**result_json)
        except LXDClientException as e:
            state_changed = len(self.actions) > 0
            fail_params = {
                'msg': e.msg,
                'changed': state_changed,
                'actions': self.actions
            }
            if self.client.debug:
                fail_params['logs'] = e.kwargs['logs']
            self.module.fail_json(**fail_params)


def main():
    """Ansible Main module."""

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(
                type='str',
                required=True
            ),
            new_name=dict(
                type='str',
            ),
            config=dict(
                type='dict',
            ),
            description=dict(
                type='str',
            ),
            merge_project=dict(
                type='bool',
                default=False
            ),
            state=dict(
                choices=PROJECTS_STATES,
                default='present'
            ),
            url=dict(
                type='str',
                default=ANSIBLE_LXD_DEFAULT_URL
            ),
            snap_url=dict(
                type='str',
                default='unix:/var/snap/lxd/common/lxd/unix.socket'
            ),
            client_key=dict(
                type='path',
                aliases=['key_file']
            ),
            client_cert=dict(
                type='path',
                aliases=['cert_file']
            ),
            trust_password=dict(type='str', no_log=True)
        ),
        supports_check_mode=False,
    )

    lxd_manage = LXDProjectManagement(module=module)
    lxd_manage.run()


if __name__ == '__main__':
    main()
