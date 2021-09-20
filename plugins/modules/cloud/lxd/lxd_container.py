#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Hiroaki Nakamura <hnakamur@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: lxd_container
short_description: Manage LXD Containers
description:
  - Management of LXD containers
author: "Hiroaki Nakamura (@hnakamur)"
options:
    name:
        description:
          - Name of a container.
        type: str
        required: true
    architecture:
        description:
          - The architecture for the container (e.g. "x86_64" or "i686").
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1)
        type: str
        required: false
    config:
        description:
          - 'The config for the container (e.g. {"limits.cpu": "2"}).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1)'
          - If the container already exists and its "config" values in metadata
            obtained from GET /1.0/containers/<name>
            U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#10containersname)
            are different, this module tries to apply the configurations.
          - The keys starting with C(volatile.) are ignored for this comparison when I(ignore_volatile_options=true).
        type: dict
        required: false
    ignore_volatile_options:
        description:
          - If set to C(true), options starting with C(volatile.) are ignored. As a result,
            they are reapplied for each execution.
          - This default behavior can be changed by setting this option to C(false).
          - The default value C(true) will be deprecated in community.general 4.0.0,
            and will change to C(false) in community.general 5.0.0.
        type: bool
        default: true
        required: false
        version_added: 3.7.0
    profiles:
        description:
          - Profile to be used by the container
        type: list
        elements: str
    devices:
        description:
          - 'The devices for the container
            (e.g. { "rootfs": { "path": "/dev/kvm", "type": "unix-char" }).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1)'
        type: dict
        required: false
    ephemeral:
        description:
          - Whether or not the container is ephemeral (e.g. true or false).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1)
        required: false
        type: bool
    source:
        description:
          - 'The source for the container
            (e.g. { "type": "image",
                    "mode": "pull",
                    "server": "https://images.linuxcontainers.org",
                    "protocol": "lxd",
                    "alias": "ubuntu/xenial/amd64" }).'
          - 'See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1) for complete API documentation.'
          - 'Note that C(protocol) accepts two choices: C(lxd) or C(simplestreams)'
        required: false
        type: dict
    state:
        choices:
          - started
          - stopped
          - restarted
          - absent
          - frozen
        description:
          - Define the state of a container.
        required: false
        default: started
        type: str
    target:
        description:
          - For cluster deployments. Will attempt to create a container on a target node.
            If container exists elsewhere in a cluster, then container will not be replaced or moved.
            The name should respond to same name of the node you see in C(lxc cluster list).
        type: str
        required: false
        version_added: 1.0.0
    timeout:
        description:
          - A timeout for changing the state of the container.
          - This is also used as a timeout for waiting until IPv4 addresses
            are set to the all network interfaces in the container after
            starting or restarting.
        required: false
        default: 30
        type: int
    wait_for_ipv4_addresses:
        description:
          - If this is true, the C(lxd_container) waits until IPv4 addresses
            are set to the all network interfaces in the container after
            starting or restarting.
        required: false
        default: false
        type: bool
    force_stop:
        description:
          - If this is true, the C(lxd_container) forces to stop the container
            when it stops or restarts the container.
        required: false
        default: false
        type: bool
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
          - If not specified, it defaults to C(${HOME}/.config/lxc/client.key).
        required: false
        aliases: [ key_file ]
        type: path
    client_cert:
        description:
          - The client certificate file path.
          - If not specified, it defaults to C(${HOME}/.config/lxc/client.crt).
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
  - Containers must have a unique name. If you attempt to create a container
    with a name that already existed in the users namespace the module will
    simply return as "unchanged".
  - There are two ways to run commands in containers, using the command
    module or using the ansible lxd connection plugin bundled in Ansible >=
    2.1, the later requires python to be installed in the container which can
    be done with the command module.
  - You can copy a file from the host to the container
    with the Ansible M(ansible.builtin.copy) and M(ansible.builtin.template) module and the `lxd` connection plugin.
    See the example below.
  - You can copy a file in the created container to the localhost
    with `command=lxc file pull container_name/dir/filename filename`.
    See the first example below.
'''

EXAMPLES = '''
# An example for creating a Ubuntu container and install python
- hosts: localhost
  connection: local
  tasks:
    - name: Create a started container
      community.general.lxd_container:
        name: mycontainer
        ignore_volatile_options: true
        state: started
        source:
          type: image
          mode: pull
          server: https://images.linuxcontainers.org
          protocol: lxd # if you get a 404, try setting protocol: simplestreams
          alias: ubuntu/xenial/amd64
        profiles: ["default"]
        wait_for_ipv4_addresses: true
        timeout: 600

    - name: Check python is installed in container
      delegate_to: mycontainer
      ansible.builtin.raw: dpkg -s python
      register: python_install_check
      failed_when: python_install_check.rc not in [0, 1]
      changed_when: false

    - name: Install python in container
      delegate_to: mycontainer
      ansible.builtin.raw: apt-get install -y python
      when: python_install_check.rc == 1

# An example for creating an Ubuntu 14.04 container using an image fingerprint.
# This requires changing 'server' and 'protocol' key values, replacing the
# 'alias' key with with 'fingerprint' and supplying an appropriate value that
# matches the container image you wish to use.
- hosts: localhost
  connection: local
  tasks:
    - name: Create a started container
      community.general.lxd_container:
        name: mycontainer
        ignore_volatile_options: true
        state: started
        source:
          type: image
          mode: pull
          # Provides current (and older) Ubuntu images with listed fingerprints
          server: https://cloud-images.ubuntu.com/releases
          # Protocol used by 'ubuntu' remote (as shown by 'lxc remote list')
          protocol: simplestreams
          # This provides an Ubuntu 14.04 LTS amd64 image from 20150814.
          fingerprint: e9a8bdfab6dc
        profiles: ["default"]
        wait_for_ipv4_addresses: true
        timeout: 600

# An example for deleting a container
- hosts: localhost
  connection: local
  tasks:
    - name: Delete a container
      community.general.lxd_container:
        name: mycontainer
        state: absent

# An example for restarting a container
- hosts: localhost
  connection: local
  tasks:
    - name: Restart a container
      community.general.lxd_container:
        name: mycontainer
        state: restarted

# An example for restarting a container using https to connect to the LXD server
- hosts: localhost
  connection: local
  tasks:
    - name: Restart a container
      community.general.lxd_container:
        url: https://127.0.0.1:8443
        # These client_cert and client_key values are equal to the default values.
        #client_cert: "{{ lookup('env', 'HOME') }}/.config/lxc/client.crt"
        #client_key: "{{ lookup('env', 'HOME') }}/.config/lxc/client.key"
        trust_password: mypassword
        name: mycontainer
        state: restarted

# Note your container must be in the inventory for the below example.
#
# [containers]
# mycontainer ansible_connection=lxd
#
- hosts:
    - mycontainer
  tasks:
    - name: Copy /etc/hosts in the created container to localhost with name "mycontainer-hosts"
      ansible.builtin.fetch:
        src: /etc/hosts
        dest: /tmp/mycontainer-hosts
        flat: true

# An example for LXD cluster deployments. This example will create two new container on specific
# nodes - 'node01' and 'node02'. In 'target:', 'node01' and 'node02' are names of LXD cluster
# members that LXD cluster recognizes, not ansible inventory names, see: 'lxc cluster list'.
# LXD API calls can be made to any LXD member, in this example, we send API requests to
#'node01.example.com', which matches ansible inventory name.
- hosts: node01.example.com
  tasks:
    - name: Create LXD container
      community.general.lxd_container:
        name: new-container-1
        ignore_volatile_options: true
        state: started
        source:
          type: image
          mode: pull
          alias: ubuntu/xenial/amd64
        target: node01

    - name: Create container on another node
      community.general.lxd_container:
        name: new-container-2
        ignore_volatile_options: true
        state: started
        source:
          type: image
          mode: pull
          alias: ubuntu/xenial/amd64
        target: node02
'''

RETURN = '''
addresses:
  description: Mapping from the network device name to a list of IPv4 addresses in the container
  returned: when state is started or restarted
  type: dict
  sample: {"eth0": ["10.155.92.191"]}
old_state:
  description: The old state of the container
  returned: when state is started or restarted
  type: str
  sample: "stopped"
logs:
  description: The logs of requests and responses.
  returned: when ansible-playbook is invoked with -vvvv.
  type: list
  sample: "(too long to be placed here)"
actions:
  description: List of actions performed for the container.
  returned: success
  type: list
  sample: '["create", "start"]'
'''
import datetime
import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.lxd import LXDClient, LXDClientException
from ansible.module_utils.six.moves.urllib.parse import urlencode

# LXD_ANSIBLE_STATES is a map of states that contain values of methods used
# when a particular state is evoked.
LXD_ANSIBLE_STATES = {
    'started': '_started',
    'stopped': '_stopped',
    'restarted': '_restarted',
    'absent': '_destroyed',
    'frozen': '_frozen'
}

# ANSIBLE_LXD_STATES is a map of states of lxd containers to the Ansible
# lxc_container module state parameter value.
ANSIBLE_LXD_STATES = {
    'Running': 'started',
    'Stopped': 'stopped',
    'Frozen': 'frozen',
}

# ANSIBLE_LXD_DEFAULT_URL is a default value of the lxd endpoint
ANSIBLE_LXD_DEFAULT_URL = 'unix:/var/lib/lxd/unix.socket'

# CONFIG_PARAMS is a list of config attribute names.
CONFIG_PARAMS = [
    'architecture', 'config', 'devices', 'ephemeral', 'profiles', 'source'
]


class LXDContainerManagement(object):
    def __init__(self, module):
        """Management of LXC containers via Ansible.

        :param module: Processed Ansible Module.
        :type module: ``object``
        """
        self.module = module
        self.name = self.module.params['name']
        self._build_config()

        self.state = self.module.params['state']

        self.timeout = self.module.params['timeout']
        self.wait_for_ipv4_addresses = self.module.params['wait_for_ipv4_addresses']
        self.force_stop = self.module.params['force_stop']
        self.addresses = None
        self.target = self.module.params['target']

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

    def _get_container_json(self):
        return self.client.do(
            'GET', '/1.0/containers/{0}'.format(self.name),
            ok_error_codes=[404]
        )

    def _get_container_state_json(self):
        return self.client.do(
            'GET', '/1.0/containers/{0}/state'.format(self.name),
            ok_error_codes=[404]
        )

    @staticmethod
    def _container_json_to_module_state(resp_json):
        if resp_json['type'] == 'error':
            return 'absent'
        return ANSIBLE_LXD_STATES[resp_json['metadata']['status']]

    def _change_state(self, action, force_stop=False):
        body_json = {'action': action, 'timeout': self.timeout}
        if force_stop:
            body_json['force'] = True
        return self.client.do('PUT', '/1.0/containers/{0}/state'.format(self.name), body_json=body_json)

    def _create_container(self):
        config = self.config.copy()
        config['name'] = self.name
        if self.target:
            self.client.do('POST', '/1.0/containers?' + urlencode(dict(target=self.target)), config)
        else:
            self.client.do('POST', '/1.0/containers', config)
        self.actions.append('create')

    def _start_container(self):
        self._change_state('start')
        self.actions.append('start')

    def _stop_container(self):
        self._change_state('stop', self.force_stop)
        self.actions.append('stop')

    def _restart_container(self):
        self._change_state('restart', self.force_stop)
        self.actions.append('restart')

    def _delete_container(self):
        self.client.do('DELETE', '/1.0/containers/{0}'.format(self.name))
        self.actions.append('delete')

    def _freeze_container(self):
        self._change_state('freeze')
        self.actions.append('freeze')

    def _unfreeze_container(self):
        self._change_state('unfreeze')
        self.actions.append('unfreez')

    def _container_ipv4_addresses(self, ignore_devices=None):
        ignore_devices = ['lo'] if ignore_devices is None else ignore_devices

        resp_json = self._get_container_state_json()
        network = resp_json['metadata']['network'] or {}
        network = dict((k, v) for k, v in network.items() if k not in ignore_devices) or {}
        addresses = dict((k, [a['address'] for a in v['addresses'] if a['family'] == 'inet']) for k, v in network.items()) or {}
        return addresses

    @staticmethod
    def _has_all_ipv4_addresses(addresses):
        return len(addresses) > 0 and all(len(v) > 0 for v in addresses.values())

    def _get_addresses(self):
        try:
            due = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)
            while datetime.datetime.now() < due:
                time.sleep(1)
                addresses = self._container_ipv4_addresses()
                if self._has_all_ipv4_addresses(addresses):
                    self.addresses = addresses
                    return
        except LXDClientException as e:
            e.msg = 'timeout for getting IPv4 addresses'
            raise

    def _started(self):
        if self.old_state == 'absent':
            self._create_container()
            self._start_container()
        else:
            if self.old_state == 'frozen':
                self._unfreeze_container()
            elif self.old_state == 'stopped':
                self._start_container()
            if self._needs_to_apply_container_configs():
                self._apply_container_configs()
        if self.wait_for_ipv4_addresses:
            self._get_addresses()

    def _stopped(self):
        if self.old_state == 'absent':
            self._create_container()
        else:
            if self.old_state == 'stopped':
                if self._needs_to_apply_container_configs():
                    self._start_container()
                    self._apply_container_configs()
                    self._stop_container()
            else:
                if self.old_state == 'frozen':
                    self._unfreeze_container()
                if self._needs_to_apply_container_configs():
                    self._apply_container_configs()
                self._stop_container()

    def _restarted(self):
        if self.old_state == 'absent':
            self._create_container()
            self._start_container()
        else:
            if self.old_state == 'frozen':
                self._unfreeze_container()
            if self._needs_to_apply_container_configs():
                self._apply_container_configs()
            self._restart_container()
        if self.wait_for_ipv4_addresses:
            self._get_addresses()

    def _destroyed(self):
        if self.old_state != 'absent':
            if self.old_state == 'frozen':
                self._unfreeze_container()
            if self.old_state != 'stopped':
                self._stop_container()
            self._delete_container()

    def _frozen(self):
        if self.old_state == 'absent':
            self._create_container()
            self._start_container()
            self._freeze_container()
        else:
            if self.old_state == 'stopped':
                self._start_container()
            if self._needs_to_apply_container_configs():
                self._apply_container_configs()
            self._freeze_container()

    def _needs_to_change_container_config(self, key):
        if key not in self.config:
            return False
        if key == 'config' and self.ignore_volatile_options:  # the old behavior is to ignore configurations by keyword "volatile"
            old_configs = dict((k, v) for k, v in self.old_container_json['metadata'][key].items() if not k.startswith('volatile.'))
            for k, v in self.config['config'].items():
                if k not in old_configs:
                    return True
                if old_configs[k] != v:
                    return True
            return False
        elif key == 'config':  # next default behavior
            old_configs = dict((k, v) for k, v in self.old_container_json['metadata'][key].items())
            for k, v in self.config['config'].items():
                if k not in old_configs:
                    return True
                if old_configs[k] != v:
                    return True
            return False
        else:
            old_configs = self.old_container_json['metadata'][key]
            return self.config[key] != old_configs

    def _needs_to_apply_container_configs(self):
        return (
            self._needs_to_change_container_config('architecture') or
            self._needs_to_change_container_config('config') or
            self._needs_to_change_container_config('ephemeral') or
            self._needs_to_change_container_config('devices') or
            self._needs_to_change_container_config('profiles')
        )

    def _apply_container_configs(self):
        old_metadata = self.old_container_json['metadata']
        body_json = {
            'architecture': old_metadata['architecture'],
            'config': old_metadata['config'],
            'devices': old_metadata['devices'],
            'profiles': old_metadata['profiles']
        }
        if self._needs_to_change_container_config('architecture'):
            body_json['architecture'] = self.config['architecture']
        if self._needs_to_change_container_config('config'):
            for k, v in self.config['config'].items():
                body_json['config'][k] = v
        if self._needs_to_change_container_config('ephemeral'):
            body_json['ephemeral'] = self.config['ephemeral']
        if self._needs_to_change_container_config('devices'):
            body_json['devices'] = self.config['devices']
        if self._needs_to_change_container_config('profiles'):
            body_json['profiles'] = self.config['profiles']
        self.client.do('PUT', '/1.0/containers/{0}'.format(self.name), body_json=body_json)
        self.actions.append('apply_container_configs')

    def run(self):
        """Run the main method."""

        try:
            if self.trust_password is not None:
                self.client.authenticate(self.trust_password)
            self.ignore_volatile_options = self.module.params.get('ignore_volatile_options')

            self.old_container_json = self._get_container_json()
            self.old_state = self._container_json_to_module_state(self.old_container_json)
            action = getattr(self, LXD_ANSIBLE_STATES[self.state])
            action()

            state_changed = len(self.actions) > 0
            result_json = {
                'log_verbosity': self.module._verbosity,
                'changed': state_changed,
                'old_state': self.old_state,
                'actions': self.actions
            }
            if self.client.debug:
                result_json['logs'] = self.client.logs
            if self.addresses is not None:
                result_json['addresses'] = self.addresses
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
            architecture=dict(
                type='str',
            ),
            config=dict(
                type='dict',
            ),
            ignore_volatile_options=dict(
                type='bool',
                default=True
            ),
            devices=dict(
                type='dict',
            ),
            ephemeral=dict(
                type='bool',
            ),
            profiles=dict(
                type='list',
                elements='str',
            ),
            source=dict(
                type='dict',
            ),
            state=dict(
                choices=list(LXD_ANSIBLE_STATES.keys()),
                default='started'
            ),
            target=dict(
                type='str',
            ),
            timeout=dict(
                type='int',
                default=30
            ),
            wait_for_ipv4_addresses=dict(
                type='bool',
                default=False
            ),
            force_stop=dict(
                type='bool',
                default=False
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
    # if module.params['ignore_volatile_options'] is None:
    #     module.params['ignore_volatile_options'] = True
    #     module.deprecate(
    #         'If the keyword "volatile" is used in a playbook in the config section, a
    #         "changed" message will appear with every run, even without a change to the playbook.
    #         This will change in the future.
    #         Please test your scripts by "ignore_volatile_options: false"', version='5.0.0', collection_name='community.general')
    lxd_manage = LXDContainerManagement(module=module)
    lxd_manage.run()


if __name__ == '__main__':
    main()
