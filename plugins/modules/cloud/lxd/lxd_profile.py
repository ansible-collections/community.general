#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Hiroaki Nakamura <hnakamur@gmail.com>
# Copyright (c) 2020, Frank Dornheim <dornheim@posteo.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: lxd_profile
short_description: Manage LXD profiles
description:
  - Management of LXD profiles
author: "Hiroaki Nakamura (@hnakamur)"
options:
    name:
        description:
          - Name of a profile.
        required: true
        type: str
    project:
        description:
         - 'Project of a profile.
           See U(https://github.com/lxc/lxd/blob/master/doc/projects.md).'
        type: str
        required: false
        version_added: 4.8.0
    description:
        description:
          - Description of the profile.
        type: str
    config:
        description:
          - 'The config for the container (e.g. {"limits.memory": "4GB"}).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#patch-3)'
          - If the profile already exists and its "config" value in metadata
            obtained from
            GET /1.0/profiles/<name>
            U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#get-19)
            are different, they this module tries to apply the configurations.
          - Not all config values are supported to apply the existing profile.
            Maybe you need to delete and recreate a profile.
        required: false
        type: dict
    devices:
        description:
          - 'The devices for the profile
            (e.g. {"rootfs": {"path": "/dev/kvm", "type": "unix-char"}).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#patch-3)'
        required: false
        type: dict
    new_name:
        description:
          - A new name of a profile.
          - If this parameter is specified a profile will be renamed to this name.
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-11)
        required: false
        type: str
    merge_profile:
        description:
            - Merge the configuration of the present profile with the new desired configuration,
              instead of replacing it.
        required: false
        default: false
        type: bool
        version_added: 2.1.0
    state:
        choices:
          - present
          - absent
        description:
          - Define the state of a profile.
        required: false
        default: present
        type: str
    url:
        description:
          - The unix domain socket path or the https URL for the LXD server.
        required: false
        default: unix:/var/lib/lxd/unix.socket
        type: str
    snap_url:
        description:
          - The unix domain socket path when LXD is installed by snap package manager.
        required: false
        default: unix:/var/snap/lxd/common/lxd/unix.socket
        type: str
    client_key:
        description:
          - The client certificate key file path.
          - If not specified, it defaults to C($HOME/.config/lxc/client.key).
        required: false
        aliases: [ key_file ]
        type: path
    client_cert:
        description:
          - The client certificate file path.
          - If not specified, it defaults to C($HOME/.config/lxc/client.crt).
        required: false
        aliases: [ cert_file ]
        type: path
    trust_password:
        description:
          - The client trusted password.
          - You need to set this password on the LXD server before
            running this module using the following command.
            lxc config set core.trust_password <some random password>
            See U(https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/)
          - If trust_password is set, this module send a request for
            authentication before sending any requests.
        required: false
        type: str
notes:
  - Profiles must have a unique name. If you attempt to create a profile
    with a name that already existed in the users namespace the module will
    simply return as "unchanged".
'''

EXAMPLES = '''
# An example for creating a profile
- hosts: localhost
  connection: local
  tasks:
    - name: Create a profile
      community.general.lxd_profile:
        name: macvlan
        state: present
        config: {}
        description: my macvlan profile
        devices:
          eth0:
            nictype: macvlan
            parent: br0
            type: nic

# An example for creating a profile in project mytestproject
- hosts: localhost
  connection: local
  tasks:
    - name: Create a profile
      community.general.lxd_profile:
        name: testprofile
        project: mytestproject
        state: present
        config: {}
        description: test profile in project mytestproject
        devices: {}

# An example for creating a profile via http connection
- hosts: localhost
  connection: local
  tasks:
  - name: Create macvlan profile
    community.general.lxd_profile:
      url: https://127.0.0.1:8443
      # These client_cert and client_key values are equal to the default values.
      #client_cert: "{{ lookup('env', 'HOME') }}/.config/lxc/client.crt"
      #client_key: "{{ lookup('env', 'HOME') }}/.config/lxc/client.key"
      trust_password: mypassword
      name: macvlan
      state: present
      config: {}
      description: my macvlan profile
      devices:
        eth0:
          nictype: macvlan
          parent: br0
          type: nic

# An example for modify/merge a profile
- hosts: localhost
  connection: local
  tasks:
    - name: Merge a profile
      community.general.lxd_profile:
        merge_profile: true
        name: macvlan
        state: present
        config: {}
        description: my macvlan profile
        devices:
          eth0:
            nictype: macvlan
            parent: br0
            type: nic

# An example for deleting a profile
- hosts: localhost
  connection: local
  tasks:
    - name: Delete a profile
      community.general.lxd_profile:
        name: macvlan
        state: absent

# An example for renaming a profile
- hosts: localhost
  connection: local
  tasks:
    - name: Rename a profile
      community.general.lxd_profile:
        name: macvlan
        new_name: macvlan2
        state: present
'''

RETURN = '''
old_state:
  description: The old state of the profile
  returned: success
  type: str
  sample: "absent"
logs:
  description: The logs of requests and responses.
  returned: when ansible-playbook is invoked with -vvvv.
  type: list
  sample: "(too long to be placed here)"
actions:
  description: List of actions performed for the profile.
  returned: success
  type: list
  sample: ["create"]
'''

import os
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.lxd import LXDClient, LXDClientException
from ansible.module_utils.six.moves.urllib.parse import urlencode

# ANSIBLE_LXD_DEFAULT_URL is a default value of the lxd endpoint
ANSIBLE_LXD_DEFAULT_URL = 'unix:/var/lib/lxd/unix.socket'

# PROFILE_STATES is a list for states supported
PROFILES_STATES = [
    'present', 'absent'
]

# CONFIG_PARAMS is a list of config attribute names.
CONFIG_PARAMS = [
    'config', 'description', 'devices'
]


class LXDProfileManagement(object):
    def __init__(self, module):
        """Management of LXC containers via Ansible.

        :param module: Processed Ansible Module.
        :type module: ``object``
        """
        self.module = module
        self.name = self.module.params['name']
        self.project = self.module.params['project']
        self._build_config()
        self.state = self.module.params['state']
        self.new_name = self.module.params.get('new_name', None)

        self.key_file = self.module.params.get('client_key')
        if self.key_file is None:
            self.key_file = '{0}/.config/lxc/client.key'.format(os.environ['HOME'])
        self.cert_file = self.module.params.get('client_cert')
        if self.cert_file is None:
            self.cert_file = '{0}/.config/lxc/client.crt'.format(os.environ['HOME'])
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

    def _get_profile_json(self):
        url = '/1.0/profiles/{0}'.format(self.name)
        if self.project:
            url = '{0}?{1}'.format(url, urlencode(dict(project=self.project)))
        return self.client.do('GET', url, ok_error_codes=[404])

    @staticmethod
    def _profile_json_to_module_state(resp_json):
        if resp_json['type'] == 'error':
            return 'absent'
        return 'present'

    def _update_profile(self):
        if self.state == 'present':
            if self.old_state == 'absent':
                if self.new_name is None:
                    self._create_profile()
                else:
                    self.module.fail_json(
                        msg='new_name must not be set when the profile does not exist and the state is present',
                        changed=False)
            else:
                if self.new_name is not None and self.new_name != self.name:
                    self._rename_profile()
                if self._needs_to_apply_profile_configs():
                    self._apply_profile_configs()
        elif self.state == 'absent':
            if self.old_state == 'present':
                if self.new_name is None:
                    self._delete_profile()
                else:
                    self.module.fail_json(
                        msg='new_name must not be set when the profile exists and the specified state is absent',
                        changed=False)

    def _create_profile(self):
        url = '/1.0/profiles'
        if self.project:
            url = '{0}?{1}'.format(url, urlencode(dict(project=self.project)))
        config = self.config.copy()
        config['name'] = self.name
        self.client.do('POST', url, config)
        self.actions.append('create')

    def _rename_profile(self):
        url = '/1.0/profiles/{0}'.format(self.name)
        if self.project:
            url = '{0}?{1}'.format(url, urlencode(dict(project=self.project)))
        config = {'name': self.new_name}
        self.client.do('POST', url, config)
        self.actions.append('rename')
        self.name = self.new_name

    def _needs_to_change_profile_config(self, key):
        if key not in self.config:
            return False
        old_configs = self.old_profile_json['metadata'].get(key, None)
        return self.config[key] != old_configs

    def _needs_to_apply_profile_configs(self):
        return (
            self._needs_to_change_profile_config('config') or
            self._needs_to_change_profile_config('description') or
            self._needs_to_change_profile_config('devices')
        )

    def _merge_dicts(self, source, destination):
        """Merge Dictionaries

        Get a list of filehandle numbers from logger to be handed to
        DaemonContext.files_preserve

        Args:
            dict(source): source dict
            dict(destination): destination dict
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(destination): merged dict"""
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self._merge_dicts(value, node)
            else:
                destination[key] = value
        return destination

    def _merge_config(self, config):
        """ merge profile

        Merge Configuration of the present profile and the new desired configitems

        Args:
            dict(config): Dict with the old config in 'metadata' and new config in 'config'
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(config): new config"""
        # merge or copy the sections from the existing profile to 'config'
        for item in ['config', 'description', 'devices', 'name', 'used_by']:
            if item in config:
                config[item] = self._merge_dicts(config['metadata'][item], config[item])
            else:
                config[item] = config['metadata'][item]
        # merge or copy the sections from the ansible-task to 'config'
        return self._merge_dicts(self.config, config)

    def _generate_new_config(self, config):
        """ rebuild profile

        Rebuild the Profile by the configuration provided in the play.
        Existing configurations are discarded.

        This ist the default behavior.

        Args:
            dict(config): Dict with the old config in 'metadata' and new config in 'config'
        Kwargs:
            None
        Raises:
            None
        Returns:
            dict(config): new config"""
        for k, v in self.config.items():
            config[k] = v
        return config

    def _apply_profile_configs(self):
        """ Selection of the procedure: rebuild or merge

        The standard behavior is that all information not contained
        in the play is discarded.

        If "merge_profile" is provides in the play and "True", then existing
        configurations from the profile and new ones defined are merged.

        Args:
            None
        Kwargs:
            None
        Raises:
            None
        Returns:
            None"""
        config = self.old_profile_json.copy()
        if self.module.params['merge_profile']:
            config = self._merge_config(config)
        else:
            config = self._generate_new_config(config)

        # upload config to lxd
        url = '/1.0/profiles/{0}'.format(self.name)
        if self.project:
            url = '{0}?{1}'.format(url, urlencode(dict(project=self.project)))
        self.client.do('PUT', url, config)
        self.actions.append('apply_profile_configs')

    def _delete_profile(self):
        url = '/1.0/profiles/{0}'.format(self.name)
        if self.project:
            url = '{0}?{1}'.format(url, urlencode(dict(project=self.project)))
        self.client.do('DELETE', url)
        self.actions.append('delete')

    def run(self):
        """Run the main method."""

        try:
            if self.trust_password is not None:
                self.client.authenticate(self.trust_password)

            self.old_profile_json = self._get_profile_json()
            self.old_state = self._profile_json_to_module_state(self.old_profile_json)
            self._update_profile()

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
            project=dict(
                type='str',
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
            devices=dict(
                type='dict',
            ),
            merge_profile=dict(
                type='bool',
                default=False
            ),
            state=dict(
                choices=PROFILES_STATES,
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

    lxd_manage = LXDProfileManagement(module=module)
    lxd_manage.run()


if __name__ == '__main__':
    main()
