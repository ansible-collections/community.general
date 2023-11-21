#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxmox
short_description: Management of instances in Proxmox VE cluster
description:
  - allows you to create/delete/stop instances in Proxmox VE cluster
  - Starting in Ansible 2.1, it automatically detects containerization type (lxc for PVE 4, openvz for older)
  - Since community.general 4.0.0 on, there are no more default values, see O(proxmox_default_behavior).
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  password:
    description:
      - the instance root password
    type: str
  hostname:
    description:
      - the instance hostname
      - required only for O(state=present)
      - must be unique if vmid is not passed
    type: str
  ostemplate:
    description:
      - the template for VM creating
      - required only for O(state=present)
    type: str
  disk:
    description:
      - This option was previously described as "hard disk size in GB for instance" however several formats describing
        a lxc mount are permitted.
      - Older versions of Proxmox will accept a numeric value for size using the O(storage) parameter to automatically
        choose which storage to allocate from, however new versions enforce the C(<STORAGE>:<SIZE>) syntax.
      - "Additional options are available by using some combination of the following key-value pairs as a
        comma-delimited list C([volume=]<volume> [,acl=<1|0>] [,mountoptions=<opt[;opt...]>] [,quota=<1|0>]
        [,replicate=<1|0>] [,ro=<1|0>] [,shared=<1|0>] [,size=<DiskSize>])."
      - See U(https://pve.proxmox.com/wiki/Linux_Container) for a full description.
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(3).
    type: str
  cores:
    description:
      - Specify number of cores per socket.
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(1).
    type: int
  cpus:
    description:
      - numbers of allocated cpus for instance
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(1).
    type: int
  memory:
    description:
      - memory size in MB for instance
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(512).
    type: int
  swap:
    description:
      - swap memory size in MB for instance
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(0).
    type: int
  netif:
    description:
      - specifies network interfaces for the container. As a hash/dictionary defining interfaces.
    type: dict
  features:
    description:
      - Specifies a list of features to be enabled. For valid options, see U(https://pve.proxmox.com/wiki/Linux_Container#pct_options).
      - Some features require the use of a privileged container.
    type: list
    elements: str
    version_added: 2.0.0
  mounts:
    description:
      - specifies additional mounts (separate disks) for the container. As a hash/dictionary defining mount points
    type: dict
  ip_address:
    description:
      - specifies the address the container will be assigned
    type: str
  onboot:
    description:
      - specifies whether a VM will be started during system bootup
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(false).
    type: bool
  storage:
    description:
      - target storage
    type: str
    default: 'local'
  ostype:
    description:
      - Specifies the C(ostype) of the LXC container.
      - If set to V(auto), no C(ostype) will be provided on instance creation.
    choices: ['auto', 'debian', 'devuan', 'ubuntu', 'centos', 'fedora', 'opensuse', 'archlinux', 'alpine', 'gentoo', 'nixos', 'unmanaged']
    type: str
    default: 'auto'
    version_added: 8.1.0
  cpuunits:
    description:
      - CPU weight for a VM
      - This option has no default unless O(proxmox_default_behavior) is set to V(compatibility); then the default is V(1000).
    type: int
  nameserver:
    description:
      - sets DNS server IP address for a container
    type: str
  searchdomain:
    description:
      - sets DNS search domain for a container
    type: str
  tags:
    description:
      - List of tags to apply to the container.
      - Tags must start with V([a-z0-9_]) followed by zero or more of the following characters V([a-z0-9_-+.]).
      - Tags are only available in Proxmox 7+.
    type: list
    elements: str
    version_added: 6.2.0
  timeout:
    description:
      - timeout for operations
    type: int
    default: 30
  update:
    description:
      - If V(true), the container will be updated with new values.
    type: bool
    default: false
    version_added: 8.1.0
  force:
    description:
      - Forcing operations.
      - Can be used only with states V(present), V(stopped), V(restarted).
      - with O(state=present) force option allow to overwrite existing container.
      - with states V(stopped), V(restarted) allow to force stop instance.
    type: bool
    default: false
  purge:
    description:
      - Remove container from all related configurations.
      - For example backup jobs, replication jobs, or HA.
      - Related ACLs and Firewall entries will always be removed.
      - Used with O(state=absent).
    type: bool
    default: false
    version_added: 2.3.0
  state:
    description:
     - Indicate desired state of the instance
     - V(template) was added in community.general 8.1.0.
    type: str
    choices: ['present', 'started', 'absent', 'stopped', 'restarted', 'template']
    default: present
  pubkey:
    description:
      - Public key to add to /root/.ssh/authorized_keys. This was added on Proxmox 4.2, it is ignored for earlier versions
    type: str
  unprivileged:
    description:
      - Indicate if the container should be unprivileged.
      - The default change to V(true) in community.general 7.0.0. It used to be V(false) before.
    type: bool
    default: true
  description:
    description:
      - Specify the description for the container. Only used on the configuration web interface.
      - This is saved as a comment inside the configuration file.
    type: str
    version_added: '0.2.0'
  hookscript:
    description:
      - Script that will be executed during various steps in the containers lifetime.
    type: str
    version_added: '0.2.0'
  timezone:
    description:
      - Timezone used by the container, accepts values like V(Europe/Paris).
      - The special value V(host) configures the same timezone used by Proxmox host.
    type: str
    version_added: '7.1.0'
  proxmox_default_behavior:
    description:
      - As of community.general 4.0.0, various options no longer have default values.
        These default values caused problems when users expected different behavior from Proxmox
        by default or filled options which caused problems when set.
      - The value V(compatibility) (default before community.general 4.0.0) will ensure that the default values
        are used when the values are not explicitly specified by the user. The new default is V(no_defaults),
        which makes sure these options have no defaults.
      - This affects the O(disk), O(cores), O(cpus), O(memory), O(onboot), O(swap), and O(cpuunits) options.
      - >
        This parameter is now B(deprecated) and it will be removed in community.general 10.0.0.
        By then, the module's behavior should be to not set default values, equivalent to V(no_defaults).
        If a consistent set of defaults is needed, the playbook or role should be responsible for setting it.
    type: str
    default: no_defaults
    choices:
      - compatibility
      - no_defaults
    version_added: "1.3.0"
  clone:
    description:
      - ID of the container to be cloned.
      - O(description), O(hostname), and O(pool) will be copied from the cloned container if not specified.
      - The type of clone created is defined by the O(clone_type) parameter.
      - This operator is only supported for Proxmox clusters that use LXC containerization (PVE version >= 4).
    type: int
    version_added: 4.3.0
  clone_type:
    description:
      - Type of the clone created.
      - V(full) creates a full clone, and O(storage) must be specified.
      - V(linked) creates a linked clone, and the cloned container must be a template container.
      - V(opportunistic) creates a linked clone if the cloned container is a template container, and a full clone if not.
        O(storage) may be specified, if not it will fall back to the default.
    type: str
    choices: ['full', 'linked', 'opportunistic']
    default: opportunistic
    version_added: 4.3.0
author: Sergei Antipov (@UnderGreen)
seealso:
  - module: community.general.proxmox_vm_info
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.proxmox.selection
  - community.general.attributes
'''

EXAMPLES = r'''
- name: Create new container with minimal options
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'

- name: Create new container with hookscript and description
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    hookscript: 'local:snippets/vm_hook.sh'
    description: created with ansible

- name: Create new container automatically selecting the next available vmid.
  community.general.proxmox:
    node: 'uk-mc02'
    api_user: 'root@pam'
    api_password: '1q2w3e'
    api_host: 'node1'
    password: '123456'
    hostname: 'example.org'
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'

- name: Create new container with minimal options with force(it will rewrite existing container)
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    force: true

- name: Create new container with minimal options use environment PROXMOX_PASSWORD variable(you should export it before)
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'

- name: Create new container with minimal options defining network interface with dhcp
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    netif: '{"net0":"name=eth0,ip=dhcp,ip6=dhcp,bridge=vmbr0"}'

- name: Create new container with minimal options defining network interface with static ip
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    netif: '{"net0":"name=eth0,gw=192.168.0.1,ip=192.168.0.2/24,bridge=vmbr0"}'

- name: Create new container with minimal options defining a mount with 8GB
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    mounts: '{"mp0":"local:8,mp=/mnt/test/"}'

- name: Create new container with minimal options defining a cpu core limit
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    cores: 2

- name: Create new container with minimal options and same timezone as proxmox host
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    timezone: host

- name: Create a new container with nesting enabled and allows the use of CIFS/NFS inside the container.
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    features:
     - nesting=1
     - mount=cifs,nfs

- name: >
    Create a linked clone of the template container with id 100. The newly created container with be a
    linked clone, because no storage parameter is defined
  community.general.proxmox:
    vmid: 201
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    clone: 100
    hostname: clone.example.org

- name: Create a full clone of the container with id 100
  community.general.proxmox:
    vmid: 201
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    clone: 100
    hostname: clone.example.org
    storage: local

- name: Update container configuration
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    netif: '{"net0":"name=eth0,gw=192.168.0.1,ip=192.168.0.3/24,bridge=vmbr0"}'
    update: true

- name: Start container
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: started

- name: >
    Start container with mount. You should enter a 90-second timeout because servers
    with additional disks take longer to boot
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: started
    timeout: 90

- name: Stop container
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: stopped

- name: Stop container with force
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    force: true
    state: stopped

- name: Restart container(stopped or mounted container you can't restart)
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: restarted

- name: Convert container to template
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: template

- name: Convert container to template (stop container if running)
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: template
    force: true

- name: Remove container
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: absent
'''

import re
import time

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.proxmox import (
    ansible_to_proxmox_bool, proxmox_auth_argument_spec, ProxmoxAnsible)

VZ_TYPE = None


class ProxmoxLxcAnsible(ProxmoxAnsible):
    def content_check(self, node, ostemplate, template_store):
        return [True for cnt in self.proxmox_api.nodes(node).storage(template_store).content.get() if cnt['volid'] == ostemplate]

    def is_template_container(self, node, vmid):
        """Check if the specified container is a template."""
        proxmox_node = self.proxmox_api.nodes(node)
        config = getattr(proxmox_node, VZ_TYPE)(vmid).config.get()
        return config.get('template', False)

    def update_config(self, vmid, node, disk, cpus, memory, swap, **kwargs):
        if VZ_TYPE != "lxc":
            self.module.fail_json(
                changed=False,
                msg="Updating configuration is only supported for LXC enabled proxmox clusters.",
            )

        # Version limited features
        minimum_version = {"tags": "6.1", "timezone": "6.3"}
        proxmox_node = self.proxmox_api.nodes(node)

        pve_version = self.version()

        # Fail on unsupported features
        for option, version in minimum_version.items():
            if pve_version < LooseVersion(version) and option in kwargs:
                self.module.fail_json(
                    changed=False,
                    msg="Feature {option} is only supported in PVE {version}+, and you're using PVE {pve_version}".format(
                        option=option, version=version, pve_version=pve_version
                    ),
                )

        # Remove all empty kwarg entries
        kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)

        if cpus is not None:
            kwargs["cpulimit"] = cpus
        if disk is not None:
            kwargs["rootfs"] = disk
        if memory is not None:
            kwargs["memory"] = memory
        if swap is not None:
            kwargs["swap"] = swap
        if "netif" in kwargs:
            kwargs.update(kwargs["netif"])
            del kwargs["netif"]
        if "mounts" in kwargs:
            kwargs.update(kwargs["mounts"])
            del kwargs["mounts"]
        # LXC tags are expected to be valid and presented as a comma/semi-colon delimited string
        if "tags" in kwargs:
            re_tag = re.compile(r"^[a-z0-9_][a-z0-9_\-\+\.]*$")
            for tag in kwargs["tags"]:
                if not re_tag.match(tag):
                    self.module.fail_json(msg="%s is not a valid tag" % tag)
            kwargs["tags"] = ",".join(kwargs["tags"])

        # fetch the current config
        current_config = getattr(proxmox_node, VZ_TYPE)(vmid).config.get()

        # compare the requested config against the current
        update_config = False
        for (arg, value) in kwargs.items():
            # some values are lists, the order isn't always the same, so split them and compare by key
            if isinstance(value, str):
                current_values = current_config[arg].split(",")
                requested_values = value.split(",")
                for new_value in requested_values:
                    if new_value not in current_values:
                        update_config = True
                        break
            # if it's not a list (or string) just compare the current value
            else:
                # some types don't match with the API, so forcing to string for comparison
                if str(value) != str(current_config[arg]):
                    update_config = True
                    break

        if update_config:
            getattr(proxmox_node, VZ_TYPE)(vmid).config.put(vmid=vmid, node=node, **kwargs)
        else:
            self.module.exit_json(changed=False, msg="Container config is already up to date")

    def create_instance(self, vmid, node, disk, storage, cpus, memory, swap, timeout, clone, **kwargs):

        # Version limited features
        minimum_version = {
            'tags': '6.1',
            'timezone': '6.3'
        }
        proxmox_node = self.proxmox_api.nodes(node)

        # Remove all empty kwarg entries
        kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)

        pve_version = self.version()

        # Fail on unsupported features
        for option, version in minimum_version.items():
            if pve_version < LooseVersion(version) and option in kwargs:
                self.module.fail_json(changed=False, msg="Feature {option} is only supported in PVE {version}+, and you're using PVE {pve_version}".
                                      format(option=option, version=version, pve_version=pve_version))

        if VZ_TYPE == 'lxc':
            kwargs['cpulimit'] = cpus
            kwargs['rootfs'] = disk
            if 'netif' in kwargs:
                kwargs.update(kwargs['netif'])
                del kwargs['netif']
            if 'mounts' in kwargs:
                kwargs.update(kwargs['mounts'])
                del kwargs['mounts']
            if 'pubkey' in kwargs:
                if self.version() >= LooseVersion('4.2'):
                    kwargs['ssh-public-keys'] = kwargs['pubkey']
                del kwargs['pubkey']
        else:
            kwargs['cpus'] = cpus
            kwargs['disk'] = disk

        # LXC tags are expected to be valid and presented as a comma/semi-colon delimited string
        if 'tags' in kwargs:
            re_tag = re.compile(r'^[a-z0-9_][a-z0-9_\-\+\.]*$')
            for tag in kwargs['tags']:
                if not re_tag.match(tag):
                    self.module.fail_json(msg='%s is not a valid tag' % tag)
            kwargs['tags'] = ",".join(kwargs['tags'])

        if kwargs.get('ostype') == 'auto':
            kwargs.pop('ostype')

        if clone is not None:
            if VZ_TYPE != 'lxc':
                self.module.fail_json(changed=False, msg="Clone operator is only supported for LXC enabled proxmox clusters.")

            clone_is_template = self.is_template_container(node, clone)

            # By default, create a full copy only when the cloned container is not a template.
            create_full_copy = not clone_is_template

            # Only accept parameters that are compatible with the clone endpoint.
            valid_clone_parameters = ['hostname', 'pool', 'description']
            if self.module.params['storage'] is not None and clone_is_template:
                # Cloning a template, so create a full copy instead of a linked copy
                create_full_copy = True
            elif self.module.params['storage'] is None and not clone_is_template:
                # Not cloning a template, but also no defined storage. This isn't possible.
                self.module.fail_json(changed=False, msg="Cloned container is not a template, storage needs to be specified.")

            if self.module.params['clone_type'] == 'linked':
                if not clone_is_template:
                    self.module.fail_json(changed=False, msg="'linked' clone type is specified, but cloned container is not a template container.")
                # Don't need to do more, by default create_full_copy is set to false already
            elif self.module.params['clone_type'] == 'opportunistic':
                if not clone_is_template:
                    # Cloned container is not a template, so we need our 'storage' parameter
                    valid_clone_parameters.append('storage')
            elif self.module.params['clone_type'] == 'full':
                create_full_copy = True
                valid_clone_parameters.append('storage')

            clone_parameters = {}

            if create_full_copy:
                clone_parameters['full'] = '1'
            else:
                clone_parameters['full'] = '0'
            for param in valid_clone_parameters:
                if self.module.params[param] is not None:
                    clone_parameters[param] = self.module.params[param]

            taskid = getattr(proxmox_node, VZ_TYPE)(clone).clone.post(newid=vmid, **clone_parameters)
        else:
            taskid = getattr(proxmox_node, VZ_TYPE).create(vmid=vmid, storage=storage, memory=memory, swap=swap, **kwargs)

        while timeout:
            if self.api_task_ok(node, taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(vmid=vmid, node=node, msg='Reached timeout while waiting for creating VM. Last line in task before timeout: %s' %
                                      proxmox_node.tasks(taskid).log.get()[:1])

            time.sleep(1)
        return False

    def start_instance(self, vm, vmid, timeout):
        taskid = getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.start.post()
        while timeout:
            if self.api_task_ok(vm['node'], taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(vmid=vmid, taskid=taskid, msg='Reached timeout while waiting for starting VM. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
        return False

    def stop_instance(self, vm, vmid, timeout, force):
        if force:
            taskid = getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.shutdown.post(forceStop=1)
        else:
            taskid = getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.shutdown.post()
        while timeout:
            if self.api_task_ok(vm['node'], taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(vmid=vmid, taskid=taskid, msg='Reached timeout while waiting for stopping VM. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
        return False

    def convert_to_template(self, vm, vmid, timeout, force):
        if getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'running' and force:
            self.stop_instance(vm, vmid, timeout, force)
        # not sure why, but templating a container doesn't return a taskid
        getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).template.post()
        return True

    def umount_instance(self, vm, vmid, timeout):
        taskid = getattr(self.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.umount.post()
        while timeout:
            if self.api_task_ok(vm['node'], taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.module.fail_json(vmid=vmid, taskid=taskid, msg='Reached timeout while waiting for unmounting VM. Last line in task before timeout: %s' %
                                      self.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

            time.sleep(1)
        return False


def main():
    module_args = proxmox_auth_argument_spec()
    proxmox_args = dict(
        vmid=dict(type='int', required=False),
        node=dict(),
        pool=dict(),
        password=dict(no_log=True),
        hostname=dict(),
        ostemplate=dict(),
        disk=dict(type='str'),
        cores=dict(type='int'),
        cpus=dict(type='int'),
        memory=dict(type='int'),
        swap=dict(type='int'),
        netif=dict(type='dict'),
        mounts=dict(type='dict'),
        ip_address=dict(),
        ostype=dict(default='auto', choices=[
            'auto', 'debian', 'devuan', 'ubuntu', 'centos', 'fedora', 'opensuse', 'archlinux', 'alpine', 'gentoo', 'nixos', 'unmanaged'
        ]),
        onboot=dict(type='bool'),
        features=dict(type='list', elements='str'),
        storage=dict(default='local'),
        cpuunits=dict(type='int'),
        nameserver=dict(),
        searchdomain=dict(),
        timeout=dict(type='int', default=30),
        update=dict(type='bool', default=False),
        force=dict(type='bool', default=False),
        purge=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent', 'stopped', 'started', 'restarted', 'template']),
        pubkey=dict(type='str'),
        unprivileged=dict(type='bool', default=True),
        description=dict(type='str'),
        hookscript=dict(type='str'),
        timezone=dict(type='str'),
        proxmox_default_behavior=dict(type='str', default='no_defaults', choices=['compatibility', 'no_defaults'],
                                      removed_in_version='9.0.0', removed_from_collection='community.general'),
        clone=dict(type='int'),
        clone_type=dict(default='opportunistic', choices=['full', 'linked', 'opportunistic']),
        tags=dict(type='list', elements='str')
    )
    module_args.update(proxmox_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ('state', 'present', ['node', 'hostname']),
            # Require one of clone, ostemplate, or update. Together with mutually_exclusive this ensures that we
            # either clone a container or create a new one from a template file.
            ('state', 'present', ('clone', 'ostemplate', 'update'), True),
        ],
        required_together=[
            ('api_token_id', 'api_token_secret')
        ],
        required_one_of=[('api_password', 'api_token_id')],
        mutually_exclusive=[('clone', 'ostemplate', 'update')],  # Creating a new container is done either by cloning an existing one, or based on a template.
    )

    proxmox = ProxmoxLxcAnsible(module)

    global VZ_TYPE
    VZ_TYPE = 'openvz' if proxmox.version() < LooseVersion('4.0') else 'lxc'

    state = module.params['state']
    vmid = module.params['vmid']
    node = module.params['node']
    disk = module.params['disk']
    cpus = module.params['cpus']
    memory = module.params['memory']
    swap = module.params['swap']
    storage = module.params['storage']
    hostname = module.params['hostname']
    if module.params['ostemplate'] is not None:
        template_store = module.params['ostemplate'].split(":")[0]
    timeout = module.params['timeout']
    clone = module.params['clone']

    if module.params['proxmox_default_behavior'] == 'compatibility':
        old_default_values = dict(
            disk="3",
            cores=1,
            cpus=1,
            memory=512,
            swap=0,
            onboot=False,
            cpuunits=1000,
        )
        for param, value in old_default_values.items():
            if module.params[param] is None:
                module.params[param] = value

    # If vmid not set get the Next VM id from ProxmoxAPI
    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and state == 'present':
        vmid = proxmox.get_nextvmid()
    elif not vmid and hostname:
        vmid = proxmox.get_vmid(hostname)
    elif not vmid:
        module.exit_json(changed=False, msg="Vmid could not be fetched for the following action: %s" % state)

    # Create a new container
    if state == 'present' and clone is None:
        try:
            if proxmox.get_vm(vmid, ignore_missing=True):
                if module.params["update"]:
                    try:
                        proxmox.update_config(vmid, node, disk, cpus, memory, swap,
                                              cores=module.params["cores"],
                                              hostname=module.params["hostname"],
                                              netif=module.params["netif"],
                                              mounts=module.params["mounts"],
                                              ip_address=module.params["ip_address"],
                                              onboot=ansible_to_proxmox_bool(module.params["onboot"]),
                                              cpuunits=module.params["cpuunits"],
                                              nameserver=module.params["nameserver"],
                                              searchdomain=module.params["searchdomain"],
                                              features=",".join(module.params["features"])
                                              if module.params["features"] is not None
                                              else None,
                                              description=module.params["description"],
                                              hookscript=module.params["hookscript"],
                                              timezone=module.params["timezone"],
                                              tags=module.params["tags"])
                        module.exit_json(
                            changed=True,
                            vmid=vmid,
                            msg="Configured VM %s" % (vmid),
                        )
                    except Exception as e:
                        module.fail_json(
                            vmid=vmid,
                            msg="Configuration of %s VM %s failed with exception: %s"
                            % (VZ_TYPE, vmid, e),
                        )
                if not module.params["force"]:
                    module.exit_json(
                        changed=False,
                        vmid=vmid,
                        msg="VM with vmid = %s is already exists" % vmid,
                    )
            # If no vmid was passed, there cannot be another VM named 'hostname'
            if (not module.params['vmid'] and
                    proxmox.get_vmid(hostname, ignore_missing=True) and
                    not module.params['force']):
                vmid = proxmox.get_vmid(hostname)
                module.exit_json(changed=False, vmid=vmid, msg="VM with hostname %s already exists and has ID number %s" % (hostname, vmid))
            elif not proxmox.get_node(node):
                module.fail_json(vmid=vmid, msg="node '%s' not exists in cluster" % node)
            elif not proxmox.content_check(node, module.params['ostemplate'], template_store):
                module.fail_json(vmid=vmid, msg="ostemplate '%s' not exists on node %s and storage %s"
                                 % (module.params['ostemplate'], node, template_store))
        except Exception as e:
            module.fail_json(vmid=vmid, msg="Pre-creation checks of {VZ_TYPE} VM {vmid} failed with exception: {e}".format(VZ_TYPE=VZ_TYPE, vmid=vmid, e=e))

        try:
            proxmox.create_instance(vmid, node, disk, storage, cpus, memory, swap, timeout, clone,
                                    cores=module.params['cores'],
                                    pool=module.params['pool'],
                                    password=module.params['password'],
                                    hostname=module.params['hostname'],
                                    ostemplate=module.params['ostemplate'],
                                    netif=module.params['netif'],
                                    mounts=module.params['mounts'],
                                    ostype=module.params['ostype'],
                                    ip_address=module.params['ip_address'],
                                    onboot=ansible_to_proxmox_bool(module.params['onboot']),
                                    cpuunits=module.params['cpuunits'],
                                    nameserver=module.params['nameserver'],
                                    searchdomain=module.params['searchdomain'],
                                    force=ansible_to_proxmox_bool(module.params['force']),
                                    pubkey=module.params['pubkey'],
                                    features=",".join(module.params['features']) if module.params['features'] is not None else None,
                                    unprivileged=ansible_to_proxmox_bool(module.params['unprivileged']),
                                    description=module.params['description'],
                                    hookscript=module.params['hookscript'],
                                    timezone=module.params['timezone'],
                                    tags=module.params['tags'])

            module.exit_json(changed=True, vmid=vmid, msg="Deployed VM %s from template %s" % (vmid, module.params['ostemplate']))
        except Exception as e:
            module.fail_json(vmid=vmid, msg="Creation of %s VM %s failed with exception: %s" % (VZ_TYPE, vmid, e))

    # Clone a container
    elif state == 'present' and clone is not None:
        try:
            if proxmox.get_vm(vmid, ignore_missing=True) and not module.params['force']:
                module.exit_json(changed=False, vmid=vmid, msg="VM with vmid = %s is already exists" % vmid)
            # If no vmid was passed, there cannot be another VM named 'hostname'
            if (not module.params['vmid'] and
                    proxmox.get_vmid(hostname, ignore_missing=True) and
                    not module.params['force']):
                vmid = proxmox.get_vmid(hostname)
                module.exit_json(changed=False, vmid=vmid, msg="VM with hostname %s already exists and has ID number %s" % (hostname, vmid))
            if not proxmox.get_vm(clone, ignore_missing=True):
                module.exit_json(changed=False, vmid=vmid, msg="Container to be cloned does not exist")
        except Exception as e:
            module.fail_json(vmid=vmid, msg="Pre-clone checks of {VZ_TYPE} VM {vmid} failed with exception: {e}".format(VZ_TYPE=VZ_TYPE, vmid=vmid, e=e))

        try:
            proxmox.create_instance(vmid, node, disk, storage, cpus, memory, swap, timeout, clone)

            module.exit_json(changed=True, vmid=vmid, msg="Cloned VM %s from %s" % (vmid, clone))
        except Exception as e:
            module.fail_json(vmid=vmid, msg="Cloning %s VM %s failed with exception: %s" % (VZ_TYPE, vmid, e))

    elif state == 'started':
        try:
            vm = proxmox.get_vm(vmid)
            if getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'running':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is already running" % vmid)

            if proxmox.start_instance(vm, vmid, timeout):
                module.exit_json(changed=True, vmid=vmid, msg="VM %s started" % vmid)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="starting of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'stopped':
        try:
            vm = proxmox.get_vm(vmid)

            if getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'mounted':
                if module.params['force']:
                    if proxmox.umount_instance(vm, vmid, timeout):
                        module.exit_json(changed=True, vmid=vmid, msg="VM %s is shutting down" % vmid)
                else:
                    module.exit_json(changed=False, vmid=vmid,
                                     msg=("VM %s is already shutdown, but mounted. You can use force option to umount it.") % vmid)

            if getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'stopped':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is already shutdown" % vmid)

            if proxmox.stop_instance(vm, vmid, timeout, force=module.params['force']):
                module.exit_json(changed=True, vmid=vmid, msg="VM %s is shutting down" % vmid)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="stopping of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'template':
        try:
            vm = proxmox.get_vm(vmid)

            proxmox.convert_to_template(vm, vmid, timeout, force=module.params['force'])
            module.exit_json(changed=True, msg="VM %s is converted to template" % vmid)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="conversion of VM %s to template failed with exception: %s" % (vmid, e))

    elif state == 'restarted':
        try:
            vm = proxmox.get_vm(vmid)

            vm_status = getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status']
            if vm_status in ['stopped', 'mounted']:
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is not running" % vmid)

            if (proxmox.stop_instance(vm, vmid, timeout, force=module.params['force']) and
                    proxmox.start_instance(vm, vmid, timeout)):
                module.exit_json(changed=True, vmid=vmid, msg="VM %s is restarted" % vmid)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="restarting of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'absent':
        if not vmid:
            module.exit_json(changed=False, vmid=vmid, msg='VM with hostname = %s is already absent' % hostname)
        try:
            vm = proxmox.get_vm(vmid, ignore_missing=True)
            if not vm:
                module.exit_json(changed=False, vmid=vmid, msg="VM %s does not exist" % vmid)

            vm_status = getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE)(vmid).status.current.get()['status']
            if vm_status == 'running':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is running. Stop it before deletion." % vmid)

            if vm_status == 'mounted':
                module.exit_json(changed=False, vmid=vmid, msg="VM %s is mounted. Stop it with force option before deletion." % vmid)

            delete_params = {}

            if module.params['purge']:
                delete_params['purge'] = 1

            taskid = getattr(proxmox.proxmox_api.nodes(vm['node']), VZ_TYPE).delete(vmid, **delete_params)

            while timeout:
                if proxmox.api_task_ok(vm['node'], taskid):
                    module.exit_json(changed=True, vmid=vmid, taskid=taskid, msg="VM %s removed" % vmid)
                timeout -= 1
                if timeout == 0:
                    module.fail_json(vmid=vmid, taskid=taskid, msg='Reached timeout while waiting for removing VM. Last line in task before timeout: %s'
                                     % proxmox.proxmox_api.nodes(vm['node']).tasks(taskid).log.get()[:1])

                time.sleep(1)
        except Exception as e:
            module.fail_json(vmid=vmid, msg="deletion of VM %s failed with exception: %s" % (vmid, to_native(e)))


if __name__ == '__main__':
    main()
