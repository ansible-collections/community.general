#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Hiroaki Nakamura <hnakamur@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: lxd_container
short_description: Manage LXD instances
description:
  - Management of LXD containers and virtual machines.
author: "Hiroaki Nakamura (@hnakamur)"
options:
    name:
        description:
          - Name of an instance.
        type: str
        required: true
    project:
        description:
          - 'Project of an instance.
            See U(https://github.com/lxc/lxd/blob/master/doc/projects.md).'
        required: false
        type: str
        version_added: 4.8.0
    architecture:
        description:
          - 'The architecture for the instance (for example C(x86_64) or C(i686)).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1).'
        type: str
        required: false
    config:
        description:
          - 'The config for the instance (for example C({"limits.cpu": "2"})).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1).'
          - If the instance already exists and its "config" values in metadata
            obtained from the LXD API U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#instances-containers-and-virtual-machines)
            are different, this module tries to apply the configurations.
          - The keys starting with C(volatile.) are ignored for this comparison when I(ignore_volatile_options=true).
        type: dict
        required: false
    ignore_volatile_options:
        description:
          - If set to C(true), options starting with C(volatile.) are ignored. As a result,
            they are reapplied for each execution.
          - This default behavior can be changed by setting this option to C(false).
          - The default value changed from C(true) to C(false) in community.general 6.0.0.
        type: bool
        required: false
        default: false
        version_added: 3.7.0
    profiles:
        description:
          - Profile to be used by the instance.
        type: list
        elements: str
    devices:
        description:
          - 'The devices for the instance
            (for example C({ "rootfs": { "path": "/dev/kvm", "type": "unix-char" }})).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1).'
        type: dict
        required: false
    ephemeral:
        description:
          - Whether or not the instance is ephemeral (for example C(true) or C(false)).
            See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1).
        required: false
        type: bool
    source:
        description:
          - 'The source for the instance
            (e.g. { "type": "image",
                    "mode": "pull",
                    "server": "https://images.linuxcontainers.org",
                    "protocol": "lxd",
                    "alias": "ubuntu/xenial/amd64" }).'
          - 'See U(https://github.com/lxc/lxd/blob/master/doc/rest-api.md#post-1) for complete API documentation.'
          - 'Note that C(protocol) accepts two choices: C(lxd) or C(simplestreams).'
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
          - Define the state of an instance.
        required: false
        default: started
        type: str
    target:
        description:
          - For cluster deployments. Will attempt to create an instance on a target node.
            If the instance exists elsewhere in a cluster, then it will not be replaced or moved.
            The name should respond to same name of the node you see in C(lxc cluster list).
        type: str
        required: false
        version_added: 1.0.0
    timeout:
        description:
          - A timeout for changing the state of the instance.
          - This is also used as a timeout for waiting until IPv4 addresses
            are set to the all network interfaces in the instance after
            starting or restarting.
        required: false
        default: 30
        type: int
    type:
        description:
          - Instance type can be either C(virtual-machine) or C(container).
        required: false
        default: container
        choices:
          - container
          - virtual-machine
        type: str
        version_added: 4.1.0
    wait_for_ipv4_addresses:
        description:
          - If this is true, the C(lxd_container) waits until IPv4 addresses
            are set to the all network interfaces in the instance after
            starting or restarting.
        required: false
        default: false
        type: bool
    wait_for_container:
        description:
            - If set to C(true), the tasks will wait till the task reports a
              success status when performing container operations.
        default: false
        type: bool
        version_added: 4.4.0
    force_stop:
        description:
          - If this is true, the C(lxd_container) forces to stop the instance
            when it stops or restarts the instance.
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
          - 'You need to set this password on the LXD server before
            running this module using the following command:
            C(lxc config set core.trust_password <some random password>).
            See U(https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/).'
          - If trust_password is set, this module send a request for
            authentication before sending any requests.
        required: false
        type: str
notes:
  - Instances can be a container or a virtual machine, both of them must have unique name. If you attempt to create an instance
    with a name that already existed in the users namespace the module will
    simply return as "unchanged".
  - There are two ways to run commands inside a container or virtual machine, using the command
    module or using the ansible lxd connection plugin bundled in Ansible >=
    2.1, the later requires python to be installed in the instance which can
    be done with the command module.
  - You can copy a file from the host to the instance
    with the Ansible M(ansible.builtin.copy) and M(ansible.builtin.template) module and the C(community.general.lxd) connection plugin.
    See the example below.
  - You can copy a file in the created instance to the localhost
    with C(command=lxc file pull instance_name/dir/filename filename).
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

# An example for creating container in project other than default
- hosts: localhost
  connection: local
  tasks:
    - name: Create a started container in project mytestproject
      community.general.lxd_container:
        name: mycontainer
        project: mytestproject
        ignore_volatile_options: true
        state: started
        source:
          protocol: simplestreams
          type: image
          mode: pull
          server: https://images.linuxcontainers.org
          alias: ubuntu/20.04/cloud
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
        type: container

# An example for restarting a container
- hosts: localhost
  connection: local
  tasks:
    - name: Restart a container
      community.general.lxd_container:
        name: mycontainer
        state: restarted
        type: container

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

# An example for creating a virtual machine
- hosts: localhost
  connection: local
  tasks:
    - name: Create container on another node
      community.general.lxd_container:
        name: new-vm-1
        type: virtual-machine
        state: started
        ignore_volatile_options: true
        wait_for_ipv4_addresses: true
        profiles: ["default"]
        source:
          protocol: simplestreams
          type: image
          mode: pull
          server: https://images.linuxcontainers.org
          alias: debian/11
        timeout: 600
'''

RETURN = '''
addresses:
  description: Mapping from the network device name to a list of IPv4 addresses in the instance.
  returned: when state is started or restarted
  type: dict
  sample: {"eth0": ["10.155.92.191"]}
old_state:
  description: The old state of the instance.
  returned: when state is started or restarted
  type: str
  sample: "stopped"
logs:
  description: The logs of requests and responses.
  returned: when ansible-playbook is invoked with -vvvv.
  type: list
  sample: "(too long to be placed here)"
actions:
  description: List of actions performed for the instance.
  returned: success
  type: list
  sample: ["create", "start"]
'''
import datetime
import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.lxd import pylxd_client, LXDClientException
from pylxd.exceptions import NotFound


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
        self.project = self.module.params['project']
        self._build_config()

        self.state = self.module.params['state']

        self.timeout = self.module.params['timeout']
        self.wait_for_ipv4_addresses = self.module.params['wait_for_ipv4_addresses']
        self.force_stop = self.module.params['force_stop']
        self.addresses = None
        self.target = self.module.params['target']
        self.wait_for_container = self.module.params['wait_for_container']
        self.ignore_volatile_options = self.module.params.get('ignore_volatile_options')

        self.type = self.module.params['type']

        self.client_key = self.module.params.get('client_key')
        self.client_cert = self.module.params.get('client_cert')
        self.trust_password = self.module.params.get('trust_password', None)
        self.verify = self.module.params.get('verify')

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
            self.client = pylxd_client(
                endpoint=self.url,
                client_cert=self.client_cert,
                client_key=self.client_key,
                password=self.trust_password,
                project=self.project,
                timeout=self.timeout,
                verify=self.verify,
            )
        except LXDClientException as e:
            self.module.fail_json(msg=e.msg)

        self.actions = []

    def _build_config(self):
        self.config = {}
        for attr in CONFIG_PARAMS:
            param_val = self.module.params.get(attr, None)
            if param_val is not None:
                self.config[attr] = param_val

    def _create_instance(self):
        config = self.config.copy()
        config['name'] = self.name

        match self.type:
            case 'container':
                self.instance = self.client.containers.create(config=config, wait=True, target=self.target)
            case 'virtual-machine':
                self.instance = self.client.virtual_machines.create(config=config, wait=True, target=self.target)

# TODO: Re-add wait_for_container via stuff from Client.do() in pxd.py? Or just use/hijack the wait parameter above?

        self.actions.append('create')

    def _start_instance(self):
        self.instance.start(wait=True)
        self.actions.append('start')

    def _stop_instance(self):
        self.instance.stop(wait=True, force=self.force_stop)
        self.actions.append('stop')

    def _restart_instance(self):
        self.instance.restart(wait=True, force=self.force_stop)
        self.actions.append('restart')

    def _delete_instance(self):
        self.instance.delete(wait=True)
        self.actions.append('delete')

    def _freeze_instance(self):
        self.instance.freeze(wait=True)
        self.actions.append('freeze')

    def _unfreeze_instance(self):
        self.instance.unfreeze(wait=True)
        self.actions.append('unfreez')

    def _instance_ipv4_addresses(self, ignore_devices=None):
        ignore_devices = ['lo'] if ignore_devices is None else ignore_devices

        resp_json = self.client.api.instances[self.name].state.get().json()
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
                addresses = self._instance_ipv4_addresses()
                if self._has_all_ipv4_addresses(addresses):
                    self.addresses = addresses
                    return
        except LXDClientException as e:
            e.msg = 'timeout for getting IPv4 addresses'
            raise

    def _started(self):
        if self.old_state == 'absent':
            self._create_instance()
            self._start_instance()
        else:
            if self.old_state == 'frozen':
                self._unfreeze_instance()
            elif self.old_state == 'stopped':
                self._start_instance()
            if self._needs_to_apply_instance_configs():
                self._apply_instance_configs()
        if self.wait_for_ipv4_addresses:
            self._get_addresses()

    def _stopped(self):
        if self.old_state == 'absent':
            self._create_instance()
        else:
            if self.old_state == 'stopped':
                if self._needs_to_apply_instance_configs():
                    self._start_instance()
                    self._apply_instance_configs()
                    self._stop_instance()
            else:
                if self.old_state == 'frozen':
                    self._unfreeze_instance()
                if self._needs_to_apply_instance_configs():
                    self._apply_instance_configs()
                self._stop_instance()

    def _restarted(self):
        if self.old_state == 'absent':
            self._create_instance()
            self._start_instance()
        else:
            if self.old_state == 'frozen':
                self._unfreeze_instance()
            if self._needs_to_apply_instance_configs():
                self._apply_instance_configs()
            self._restart_instance()
        if self.wait_for_ipv4_addresses:
            self._get_addresses()

    def _destroyed(self):
        if self.old_state != 'absent':
            if self.old_state == 'frozen':
                self._unfreeze_instance()
            if self.old_state != 'stopped':
                self._stop_instance()
            self._delete_instance()

    def _frozen(self):
        if self.old_state == 'absent':
            self._create_instance()
            self._start_instance()
            self._freeze_instance()
        else:
            if self.old_state == 'stopped':
                self._start_instance()
            if self._needs_to_apply_instance_configs():
                self._apply_instance_configs()
            self._freeze_instance()

    def _needs_to_change_instance_config(self, key):
        if key not in self.config:
            return False
        if key == 'config' and self.ignore_volatile_options:  # the old behavior is to ignore configurations by keyword "volatile"
            old_configs = dict((k, v) for k, v in self.old_instance_json['metadata'][key].items() if not k.startswith('volatile.'))
            for k, v in self.config['config'].items():
                if k not in old_configs:
                    return True
                if old_configs[k] != v:
                    return True
            return False
        elif key == 'config':  # next default behavior
            old_configs = dict((k, v) for k, v in self.old_instance_json['metadata'][key].items())
            for k, v in self.config['config'].items():
                if k not in old_configs:
                    return True
                if old_configs[k] != v:
                    return True
            return False
        else:
            old_configs = self.old_instance_json['metadata'][key]
            return self.config[key] != old_configs

    def _needs_to_apply_instance_configs(self):
        return (
            self._needs_to_change_instance_config('architecture') or
            self._needs_to_change_instance_config('config') or
            self._needs_to_change_instance_config('ephemeral') or
            self._needs_to_change_instance_config('devices') or
            self._needs_to_change_instance_config('profiles')
        )

    def _apply_instance_configs(self):
        old_metadata = self.old_instance_json['metadata']
        body_json = {
            'architecture': old_metadata['architecture'],
            'config': old_metadata['config'],
            'devices': old_metadata['devices'],
            'profiles': old_metadata['profiles']
        }

        if self._needs_to_change_instance_config('architecture'):
            body_json['architecture'] = self.config['architecture']
        if self._needs_to_change_instance_config('config'):
            for k, v in self.config['config'].items():
                body_json['config'][k] = v
        if self._needs_to_change_instance_config('ephemeral'):
            body_json['ephemeral'] = self.config['ephemeral']
        if self._needs_to_change_instance_config('devices'):
            body_json['devices'] = self.config['devices']
        if self._needs_to_change_instance_config('profiles'):
            body_json['profiles'] = self.config['profiles']

        self.instance.api.put(json=body_json)
        self.actions.append('apply_instance_configs')

    def run(self):
        """Run the main method."""

        try:
            try:
                match self.type:
                    case 'container':
                        self.instance = self.client.containers.get(self.name)
                    case 'virtual-machine':
                        self.instance = self.client.virtual_machines.get(self.name)

                self.old_instance_json = self.client.api.instances[self.name].get().json()

            except NotFound:
                self.instance = None
                self.old_instance_json = {'metadata': {}}

            self.old_state = ANSIBLE_LXD_STATES[self.instance.status] if self.instance else 'absent'

            action = getattr(self, LXD_ANSIBLE_STATES[self.state])
            action()

            state_changed = len(self.actions) > 0
            result_json = {
                'log_verbosity': self.module._verbosity,
                'changed': state_changed,
                'old_state': self.old_state,
                'actions': self.actions
            }
# TODO: Is such logging needed at all when using the pylxd library
            if self.debug:
                # Provide a dummy log event
                result_json['logs'] = ['(Currently no client logging after switch to pylxd)']
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
            if self.debug:
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
            architecture=dict(
                type='str',
            ),
            config=dict(
                type='dict',
            ),
            ignore_volatile_options=dict(
                type='bool',
                default=False,
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
            type=dict(
                type='str',
                default='container',
                choices=['container', 'virtual-machine'],
            ),
            wait_for_container=dict(
                type='bool',
                default=False
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
                default=ANSIBLE_LXD_DEFAULT_URL,
                aliasses=['endpoint']
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
            verify=dict(
                type='bool',
                default=True
            ),
            trust_password=dict(type='str', no_log=True)
        ),
        supports_check_mode=False,
    )

    lxd_manage = LXDContainerManagement(module=module)
    lxd_manage.run()


if __name__ == '__main__':
    main()
