#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxmox
short_description: management of instances in Proxmox VE cluster
description:
  - allows you to create/delete/stop instances in Proxmox VE cluster
  - Starting in Ansible 2.1, it automatically detects containerization type (lxc for PVE 4, openvz for older)
  - From community.general 4.0.0 on, there will be no default values, see I(proxmox_default_behavior).
options:
  password:
    description:
      - the instance root password
    type: str
  hostname:
    description:
      - the instance hostname
      - required only for C(state=present)
      - must be unique if vmid is not passed
    type: str
  ostemplate:
    description:
      - the template for VM creating
      - required only for C(state=present)
    type: str
  disk:
    description:
      - This option was previously described as "hard disk size in GB for instance" however several formats describing
        a lxc mount are permitted.
      - Older versions of Proxmox will accept a numeric value for size using the I(storage) parameter to automatically
        choose which storage to allocate from, however new versions enforce the C(<STORAGE>:<SIZE>) syntax.
      - "Additional options are available by using some combination of the following key-value pairs as a
        comma-delimited list C([volume=]<volume> [,acl=<1|0>] [,mountoptions=<opt[;opt...]>] [,quota=<1|0>]
        [,replicate=<1|0>] [,ro=<1|0>] [,shared=<1|0>] [,size=<DiskSize>])."
      - See U(https://pve.proxmox.com/wiki/Linux_Container) for a full description.
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(3). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: str
  cores:
    description:
      - Specify number of cores per socket.
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(1). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: int
  cpus:
    description:
      - numbers of allocated cpus for instance
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(1). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: int
  memory:
    description:
      - memory size in MB for instance
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(512). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: int
  swap:
    description:
      - swap memory size in MB for instance
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(0). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
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
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(no). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: bool
  storage:
    description:
      - target storage
    type: str
    default: 'local'
  cpuunits:
    description:
      - CPU weight for a VM
      - If I(proxmox_default_behavior) is set to C(compatiblity) (the default value), this
        option has a default of C(1000). Note that the default value of I(proxmox_default_behavior)
        changes in community.general 4.0.0.
    type: int
  nameserver:
    description:
      - sets DNS server IP address for a container
    type: str
  searchdomain:
    description:
      - sets DNS search domain for a container
    type: str
  timeout:
    description:
      - timeout for operations
    type: int
    default: 30
  force:
    description:
      - forcing operations
      - can be used only with states C(present), C(stopped), C(restarted)
      - with C(state=present) force option allow to overwrite existing container
      - with states C(stopped) , C(restarted) allow to force stop instance
    type: bool
    default: 'no'
  purge:
    description:
      - Remove container from all related configurations.
      - For example backup jobs, replication jobs, or HA.
      - Related ACLs and Firewall entries will always be removed.
      - Used with state C(absent).
    type: bool
    default: false
    version_added: 2.3.0
  state:
    description:
     - Indicate desired state of the instance
    type: str
    choices: ['present', 'started', 'absent', 'stopped', 'restarted']
    default: present
  pubkey:
    description:
      - Public key to add to /root/.ssh/authorized_keys. This was added on Proxmox 4.2, it is ignored for earlier versions
    type: str
  unprivileged:
    description:
      - Indicate if the container should be unprivileged
    type: bool
    default: 'no'
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
  proxmox_default_behavior:
    description:
      - Various module options used to have default values. This cause problems when
        user expects different behavior from proxmox by default or fill options which cause
        problems when they have been set.
      - The default value is C(compatibility), which will ensure that the default values
        are used when the values are not explicitly specified by the user.
      - From community.general 4.0.0 on, the default value will switch to C(no_defaults). To avoid
        deprecation warnings, please set I(proxmox_default_behavior) to an explicit
        value.
      - This affects the I(disk), I(cores), I(cpus), I(memory), I(onboot), I(swap), I(cpuunits) options.
    type: str
    choices:
      - compatibility
      - no_defaults
    version_added: "1.3.0"
author: Sergei Antipov (@UnderGreen)
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.proxmox.selection
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
    force: yes

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
    force: yes
    state: stopped

- name: Restart container(stopped or mounted container you can't restart)
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: restarted

- name: Remove container
  community.general.proxmox:
    vmid: 100
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    state: absent
'''

import time
import traceback
from distutils.version import LooseVersion

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.common.text.converters import to_native


VZ_TYPE = None


def get_nextvmid(module, proxmox):
    try:
        vmid = proxmox.cluster.nextid.get()
        return vmid
    except Exception as e:
        module.fail_json(msg="Unable to get next vmid. Failed with exception: %s" % to_native(e),
                         exception=traceback.format_exc())


def get_vmid(proxmox, hostname):
    return [vm['vmid'] for vm in proxmox.cluster.resources.get(type='vm') if 'name' in vm and vm['name'] == hostname]


def get_instance(proxmox, vmid):
    return [vm for vm in proxmox.cluster.resources.get(type='vm') if vm['vmid'] == int(vmid)]


def content_check(proxmox, node, ostemplate, template_store):
    return [True for cnt in proxmox.nodes(node).storage(template_store).content.get() if cnt['volid'] == ostemplate]


def node_check(proxmox, node):
    return [True for nd in proxmox.nodes.get() if nd['node'] == node]


def proxmox_version(proxmox):
    apireturn = proxmox.version.get()
    return LooseVersion(apireturn['version'])


def create_instance(module, proxmox, vmid, node, disk, storage, cpus, memory, swap, timeout, **kwargs):
    proxmox_node = proxmox.nodes(node)
    kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)

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
            if proxmox_version(proxmox) >= LooseVersion('4.2'):
                kwargs['ssh-public-keys'] = kwargs['pubkey']
            del kwargs['pubkey']
    else:
        kwargs['cpus'] = cpus
        kwargs['disk'] = disk

    taskid = getattr(proxmox_node, VZ_TYPE).create(vmid=vmid, storage=storage, memory=memory, swap=swap, **kwargs)

    while timeout:
        if (proxmox_node.tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox_node.tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for creating VM. Last line in task before timeout: %s' %
                                 proxmox_node.tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def start_instance(module, proxmox, vm, vmid, timeout):
    taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.start.post()
    while timeout:
        if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for starting VM. Last line in task before timeout: %s' %
                                 proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def stop_instance(module, proxmox, vm, vmid, timeout, force):
    if force:
        taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.shutdown.post(forceStop=1)
    else:
        taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.shutdown.post()
    while timeout:
        if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for stopping VM. Last line in task before timeout: %s' %
                                 proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def umount_instance(module, proxmox, vm, vmid, timeout):
    taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.umount.post()
    while timeout:
        if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
            return True
        timeout -= 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for unmounting VM. Last line in task before timeout: %s' %
                                 proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(required=True),
            api_password=dict(no_log=True, fallback=(env_fallback, ['PROXMOX_PASSWORD'])),
            api_token_id=dict(no_log=True),
            api_token_secret=dict(no_log=True),
            api_user=dict(required=True),
            vmid=dict(type='int', required=False),
            validate_certs=dict(type='bool', default=False),
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
            onboot=dict(type='bool'),
            features=dict(type='list', elements='str'),
            storage=dict(default='local'),
            cpuunits=dict(type='int'),
            nameserver=dict(),
            searchdomain=dict(),
            timeout=dict(type='int', default=30),
            force=dict(type='bool', default=False),
            purge=dict(type='bool', default=False),
            state=dict(default='present', choices=['present', 'absent', 'stopped', 'started', 'restarted']),
            pubkey=dict(type='str', default=None),
            unprivileged=dict(type='bool', default=False),
            description=dict(type='str'),
            hookscript=dict(type='str'),
            proxmox_default_behavior=dict(type='str', choices=['compatibility', 'no_defaults']),
        ),
        required_if=[('state', 'present', ['node', 'hostname', 'ostemplate'])],
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('api_password', 'api_token_id')],
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg='proxmoxer required for this module')

    state = module.params['state']
    api_host = module.params['api_host']
    api_password = module.params['api_password']
    api_token_id = module.params['api_token_id']
    api_token_secret = module.params['api_token_secret']
    api_user = module.params['api_user']
    vmid = module.params['vmid']
    validate_certs = module.params['validate_certs']
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

    if module.params['proxmox_default_behavior'] is None:
        module.params['proxmox_default_behavior'] = 'compatibility'
        module.deprecate(
            'The proxmox_default_behavior option will change its default value from "compatibility" to '
            '"no_defaults" in community.general 4.0.0. To remove this warning, please specify an explicit value for it now',
            version='4.0.0', collection_name='community.general'
        )
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

    auth_args = {'user': api_user}
    if not api_token_id:
        auth_args['password'] = api_password
    else:
        auth_args['token_name'] = api_token_id
        auth_args['token_value'] = api_token_secret

    try:
        proxmox = ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
        global VZ_TYPE
        VZ_TYPE = 'openvz' if proxmox_version(proxmox) < LooseVersion('4.0') else 'lxc'
    except Exception as e:
        module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

    # If vmid not set get the Next VM id from ProxmoxAPI
    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and state == 'present':
        vmid = get_nextvmid(module, proxmox)
    elif not vmid and hostname:
        hosts = get_vmid(proxmox, hostname)
        if len(hosts) == 0:
            module.fail_json(msg="Vmid could not be fetched => Hostname doesn't exist (action: %s)" % state)
        vmid = hosts[0]
    elif not vmid:
        module.exit_json(changed=False, msg="Vmid could not be fetched for the following action: %s" % state)

    if state == 'present':
        try:
            if get_instance(proxmox, vmid) and not module.params['force']:
                module.exit_json(changed=False, msg="VM with vmid = %s is already exists" % vmid)
            # If no vmid was passed, there cannot be another VM named 'hostname'
            if not module.params['vmid'] and get_vmid(proxmox, hostname) and not module.params['force']:
                module.exit_json(changed=False, msg="VM with hostname %s already exists and has ID number %s" % (hostname, get_vmid(proxmox, hostname)[0]))
            elif not node_check(proxmox, node):
                module.fail_json(msg="node '%s' not exists in cluster" % node)
            elif not content_check(proxmox, node, module.params['ostemplate'], template_store):
                module.fail_json(msg="ostemplate '%s' not exists on node %s and storage %s"
                                 % (module.params['ostemplate'], node, template_store))

            create_instance(module, proxmox, vmid, node, disk, storage, cpus, memory, swap, timeout,
                            cores=module.params['cores'],
                            pool=module.params['pool'],
                            password=module.params['password'],
                            hostname=module.params['hostname'],
                            ostemplate=module.params['ostemplate'],
                            netif=module.params['netif'],
                            mounts=module.params['mounts'],
                            ip_address=module.params['ip_address'],
                            onboot=int(module.params['onboot']),
                            cpuunits=module.params['cpuunits'],
                            nameserver=module.params['nameserver'],
                            searchdomain=module.params['searchdomain'],
                            force=int(module.params['force']),
                            pubkey=module.params['pubkey'],
                            features=",".join(module.params['features']) if module.params['features'] is not None else None,
                            unprivileged=int(module.params['unprivileged']),
                            description=module.params['description'],
                            hookscript=module.params['hookscript'])

            module.exit_json(changed=True, msg="deployed VM %s from template %s" % (vmid, module.params['ostemplate']))
        except Exception as e:
            module.fail_json(msg="creation of %s VM %s failed with exception: %s" % (VZ_TYPE, vmid, e))

    elif state == 'started':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.fail_json(msg='VM with vmid = %s not exists in cluster' % vmid)
            if getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'running':
                module.exit_json(changed=False, msg="VM %s is already running" % vmid)

            if start_instance(module, proxmox, vm, vmid, timeout):
                module.exit_json(changed=True, msg="VM %s started" % vmid)
        except Exception as e:
            module.fail_json(msg="starting of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'stopped':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.fail_json(msg='VM with vmid = %s not exists in cluster' % vmid)

            if getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'mounted':
                if module.params['force']:
                    if umount_instance(module, proxmox, vm, vmid, timeout):
                        module.exit_json(changed=True, msg="VM %s is shutting down" % vmid)
                else:
                    module.exit_json(changed=False, msg=("VM %s is already shutdown, but mounted. "
                                                         "You can use force option to umount it.") % vmid)

            if getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'stopped':
                module.exit_json(changed=False, msg="VM %s is already shutdown" % vmid)

            if stop_instance(module, proxmox, vm, vmid, timeout, force=module.params['force']):
                module.exit_json(changed=True, msg="VM %s is shutting down" % vmid)
        except Exception as e:
            module.fail_json(msg="stopping of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'restarted':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.fail_json(msg='VM with vmid = %s not exists in cluster' % vmid)
            if (getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'stopped' or
                    getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'mounted'):
                module.exit_json(changed=False, msg="VM %s is not running" % vmid)

            if (stop_instance(module, proxmox, vm, vmid, timeout, force=module.params['force']) and
                    start_instance(module, proxmox, vm, vmid, timeout)):
                module.exit_json(changed=True, msg="VM %s is restarted" % vmid)
        except Exception as e:
            module.fail_json(msg="restarting of VM %s failed with exception: %s" % (vmid, e))

    elif state == 'absent':
        try:
            vm = get_instance(proxmox, vmid)
            if not vm:
                module.exit_json(changed=False, msg="VM %s does not exist" % vmid)

            if getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'running':
                module.exit_json(changed=False, msg="VM %s is running. Stop it before deletion." % vmid)

            if getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE)(vmid).status.current.get()['status'] == 'mounted':
                module.exit_json(changed=False, msg="VM %s is mounted. Stop it with force option before deletion." % vmid)

            delete_params = {}

            if module.params['purge']:
                delete_params['purge'] = 1

            taskid = getattr(proxmox.nodes(vm[0]['node']), VZ_TYPE).delete(vmid, **delete_params)

            while timeout:
                if (proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['status'] == 'stopped' and
                        proxmox.nodes(vm[0]['node']).tasks(taskid).status.get()['exitstatus'] == 'OK'):
                    module.exit_json(changed=True, msg="VM %s removed" % vmid)
                timeout -= 1
                if timeout == 0:
                    module.fail_json(msg='Reached timeout while waiting for removing VM. Last line in task before timeout: %s'
                                     % proxmox.nodes(vm[0]['node']).tasks(taskid).log.get()[:1])

                time.sleep(1)
        except Exception as e:
            module.fail_json(msg="deletion of VM %s failed with exception: %s" % (vmid, to_native(e)))


if __name__ == '__main__':
    main()
