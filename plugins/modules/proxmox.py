#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: proxmox
short_description: Management of instances in Proxmox VE cluster
description:
  - Allows you to create/delete/stop instances in Proxmox VE cluster.
  - The module automatically detects containerization type (lxc for PVE 4, openvz for older).
  - Since community.general 4.0.0 on, there are no more default values.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
  action_group:
    version_added: 9.0.0
options:
  password:
    description:
      - The instance root password.
    type: str
  hostname:
    description:
      - The instance hostname.
      - Required only for O(state=present).
      - Must be unique if vmid is not passed.
    type: str
  ostemplate:
    description:
      - The template for VM creating.
      - Required only for O(state=present).
    type: str
  disk:
    description:
      - This option was previously described as "hard disk size in GB for instance" however several formats describing a lxc
        mount are permitted.
      - Older versions of Proxmox will accept a numeric value for size using the O(storage) parameter to automatically choose
        which storage to allocate from, however new versions enforce the C(<STORAGE>:<SIZE>) syntax.
      - Additional options are available by using some combination of the following key-value pairs as a comma-delimited list
        C([volume=]<volume>
        [,acl=<1|0>] [,mountoptions=<opt[;opt...] [,quota=<1|0>] [,replicate=<1|0>] [,ro=<1|0>] [,shared=<1|0>]
        [,size=<DiskSize>]).
      - See U(https://pve.proxmox.com/wiki/Linux_Container) for a full description.
      - This option is mutually exclusive with O(disk_volume).
    type: str
  disk_volume:
    description:
      - Specify a hash/dictionary of the C(rootfs) disk.
      - See U(https://pve.proxmox.com/wiki/Linux_Container#pct_mount_points) for a full description.
      - This option is mutually exclusive with O(storage) and O(disk).
    type: dict
    version_added: 9.2.0
    suboptions:
      storage:
        description:
          - O(disk_volume.storage) is the storage identifier of the storage to use for the C(rootfs).
          - Mutually exclusive with O(disk_volume.host_path).
        type: str
      volume:
        description:
          - O(disk_volume.volume) is the name of an existing volume.
          - If not defined, the module will check if one exists. If not, a new volume will be created.
          - If defined, the volume must exist under that name.
          - Required only if O(disk_volume.storage) is defined, and mutually exclusive with O(disk_volume.host_path).
        type: str
      size:
        description:
          - O(disk_volume.size) is the size of the storage to use.
          - The size is given in GiB.
          - Required only if O(disk_volume.storage) is defined, and mutually exclusive with O(disk_volume.host_path).
        type: int
      host_path:
        description:
          - O(disk_volume.host_path) defines a bind or device path on the PVE host to use for the C(rootfs).
          - Mutually exclusive with O(disk_volume.storage), O(disk_volume.volume), and O(disk_volume.size).
        type: path
      options:
        description:
          - O(disk_volume.options) is a dict of extra options.
          - The value of any given option must be a string, for example V("1").
        type: dict
  cores:
    description:
      - Specify number of cores per socket.
    type: int
  cpus:
    description:
      - Number of allocated cpus for instance.
    type: int
  memory:
    description:
      - Memory size in MB for instance.
    type: int
  swap:
    description:
      - Swap memory size in MB for instance.
    type: int
  netif:
    description:
      - Specifies network interfaces for the container. As a hash/dictionary defining interfaces.
    type: dict
  features:
    description:
      - Specifies a list of features to be enabled. For valid options, see U(https://pve.proxmox.com/wiki/Linux_Container#pct_options).
      - Some features require the use of a privileged container.
    type: list
    elements: str
    version_added: 2.0.0
  startup:
    description:
      - Specifies the startup order of the container.
      - Use C(order=#) where C(#) is a non-negative number to define the general startup order. Shutdown in done with reverse
        ordering.
      - Use C(up=#) where C(#) is in seconds, to specify a delay to wait before the next VM is started.
      - Use C(down=#) where C(#) is in seconds, to specify a delay to wait before the next VM is stopped.
    type: list
    elements: str
    version_added: 8.5.0
  mounts:
    description:
      - Specifies additional mounts (separate disks) for the container. As a hash/dictionary defining mount points as strings.
      - This Option is mutually exclusive with O(mount_volumes).
    type: dict
  mount_volumes:
    description:
      - Specify additional mounts (separate disks) for the container. As a hash/dictionary defining mount points.
      - See U(https://pve.proxmox.com/wiki/Linux_Container#pct_mount_points) for a full description.
      - This Option is mutually exclusive with O(mounts).
    type: list
    elements: dict
    version_added: 9.2.0
    suboptions:
      id:
        description:
          - O(mount_volumes[].id) is the identifier of the mount point written as C(mp[n]).
        type: str
        required: true
      storage:
        description:
          - O(mount_volumes[].storage) is the storage identifier of the storage to use.
          - Mutually exclusive with O(mount_volumes[].host_path).
        type: str
      volume:
        description:
          - O(mount_volumes[].volume) is the name of an existing volume.
          - If not defined, the module will check if one exists. If not, a new volume will be created.
          - If defined, the volume must exist under that name.
          - Required only if O(mount_volumes[].storage) is defined and mutually exclusive with O(mount_volumes[].host_path).
        type: str
      size:
        description:
          - O(mount_volumes[].size) is the size of the storage to use.
          - The size is given in GiB.
          - Required only if O(mount_volumes[].storage) is defined and mutually exclusive with O(mount_volumes[].host_path).
        type: int
      host_path:
        description:
          - O(mount_volumes[].host_path) defines a bind or device path on the PVE host to use for the C(rootfs).
          - Mutually exclusive with O(mount_volumes[].storage), O(mount_volumes[].volume), and O(mount_volumes[].size).
        type: path
      mountpoint:
        description:
          - O(mount_volumes[].mountpoint) is the mount point of the volume.
        type: path
        required: true
      options:
        description:
          - O(mount_volumes[].options) is a dict of extra options.
          - The value of any given option must be a string, for example V("1").
        type: dict
  ip_address:
    description:
      - Specifies the address the container will be assigned.
    type: str
  onboot:
    description:
      - Specifies whether a VM will be started during system bootup.
    type: bool
  storage:
    description:
      - Target storage.
      - This option is mutually exclusive with O(disk_volume) and O(mount_volumes).
    type: str
    default: 'local'
  ostype:
    description:
      - Specifies the C(ostype) of the LXC container.
      - If set to V(auto), no C(ostype) will be provided on instance creation.
    choices: ['auto', 'debian', 'devuan', 'ubuntu', 'centos', 'fedora', 'opensuse', 'archlinux', 'alpine', 'gentoo', 'nixos',
      'unmanaged']
    type: str
    default: 'auto'
    version_added: 8.1.0
  cpuunits:
    description:
      - CPU weight for a VM.
    type: int
  nameserver:
    description:
      - Sets DNS server IP address for a container.
    type: str
  searchdomain:
    description:
      - Sets DNS search domain for a container.
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
      - Timeout for operations.
    type: int
    default: 30
  update:
    description:
      - If V(true), the container will be updated with new values.
      - The current default value of V(false) is deprecated and should will change to V(true) in community.general 11.0.0.
        Please set O(update) explicitly to V(false) or V(true) to avoid surprises and get rid of the deprecation warning.
    type: bool
    version_added: 8.1.0
  force:
    description:
      - Forcing operations.
      - Can be used only with states V(present), V(stopped), V(restarted).
      - With O(state=present) force option allow to overwrite existing container.
      - With states V(stopped), V(restarted) allow to force stop instance.
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
      - Indicate desired state of the instance.
      - V(template) was added in community.general 8.1.0.
    type: str
    choices: ['present', 'started', 'absent', 'stopped', 'restarted', 'template']
    default: present
  pubkey:
    description:
      - Public key to add to /root/.ssh/authorized_keys. This was added on Proxmox 4.2, it is ignored for earlier versions.
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
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.proxmox.selection
  - community.general.attributes
"""

EXAMPLES = r"""
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

- name: Create new container with minimal options specifying disk storage location and size
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    disk: 'local-lvm:20'

- name: Create new container with minimal options specifying disk storage location and size via disk_volume
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    disk_volume:
      storage: local
      size: 20

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
    netif:
      net0: "name=eth0,ip=dhcp,ip6=dhcp,bridge=vmbr0"

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
    netif:
      net0: "name=eth0,gw=192.168.0.1,ip=192.168.0.2/24,bridge=vmbr0"

- name: Create new container with more options defining network interface with static ip4 and ip6 with vlan-tag and mtu
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    netif:
      net0: "name=eth0,gw=192.168.0.1,ip=192.168.0.2/24,ip6=fe80::1227/64,gw6=fe80::1,bridge=vmbr0,firewall=1,tag=934,mtu=1500"

- name: Create new container with minimal options defining a mount with 8GB
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    mounts:
      mp0: "local:8,mp=/mnt/test/"

- name: Create new container with minimal options defining a mount with 8GB using mount_volumes
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
    mount_volumes:
      - id: mp0
        storage: local
        size: 8
        mountpoint: /mnt/test

- name: Create new container with minimal options defining a cpu core limit
  community.general.proxmox:
    vmid: 100
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    password: 123456
    hostname: example.org
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
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
    ostemplate: 'local:vztmpl/ubuntu-14.04-x86_64.tar.gz'
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
    netif:
      net0: "name=eth0,gw=192.168.0.1,ip=192.168.0.3/24,bridge=vmbr0"
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
"""

import re
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    ProxmoxAnsible,
    ansible_to_proxmox_bool,
    proxmox_auth_argument_spec,
)
from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


def get_proxmox_args():
    return dict(
        vmid=dict(type="int", required=False),
        node=dict(),
        pool=dict(),
        password=dict(no_log=True),
        hostname=dict(),
        ostemplate=dict(),
        disk=dict(type="str"),
        disk_volume=dict(
            type="dict",
            options=dict(
                storage=dict(type="str"),
                volume=dict(type="str"),
                size=dict(type="int"),
                host_path=dict(type="path"),
                options=dict(type="dict"),
            ),
            required_together=[("storage", "size")],
            required_by={
                "volume": ("storage", "size"),
            },
            mutually_exclusive=[
                ("host_path", "storage"),
                ("host_path", "volume"),
                ("host_path", "size"),
            ],
        ),
        cores=dict(type="int"),
        cpus=dict(type="int"),
        memory=dict(type="int"),
        swap=dict(type="int"),
        netif=dict(type="dict"),
        mounts=dict(type="dict"),
        mount_volumes=dict(
            type="list",
            elements="dict",
            options=dict(
                id=(dict(type="str", required=True)),
                storage=dict(type="str"),
                volume=dict(type="str"),
                size=dict(type="int"),
                host_path=dict(type="path"),
                mountpoint=dict(type="path", required=True),
                options=dict(type="dict"),
            ),
            required_together=[("storage", "size")],
            required_by={
                "volume": ("storage", "size"),
            },
            mutually_exclusive=[
                ("host_path", "storage"),
                ("host_path", "volume"),
                ("host_path", "size"),
            ],
        ),
        ip_address=dict(),
        ostype=dict(
            default="auto",
            choices=[
                "auto",
                "debian",
                "devuan",
                "ubuntu",
                "centos",
                "fedora",
                "opensuse",
                "archlinux",
                "alpine",
                "gentoo",
                "nixos",
                "unmanaged",
            ],
        ),
        onboot=dict(type="bool"),
        features=dict(type="list", elements="str"),
        startup=dict(type="list", elements="str"),
        storage=dict(default="local"),
        cpuunits=dict(type="int"),
        nameserver=dict(),
        searchdomain=dict(),
        timeout=dict(type="int", default=30),
        update=dict(type="bool"),
        force=dict(type="bool", default=False),
        purge=dict(type="bool", default=False),
        state=dict(
            default="present",
            choices=[
                "present",
                "absent",
                "stopped",
                "started",
                "restarted",
                "template",
            ],
        ),
        pubkey=dict(type="str"),
        unprivileged=dict(type="bool", default=True),
        description=dict(type="str"),
        hookscript=dict(type="str"),
        timezone=dict(type="str"),
        clone=dict(type="int"),
        clone_type=dict(
            default="opportunistic", choices=["full", "linked", "opportunistic"]
        ),
        tags=dict(type="list", elements="str"),
    )


def get_ansible_module():
    module_args = proxmox_auth_argument_spec()
    module_args.update(get_proxmox_args())

    return AnsibleModule(
        argument_spec=module_args,
        required_if=[
            ("state", "present", ["node", "hostname"]),
            # Require one of clone, ostemplate, or update.
            # Together with mutually_exclusive this ensures that we either
            # clone a container or create a new one from a template file.
            ("state", "present", ("clone", "ostemplate", "update"), True),
        ],
        required_together=[("api_token_id", "api_token_secret")],
        required_one_of=[
            ("api_password", "api_token_id"),
            ("vmid", "hostname"),
        ],
        mutually_exclusive=[
            # Creating a new container is done either by cloning an existing one, or based on a template.
            ("clone", "ostemplate", "update"),
            ("disk", "disk_volume"),
            ("storage", "disk_volume"),
            ("mounts", "mount_volumes"),
        ],
    )


class ProxmoxLxcAnsible(ProxmoxAnsible):
    MINIMUM_VERSIONS = {
        "disk_volume": "5.0",
        "mount_volumes": "5.0",
        "tags": "6.1",
        "timezone": "6.3",
    }

    def __init__(self, module):
        super(ProxmoxLxcAnsible, self).__init__(module)

        self.VZ_TYPE = "openvz" if self.version() < LooseVersion("4.0") else "lxc"
        self.params = self.module.params

    def run(self):
        self.check_supported_features()

        state = self.params.get("state")

        vmid = self.params.get("vmid")
        hostname = self.params.get("hostname")

        if not vmid and not hostname:
            self.module.fail_json(msg="Either VMID or hostname must be provided.")

        if state == "present":
            self.lxc_present(
                vmid,
                hostname,
                node=self.params.get("node"),
                update=self.params.get("update"),
                force=self.params.get("force"),
            )
        elif state == "absent":
            self.lxc_absent(
                vmid,
                hostname,
                node=self.params.get("node"),
                timeout=self.params.get("timeout"),
                purge=self.params.get("purge"),
            )
        elif state == "started":
            self.lxc_started(
                vmid,
                hostname,
                node=self.params.get("node"),
                timeout=self.params.get("timeout"),
            )
        elif state == "stopped":
            self.lxc_stopped(
                vmid,
                hostname,
                node=self.params.get("node"),
                timeout=self.params.get("timeout"),
                force=self.params.get("force"),
            )
        elif state == "restarted":
            self.lxc_restarted(
                vmid,
                hostname,
                node=self.params.get("node"),
                timeout=self.params.get("timeout"),
                force=self.params.get("force"),
            )
        elif state == "template":
            self.lxc_to_template(
                vmid,
                hostname,
                node=self.params.get("node"),
                timeout=self.params.get("timeout"),
                force=self.params.get("force"),
            )

    def lxc_present(self, vmid, hostname, node, update, force):
        try:
            lxc = self.get_lxc_resource(vmid, hostname)
            vmid = vmid or lxc["id"].split("/")[-1]
            node = node or lxc["node"]
        except LookupError:
            lxc = None
            vmid = vmid or self.get_nextvmid()

        if node is None:
            raise ValueError(
                "Argument 'node' is None, but should be found from VMID/hostname or provided."
            )

        # check if the container exists already
        if lxc is not None:
            if update is None:
                # TODO: Remove deprecation warning in version 11.0.0
                self.module.deprecate(
                    msg="The default value of false for 'update' has been deprecated and will be changed to true in version 11.0.0.",
                    version="11.0.0",
                    collection_name="community.general",
                )
                update = False

            if update:
                # Update it if we should
                identifier = self.format_vm_identifier(vmid, hostname)
                self.update_lxc_instance(
                    vmid,
                    node,
                    cores=self.params.get("cores"),
                    cpus=self.params.get("cpus"),
                    cpuunits=self.params.get("cpuunits"),
                    description=self.params.get("description"),
                    disk=self.params.get("disk"),
                    disk_volume=self.params.get("disk_volume"),
                    features=self.params.get("features"),
                    hookscript=self.params.get("hookscript"),
                    hostname=self.params.get("hostname"),
                    ip_address=self.params.get("ip_address"),
                    memory=self.params.get("memory"),
                    mounts=self.params.get("mounts"),
                    mount_volumes=self.params.get("mount_volumes"),
                    nameserver=self.params.get("nameserver"),
                    netif=self.params.get("netif"),
                    onboot=ansible_to_proxmox_bool(self.params.get("onboot")),
                    searchdomain=self.params.get("searchdomain"),
                    startup=self.params.get("startup"),
                    swap=self.params.get("swap"),
                    tags=self.params.get("tags"),
                    timezone=self.params.get("timezone"),
                )
                self.module.exit_json(
                    changed=True, vmid=vmid, msg="VM %s has been updated." % identifier
                )
            elif not force:
                # We're done if it shouldn't be forcefully created
                identifier = self.format_vm_identifier(vmid, lxc["name"])
                self.module.exit_json(
                    changed=False, vmid=vmid, msg="VM %s already exists." % identifier
                )
            identifier = self.format_vm_identifier(vmid, lxc["name"])
            self.module.debug(
                "VM %s already exists, but we don't update and instead forcefully recreate it."
                % identifier
            )

        self.new_lxc_instance(
            vmid,
            hostname,
            node=self.params.get("node"),
            clone_from=self.params.get("clone"),
            ostemplate=self.params.get("ostemplate"),
            force=force,
        )

    def lxc_absent(self, vmid, hostname, node, timeout, purge):
        try:
            lxc = self.get_lxc_resource(vmid, hostname)
        except LookupError:
            identifier = self.format_vm_identifier(vmid, hostname)
            self.module.exit_json(
                changed=False, vmid=vmid, msg="VM %s is already absent." % (identifier)
            )

        vmid = vmid or lxc["id"].split("/")[-1]
        node = node or lxc["node"]

        lxc_status = self.get_lxc_status(vmid, node)
        identifier = self.format_vm_identifier(vmid, hostname)

        if lxc_status == "running":
            self.module.exit_json(
                changed=False,
                vmid=vmid,
                msg="VM %s is running. Stop it before deletion." % identifier,
            )
        if lxc_status == "mounted":
            self.module.exit_json(
                changed=False,
                vmid=vmid,
                msg="VM %s is mounted. Stop it with force option before deletion."
                % identifier,
            )

        self.remove_lxc_instance(vmid, node, timeout, purge)
        self.module.exit_json(
            changed=True, vmid=vmid, msg="VM %s removed." % identifier
        )

    def lxc_started(self, vmid, hostname, node, timeout):
        lxc = self.get_lxc_resource(vmid, hostname)
        vmid = vmid or lxc["id"].split("/")[-1]
        hostname = hostname or lxc["name"]
        identifier = self.format_vm_identifier(vmid, hostname)
        node = node or lxc["node"]
        lxc_status = self.get_lxc_status(vmid, lxc["node"])

        if lxc_status == "running":
            self.module.exit_json(
                changed=False, vmid=vmid, msg="VM %s is already running." % identifier
            )

        self.start_lxc_instance(vmid, node, timeout)
        self.module.exit_json(
            changed=True, vmid=vmid, msg="VM %s started." % identifier
        )

    def lxc_stopped(self, vmid, hostname, node, timeout, force):
        lxc = self.get_lxc_resource(vmid, hostname)
        vmid = vmid or lxc["id"].split("/")[-1]
        hostname = hostname or lxc["name"]
        identifier = self.format_vm_identifier(vmid, hostname)
        node = node or lxc["node"]
        lxc_status = self.get_lxc_status(vmid, node)

        if lxc_status == "mounted":
            if force:
                self.umount_lxc_instance(vmid, hostname, timeout)
            else:
                self.module.exit_json(
                    changed=False,
                    vmid=vmid,
                    msg="VM %s is already stopped, but mounted. Use force option to umount it."
                    % identifier,
                )

        if lxc_status == "stopped":
            self.module.exit_json(
                changed=False, vmid=vmid, msg="VM %s is already stopped." % identifier
            )

        self.stop_lxc_instance(vmid, node, timeout, force)
        self.module.exit_json(
            changed=True, vmid=vmid, msg="VM %s stopped." % identifier
        )

    def lxc_restarted(self, vmid, hostname, node, timeout, force):
        lxc = self.get_lxc_resource(vmid, hostname)

        vmid = vmid or lxc["id"].split("/")[-1]
        hostname = hostname or lxc["name"]
        node = node or lxc["node"]

        identifier = self.format_vm_identifier(vmid, hostname)
        lxc_status = self.get_lxc_status(vmid, node)

        if lxc_status in ["stopped", "mounted"]:
            self.module.exit_json(
                changed=False, vmid=vmid, msg="VM %s is not running." % identifier
            )

        self.stop_lxc_instance(vmid, node, timeout, force)
        self.start_lxc_instance(vmid, node, timeout)
        self.module.exit_json(
            changed=True, vmid=vmid, msg="VM %s is restarted." % identifier
        )

    def lxc_to_template(self, vmid, hostname, node, timeout, force):
        lxc = self.get_lxc_resource(vmid, hostname)
        vmid = vmid or lxc["id"].split("/")[-1]
        hostname = hostname or lxc["name"]
        node = node or lxc["node"]
        identifier = self.format_vm_identifier(vmid, hostname)

        if self.is_template_container(node, vmid):
            self.module.exit_json(
                changed=False,
                vmid=vmid,
                msg="VM %s is already a template." % identifier,
            )

        lxc_status = self.get_lxc_status(vmid, node)
        if lxc_status == "running" and force:
            self.stop_instance(vmid, hostname, node, timeout, force)

        proxmox_node = self.proxmox_api.nodes(node)
        getattr(proxmox_node, self.VZ_TYPE)(vmid).template.post()
        self.module.exit_json(
            changed=True, vmid=vmid, msg="VM %s converted to template." % identifier
        )

    def update_lxc_instance(self, vmid, node, **kwargs):
        if self.VZ_TYPE != "lxc":
            self.module.fail_json(
                msg="Updating LXC containers is only supported for LXC-enabled clusters in PVE 4.0 and above."
            )

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        self.validate_tags(kwargs.get("tags", []))

        if "features" in kwargs:
            kwargs["features"] = ",".join(kwargs.pop("features"))
        if "startup" in kwargs:
            kwargs["startup"] = ",".join(kwargs.pop("startup"))

        disk_updates = self.process_disk_keys(
            vmid,
            node,
            kwargs.pop("disk", None),
            kwargs.pop("disk_volume", None),
        )
        mounts_updates = self.process_mount_keys(
            vmid,
            node,
            kwargs.pop("mounts", None),
            kwargs.pop("mount_volumes", None),
        )
        kwargs.update(disk_updates)
        kwargs.update(mounts_updates)

        if "cpus" in kwargs:
            kwargs["cpulimit"] = kwargs.pop("cpus")
        if "netif" in kwargs:
            kwargs.update(kwargs.pop("netif"))

        if "pubkey" in kwargs:
            pubkey = kwargs.pop("pubkey")
            if self.version() >= LooseVersion("4.2"):
                kwargs["ssh-public-keys"] = pubkey
            else:
                self.module.warn(
                    "'pubkey' is not supported for PVE 4.1 and below. Ignoring keyword."
                )

        # fetch current config
        proxmox_node = self.proxmox_api.nodes(node)
        current_config = getattr(proxmox_node, self.VZ_TYPE)(vmid).config.get()

        # create diff between the current and requested config
        diff = {}
        for arg, value in kwargs.items():
            # if the arg isn't in the current config, it needs to be added
            if arg not in current_config:
                diff[arg] = value
            elif isinstance(value, str):
                # compare all string values as lists as some of them may be lists separated by commas. order doesn't matter
                current_values = current_config[arg].split(",")
                requested_values = value.split(",")
                for new_value in requested_values:
                    if new_value not in current_values:
                        diff[arg] = value
                        break
            # if it's not a list (or string) just compare the values
            # some types don't match with the API, so force a string comparison
            elif str(value) != str(current_config[arg]):
                diff[arg] = value

        if not diff:
            self.module.exit_json(
                changed=False, vmid=vmid, msg="Container config is already up to date."
            )

        # update the config
        getattr(proxmox_node, self.VZ_TYPE)(vmid).config.put(
            vmid=vmid, node=node, **kwargs
        )

    def new_lxc_instance(self, vmid, hostname, node, clone_from, ostemplate, force):
        identifier = self.format_vm_identifier(vmid, hostname)

        if clone_from is not None:
            self.clone_lxc_instance(
                vmid,
                node,
                clone_from,
                clone_type=self.params.get("clone_type"),
                timeout=self.params.get("timeout"),
                description=self.params.get("description"),
                hostname=hostname,
                pool=self.params.get("pool"),
                storage=self.params.get("storage"),
            )
            self.module.exit_json(
                changed=True,
                vmid=vmid,
                msg="Cloned VM %s from %d" % (identifier, clone_from),
            )

        if ostemplate is not None:
            self.create_lxc_instance(
                vmid,
                node,
                ostemplate,
                timeout=self.params.get("timeout"),
                cores=self.params.get("cores"),
                cpus=self.params.get("cpus"),
                cpuunits=self.params.get("cpuunits"),
                description=self.params.get("description"),
                disk=self.params.get("disk"),
                disk_volume=self.params.get("disk_volume"),
                features=self.params.get("features"),
                force=ansible_to_proxmox_bool(force),
                hookscript=self.params.get("hookscript"),
                hostname=hostname,
                ip_address=self.params.get("ip_address"),
                memory=self.params.get("memory"),
                mounts=self.params.get("mounts"),
                mount_volumes=self.params.get("mount_volumes"),
                nameserver=self.params.get("nameserver"),
                netif=self.params.get("netif"),
                onboot=ansible_to_proxmox_bool(self.params.get("onboot")),
                ostype=self.params.get("ostype"),
                password=self.params.get("password"),
                pool=self.params.get("pool"),
                pubkey=self.params.get("pubkey"),
                searchdomain=self.params.get("searchdomain"),
                startup=self.params.get("startup"),
                storage=self.params.get("storage"),
                swap=self.params.get("swap"),
                tags=self.params.get("tags"),
                timezone=self.params.get("timezone"),
                unprivileged=ansible_to_proxmox_bool(self.params.get("unprivileged")),
            )
            self.module.exit_json(
                changed=True,
                vmid=vmid,
                msg="Created VM %s from template %s" % (identifier, ostemplate),
            )

        self.module.fail_json(
            vmid=vmid,
            msg="VM %s does not exist but neither clone nor ostemplate were specified!"
            % identifier,
        )

    def create_lxc_instance(self, vmid, node, ostemplate, timeout, **kwargs):
        template_store = ostemplate.split(":")[0]
        if not self.content_check(node, ostemplate, template_store):
            self.module.fail_json(
                vmid=vmid,
                msg="ostemplate %s does not exist on node %s and storage %s."
                % (ostemplate, node, template_store),
            )

        disk_updates = self.process_disk_keys(
            vmid,
            node,
            kwargs.pop("disk"),
            kwargs.pop("disk_volume"),
        )
        mounts_updates = self.process_mount_keys(
            vmid,
            node,
            kwargs.pop("mounts"),
            kwargs.pop("mount_volumes"),
        )
        kwargs.update(disk_updates)
        kwargs.update(mounts_updates)

        # Remove empty values from kwargs
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if "features" in kwargs:
            kwargs["features"] = ",".join(kwargs.pop("features"))

        if "startup" in kwargs:
            kwargs["startup"] = ",".join(kwargs.pop("startup"))

        self.validate_tags(kwargs.get("tags", []))

        if self.VZ_TYPE == "lxc":
            if "cpus" in kwargs:
                kwargs["cpuunits"] = kwargs.pop("cpus")
            kwargs.update(kwargs.pop("netif", {}))
        else:
            if "mount_volumes" in kwargs:
                kwargs.pop("mount_volumes")
                self.module.warn(
                    "'mount_volumes' is not supported for non-LXC clusters. Ignoring keyword."
                )

        if "pubkey" in kwargs:
            pubkey = kwargs.pop("pubkey")
            if self.version() >= LooseVersion("4.2"):
                kwargs["ssh-public-keys"] = pubkey
            else:
                self.module.warn(
                    "'pubkey' is not supported for PVE 4.1 and below. Ignoring keyword."
                )

        if kwargs.get("ostype") == "auto":
            kwargs.pop("ostype")

        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE).create(
            vmid=vmid, ostemplate=ostemplate, **kwargs
        )
        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            "Reached timeout while waiting for creation of VM %s from template %s"
            % (vmid, ostemplate),
        )

    def clone_lxc_instance(self, vmid, node, clone_from, clone_type, timeout, **kwargs):
        if self.VZ_TYPE != "lxc":
            self.module.fail_json(
                msg="Cloning is only supported for LXC-enabled clusters in PVE 4.0 and above."
            )

        # Remove empty values from kwargs
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        target_is_template = self.is_template_container(node, clone_from)
        # By default, create a full copy only when the cloned container is not a template.
        create_full_copy = not target_is_template

        # Only accept parameters that are compatible with the clone endpoint.
        valid_clone_parameters = ["hostname", "pool", "description"]

        if "storage" not in kwargs and target_is_template:
            # Cloning a template, so create a full copy instead of a linked copy
            create_full_copy = True
        elif "storage" not in kwargs and not target_is_template:
            self.module.fail_json(
                changed=False,
                msg="Clone target container is not a template, storage needs to be specified.",
            )

        if clone_type == "linked" and not target_is_template:
            self.module.fail_json(
                changed=False,
                msg="Cloning type 'linked' is only supported for template containers.",
            )
        elif clone_type == "opportunistic" and not target_is_template:
            # Cloned container is not a template, so we need our 'storage' parameter
            valid_clone_parameters.append("storage")
        elif clone_type == "full":
            create_full_copy = True
            valid_clone_parameters.append("storage")

        clone_parameters = {}
        clone_parameters["full"] = ansible_to_proxmox_bool(create_full_copy)

        for param in valid_clone_parameters:
            if param in kwargs:
                clone_parameters[param] = kwargs[param]

        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE)(clone_from).clone.post(
            newid=vmid, **clone_parameters
        )
        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            timeout_msg="Reached timeout while waiting for VM to clone.",
        )

    def start_lxc_instance(self, vmid, node, timeout):
        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE)(vmid).status.start.post()

        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            timeout_msg="Reached timeout while waiting for VM to start.",
        )

    def stop_lxc_instance(self, vmid, node, timeout, force):
        stop_params = {}
        if force:
            stop_params["forceStop"] = 1

        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE)(vmid).status.shutdown.post(
            **stop_params
        )

        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            timeout_msg="Reached timeout while waiting for VM to stop.",
        )

    def umount_lxc_instance(self, vmid, node, timeout):
        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE)(vmid).status.unmount.post()

        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            timeout_msg="Reached timeout while waiting for VM to be unmounted.",
        )

    def remove_lxc_instance(self, vmid, node, timeout, purge):
        delete_params = {}
        if purge:
            delete_params["purge"] = 1

        proxmox_node = self.proxmox_api.nodes(node)
        taskid = getattr(proxmox_node, self.VZ_TYPE).delete(vmid, **delete_params)

        self.handle_api_timeout(
            vmid,
            node,
            taskid,
            timeout,
            timeout_msg="Reached timeout while waiting for VM to be removed.",
        )

    def process_disk_keys(self, vmid, node, disk, disk_volume):
        """
        Process disk keys and return a formatted disk volume with the `rootfs` key.

        Args:
            vmid (int): VM identifier.
            node (str): Node identifier.
            disk (str, optional): Disk key in the format 'storage:volume'. Defaults to None.
            disk_volume (Dict[str, Any], optional): Disk volume data. Defaults to None.

        Returns:
            Dict[str, str]: Formatted disk volume with the `rootfs` or `disk` key (depending on the `VZ_TYPE`), or an empty dict if no disk volume is specified.
        """
        if disk is None and disk_volume is None:
            return {}

        disk_dict = {}

        if disk is not None:
            if disk.isdigit():
                disk_dict["rootfs"] = disk
            else:
                disk_volume = self.parse_disk_string(disk)

        if disk_volume is not None:
            disk_dict = self.build_volume(vmid, node, key="rootfs", **disk_volume)

        if self.VZ_TYPE != "lxc":
            disk_dict["disk"] = disk_dict.pop("rootfs")

        return disk_dict

    def process_mount_keys(self, vmid, node, mounts, mount_volumes):
        """
        Process mount keys and return a formatted mount volumes with the `mp[n]` keys.

        Args:
            vmid (str): VM identifier.
            node (str): Node identifier.
            mounts (str, optional): Mount key in the format 'pool:volume'. Defaults to None.
            mount_volumes (Dict[str, Any], optional): Mount volume data. Defaults to None.

        Returns:
            Dict[str, str]: Formatted mount volumes with the `mp[n]` keys, or an empty dict if no mount volumes are specified.
        """
        if mounts is not None:
            mount_volumes = []
            for mount_key, mount_string in mounts.items():
                mount_config = self.parse_disk_string(mount_string)
                mount_volumes.append(dict(id=mount_key, **mount_config))
        elif mount_volumes is None or mount_volumes == []:
            return {}

        mounts_dict = {}
        for mount_config in mount_volumes:
            mount_key = mount_config.pop("id")
            mount_dict = self.build_volume(vmid, node, key=mount_key, **mount_config)
            mounts_dict.update(mount_dict)

        return mounts_dict

    def parse_disk_string(self, disk_string):
        """
        Parse a disk string and return a dictionary with the disk details.

        Args:
            disk_string (str): Disk string.

        Returns:
            Dict[str, Any]: Disk details.

        Note: Below are some example disk strings that this function MUST be able to parse:
            "acl=0,thin1:base-100-disk-1,size=8G"
            "thin1:10,backup=0"
            "local:20"
            "local-lvm:0.50"
            "tmp-dir:300/subvol-300-disk-0.subvol,acl=1,size=0T"
            "tmplog-dir:300/vm-300-disk-0.raw,mp=/var/log,mountoptions=noatime,size=32M"
            "volume=local-lvm:base-100-disk-1,size=20G"
            "/mnt/bindmounts/shared,mp=/shared"
            "volume=/dev/USB01,mp=/mnt/usb01"
        """
        args = disk_string.split(",")
        # If the volume is not explicitly defined but implicit by only passing a key,
        # add the "volume=" key prefix for ease of parsing.
        args = ["volume=" + arg if "=" not in arg else arg for arg in args]
        # Then create a dictionary from the arguments
        disk_kwargs = dict(map(lambda item: item.split("="), args))

        VOLUME_PATTERN = r"""(?x)
            ^
            (?:
                (?:
                    (?P<storage>[\w\-.]+):
                    (?:
                        (?P<size>\d+\.?\d*)|
                        (?P<volume>[^,\s]+)
                    )
                )|
                (?P<host_path>[^,\s]+)
            )
            $
        """
        # DISCLAIMER:
        # There are two things called a "volume":
        # 1. The "volume" key which describes the storage volume, device or directory to mount into the container.
        # 2. The storage volume of a storage-backed mount point in the PVE storage sub system.
        # In this section, we parse the "volume" key and check which type of mount point we are dealing with.
        pattern = re.compile(VOLUME_PATTERN)
        volume_string = disk_kwargs.pop("volume")
        match = pattern.match(volume_string)
        if match is None:
            raise ValueError(("Invalid volume string: %s", volume_string))
        match_dict = match.groupdict()
        match_dict = {k: v for k, v in match_dict.items() if v is not None}

        if "storage" in match_dict and "volume" in match_dict:
            disk_kwargs["storage"] = match_dict["storage"]
            disk_kwargs["volume"] = match_dict["volume"]
        elif "storage" in match_dict and "size" in match_dict:
            disk_kwargs["storage"] = match_dict["storage"]
            disk_kwargs["size"] = match_dict["size"]
        elif "host_path" in match_dict:
            disk_kwargs["host_path"] = match_dict["host_path"]

        # Pattern matching only available in Python 3.10+
        # TODO: Uncomment the following code once only Python 3.10+ is supported
        # match match_dict:
        #     case {"storage": storage, "volume": volume}:
        #         disk_kwargs["storage"] = storage
        #         disk_kwargs["volume"] = volume

        #     case {"storage": storage, "size": size}:
        #         disk_kwargs["storage"] = storage
        #         disk_kwargs["size"] = size

        #     case {"host_path": host_path}:
        #         disk_kwargs["host_path"] = host_path

        return disk_kwargs

    def build_volume(self, vmid, node, key, storage=None, volume=None, host_path=None, size=None, mountpoint=None, options=None, **kwargs):
        """
        Build a volume string for the specified VM.

        Args:
            vmid (str): The VM ID.
            node (str): The node where the VM resides.
            key (str): The key for the volume in the VM's config.
            storage (str, optional): The storage pool where the volume resides. Defaults to None.
            volume (str, optional): The name of the volume. Defaults to None.
            host_path (str, optional): The host path to mount. Defaults to None.
            size (str | int, optional): The size of the volume in GiB. Defaults to None.
            mountpoint (str, optional): The mountpoint for the volume. Defaults to None.
            options (Dict[str, Any], optional): Additional options for the volume. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, str]: The built volume string in the format {'volume_key': 'volume_string'}.

        Note: Further documentation can be found in the proxmox-api documentation: https://pve.proxmox.com/wiki/Linux_Container#pct_mount_points
        Note: To build a valid volume string, we need ONE of the following:
            A volume name, storage name, and size
            Only a storage name and size (to create a new volume or assign the volume automatically)
            A host directory to mount into the container
        """
        if isinstance(size, int):
            size = str(size)
        if size is not None and isfloat(size):
            size += "G"  # default to GiB
        # Handle volume checks/creation
        # TODO: Change the code below to pattern matching once only Python 3.10+ is supported
        # 1. Check if defined volume exists
        if volume is not None:
            storage_content = self.get_storage_content(node, storage, vmid=vmid)
            vol_ids = [vol["volid"] for vol in storage_content]
            volid = "{storage}:{volume}".format(storage=storage, volume=volume)
            if volid not in vol_ids:
                self.module.fail_json(
                    changed=False,
                    msg="Storage {storage} does not contain volume {volume}".format(
                        storage=storage,
                        volume=volume,
                    ),
                )
            vol_string = "{storage}:{volume},size={size}".format(
                storage=storage, volume=volume, size=size
            )
        # 2. If volume not defined (but storage is), check if it exists
        elif storage is not None:
            proxmox_node = self.proxmox_api.nodes(
                node
            )  # The node must exist, but not the LXC
            try:
                vol = proxmox_node.lxc(vmid).get("config").get(key)
                volume = self.parse_disk_string(vol).get("volume")
                vol_string = "{storage}:{volume},size={size}".format(
                    storage=storage, volume=volume, size=size
                )

            # If not, we have proxmox create one using the special syntax
            except Exception:
                if size is None:
                    raise ValueError(
                        "Size must be provided for storage-backed volume creation."
                    )
                elif size.endswith("G"):
                    size = size.rstrip("G")
                    vol_string = "{storage}:{size}".format(storage=storage, size=size)
                else:
                    raise ValueError(
                        "Size must be provided in GiB for storage-backed volume creation. Convert it to GiB or allocate a new storage manually."
                    )
        # 3. If we have a host_path, we don't have storage, a volume, or a size
        # Then we don't have to do anything, just build and return the vol_string
        elif host_path is not None:
            vol_string = ""
        else:
            raise ValueError(
                "Could not build a valid volume string. One of volume, storage, or host_path must be provided."
            )

        if host_path is not None:
            vol_string += "," + host_path

        if mountpoint is not None:
            vol_string += ",mp={}".format(mountpoint)

        if options is not None:
            vol_string += "," + ",".join(
                ["{0}={1}".format(k, v) for k, v in options.items()]
            )

        if kwargs:
            vol_string += "," + ",".join(
                ["{0}={1}".format(k, v) for k, v in kwargs.items()]
            )
        return {key: vol_string}

    def get_lxc_resource(self, vmid, hostname):
        if not vmid and not hostname:
            self.module.fail_json(msg="Either VMID or hostname must be provided.")

        if vmid:
            vm = self.get_lxc_resource_by_id(vmid)
        elif hostname:
            vm = self.get_lxc_resource_by_hostname(hostname)

        vmid = vm["vmid"]
        if vm["type"] != self.VZ_TYPE:
            identifier = self.format_vm_identifier(vmid, hostname)
            self.module.fail_json(
                msg="The specified VM %s is not an %s." % (identifier, self.VZ_TYPE)
            )

        return vm

    def get_lxc_resource_by_id(self, vmid):
        vms = self.get_vm_resources()

        vms = [vm for vm in vms if vm["vmid"] == vmid]
        if len(vms) == 0:
            raise LookupError("VM with VMID %d does not exist in cluster." % vmid)

        return vms[0]

    def get_lxc_resource_by_hostname(self, hostname):
        vms = self.get_vm_resources()

        vms = [vm for vm in vms if vm["name"] == hostname]
        if len(vms) == 0:
            raise LookupError(
                "VM with hostname %s does not exist in cluster." % hostname
            )
        elif len(vms) > 1:
            raise ValueError(
                "Multiple VMs found with hostname %s. Please specify VMID." % hostname
            )

        return vms[0]

    def get_vm_resources(self):
        try:
            return self.proxmox_api.cluster.resources.get(type="vm")
        except Exception as e:
            self.module.fail_json(
                msg="Unable to retrieve list of %s VMs from cluster resources: %s"
                % (self.VZ_TYPE, e)
            )

    def get_lxc_status(self, vmid, node_name):
        try:
            proxmox_node = self.proxmox_api.nodes(node_name)
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve node information: %s" % e)
        return getattr(proxmox_node, self.VZ_TYPE)(vmid).status.current.get()['status']

    def format_vm_identifier(self, vmid, hostname):
        if vmid and hostname:
            return "%s (%s)" % (hostname, vmid)
        elif hostname:
            return hostname
        else:
            return to_native(vmid)

    def handle_api_timeout(self, vmid, node, taskid, timeout, timeout_msg=""):
        if timeout_msg != "":
            timeout_msg = "%s " % timeout_msg

        while timeout > 0:
            if self.api_task_ok(node, taskid):
                return
            timeout -= 1
            time.sleep(1)

        self.module.fail_json(
            vmid=vmid,
            taskid=taskid,
            msg="%sLast line in task before timeout: %s"
            % (timeout_msg, self.proxmox_api.nodes(node).tasks(taskid).log.get()[:1]),
        )

    def is_template_container(self, node, target):
        """Check if the specified container is a template."""
        proxmox_node = self.proxmox_api.nodes(node)
        config = getattr(proxmox_node, self.VZ_TYPE)(target).config.get()
        return config.get("template", False)

    def content_check(self, node, ostemplate, template_store):
        """Check if the specified ostemplate is present in the specified storage."""
        proxmox_node = self.proxmox_api.nodes(node)
        storage_contents = proxmox_node.storage(template_store).content.get()
        return any(content["volid"] == ostemplate for content in storage_contents)

    def validate_tags(self, tags):
        """Check if the specified tags are valid."""
        re_tag = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-\+\.]*$")
        for tag in tags:
            if not re_tag.match(tag):
                self.module.fail_json(msg="%s is not a valid tag" % tag)
                return False
        return True

    def check_supported_features(self):
        for option, version in self.MINIMUM_VERSIONS.items():
            if self.version() < LooseVersion(version) and option in self.module.params:
                self.module.fail_json(
                    changed=False,
                    msg="Feature {option} is only supported in PVE {version}+, and you're using PVE {pve_version}".format(
                        option=option, version=version, pve_version=self.version()
                    ),
                )


def isfloat(value):
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


def main():
    module = get_ansible_module()
    proxmox = ProxmoxLxcAnsible(module)

    try:
        proxmox.run()
    except Exception as e:
        module.fail_json(msg="An error occurred: %s" % to_native(e))


if __name__ == "__main__":
    main()
