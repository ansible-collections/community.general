#!/usr/bin/python
#
# Copyright (c) 2016 Sertac Ozercan, <seozerca@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_virtualmachinescaleset


short_description: Manage Azure virtual machine scale sets

description:
    - Create and update a virtual machine scale set.
    - Note that this module was called M(azure_rm_virtualmachine_scaleset) before Ansible 2.8. The usage did not change.

options:
    resource_group:
        description:
            - Name of the resource group containing the virtual machine scale set.
        required: true
    name:
        description:
            - Name of the virtual machine.
        required: true
    state:
        description:
            - Assert the state of the virtual machine scale set.
            - State C(present) will check that the machine exists with the requested configuration. If the configuration
              of the existing machine does not match, the machine will be updated.
            - State C(absent) will remove the virtual machine scale set.
        default: present
        choices:
            - absent
            - present
    location:
        description:
            - Valid Azure location. Defaults to location of the resource group.
    short_hostname:
        description:
            - Short host name.
    vm_size:
        description:
            - A valid Azure VM size value. For example, C(Standard_D4).
            - The list of choices varies depending on the subscription and location. Check your subscription for available choices.
    capacity:
        description:
            - Capacity of VMSS.
        default: 1
    tier:
        description:
            - SKU Tier.
        choices:
            - Basic
            - Standard
    upgrade_policy:
        description:
            - Upgrade policy.
            - Required when creating the Azure virtual machine scale sets.
        choices:
            - Manual
            - Automatic
    admin_username:
        description:
            - Admin username used to access the host after it is created. Required when creating a VM.
    admin_password:
        description:
            - Password for the admin username.
            - Not required if the os_type is Linux and SSH password authentication is disabled by setting I(ssh_password_enabled=false).
    ssh_password_enabled:
        description:
            - When the os_type is Linux, setting I(ssh_password_enabled=false) will disable SSH password authentication and require use of SSH keys.
        type: bool
        default: true
    ssh_public_keys:
        description:
            - For I(os_type=Linux) provide a list of SSH keys.
            - Each item in the list should be a dictionary where the dictionary contains two keys, C(path) and C(key_data).
            - Set the C(path) to the default location of the authorized_keys files.
            - On an Enterprise Linux host, for example, the I(path=/home/<admin username>/.ssh/authorized_keys).
              Set C(key_data) to the actual value of the public key.
    image:
        description:
            - Specifies the image used to build the VM.
            - If a string, the image is sourced from a custom image based on the name.
            - If a dict with the keys I(publisher), I(offer), I(sku), and I(version), the image is sourced from a Marketplace image.
               Note that set I(version=latest) to get the most recent version of a given image.
            - If a dict with the keys I(name) and I(resource_group), the image is sourced from a custom image based on the I(name) and I(resource_group) set.
              Note that the key I(resource_group) is optional and if omitted, all images in the subscription will be searched for by I(name).
            - Custom image support was added in Ansible 2.5.
        required: true
    os_disk_caching:
        description:
            - Type of OS disk caching.
        choices:
            - ReadOnly
            - ReadWrite
        default: ReadOnly
        aliases:
            - disk_caching
    os_type:
        description:
            - Base type of operating system.
        choices:
            - Windows
            - Linux
        default: Linux
    managed_disk_type:
        description:
            - Managed disk type.
        choices:
            - Standard_LRS
            - Premium_LRS
    data_disks:
        description:
            - Describes list of data disks.
        suboptions:
            lun:
                description:
                    - The logical unit number for data disk.
                default: 0
            disk_size_gb:
                description:
                    - The initial disk size in GB for blank data disks.
            managed_disk_type:
                description:
                    - Managed data disk type.
                choices:
                    - Standard_LRS
                    - Premium_LRS
            caching:
                description:
                    - Type of data disk caching.
                choices:
                    - ReadOnly
                    - ReadWrite
                default: ReadOnly
    virtual_network_resource_group:
        description:
            - When creating a virtual machine, if a specific virtual network from another resource group should be
              used.
            - Use this parameter to specify the resource group to use.
    virtual_network_name:
        description:
            - Virtual Network name.
        aliases:
            - virtual_network
    subnet_name:
        description:
            - Subnet name.
        aliases:
            - subnet
    load_balancer:
        description:
            - Load balancer name.
    application_gateway:
        description:
            - Application gateway name.
    remove_on_absent:
        description:
            - When removing a VM using I(state=absent), also remove associated resources.
            - It can be C(all) or a list with any of the following ['network_interfaces', 'virtual_storage', 'public_ips'].
            - Any other input will be ignored.
        default: ['all']
    enable_accelerated_networking:
        description:
            - Indicates whether user wants to allow accelerated networking for virtual machines in scaleset being created.
        type: bool
    security_group:
        description:
            - Existing security group with which to associate the subnet.
            - It can be the security group name which is in the same resource group.
            - It can be the resource ID.
            - It can be a dict which contains I(name) and I(resource_group) of the security group.
        aliases:
            - security_group_name
    overprovision:
        description:
            - Specifies whether the Virtual Machine Scale Set should be overprovisioned.
        type: bool
        default: True
    single_placement_group:
        description:
            - When true this limits the scale set to a single placement group, of max size 100 virtual machines.
        type: bool
        default: True
    plan:
        description:
            - Third-party billing plan for the VM.
        type: dict
        suboptions:
            name:
                description:
                    - Billing plan name.
                required: true
            product:
                description:
                    - Product name.
                required: true
            publisher:
                description:
                    - Publisher offering the plan.
                required: true
            promotion_code:
                description:
                    - Optional promotion code.
    zones:
        description:
            - A list of Availability Zones for your virtual machine scale set.
        type: list
    custom_data:
        description:
            - Data which is made available to the virtual machine and used by e.g., C(cloud-init).
            - Many images in the marketplace are not cloud-init ready. Thus, data sent to I(custom_data) would be ignored.
            - If the image you are attempting to use is not listed in
              U(https://docs.microsoft.com/en-us/azure/virtual-machines/linux/using-cloud-init#cloud-init-overview),
              follow these steps U(https://docs.microsoft.com/en-us/azure/virtual-machines/linux/cloudinit-prepare-custom-image).
    scale_in_policy:
        description:
            - define the order in which vmss instances are scaled-in
        choices:
            - Default
            - NewestVM
            - OldestVM
    terminate_event_timeout_minutes:
        description:
            - timeout time for termination notification event
            - in range between 5 and 15


author:
    - Sertac Ozercan (@sozercan)


extends_documentation_fragment:
- community.general.azure
- community.general.azure_tags
'''
EXAMPLES = '''

- name: Create VMSS
  azure_rm_virtualmachinescaleset:
    resource_group: myResourceGroup
    name: testvmss
    vm_size: Standard_DS1_v2
    capacity: 2
    virtual_network_name: testvnet
    upgrade_policy: Manual
    subnet_name: testsubnet
    terminate_event_timeout_minutes: 10
    scale_in_policy: NewestVM
    admin_username: adminUser
    ssh_password_enabled: false
    ssh_public_keys:
      - path: /home/adminUser/.ssh/authorized_keys
        key_data: < insert yor ssh public key here... >
    managed_disk_type: Standard_LRS
    image:
      offer: CoreOS
      publisher: CoreOS
      sku: Stable
      version: latest
    data_disks:
      - lun: 0
        disk_size_gb: 64
        caching: ReadWrite
        managed_disk_type: Standard_LRS

- name: Create VMSS with an image that requires plan information
  azure_rm_virtualmachinescaleset:
    resource_group: myResourceGroup
    name: testvmss
    vm_size: Standard_DS1_v2
    capacity: 3
    virtual_network_name: testvnet
    upgrade_policy: Manual
    subnet_name: testsubnet
    admin_username: adminUser
    ssh_password_enabled: false
    ssh_public_keys:
      - path: /home/adminUser/.ssh/authorized_keys
        key_data: < insert yor ssh public key here... >
    managed_disk_type: Standard_LRS
    image:
      offer: cis-ubuntu-linux-1804-l1
      publisher: center-for-internet-security-inc
      sku: Stable
      version: latest
    plan:
      name: cis-ubuntu-linux-1804-l1
      product: cis-ubuntu-linux-1804-l1
      publisher: center-for-internet-security-inc
    data_disks:
      - lun: 0
        disk_size_gb: 64
        caching: ReadWrite
        managed_disk_type: Standard_LRS

- name: Create a VMSS with a custom image
  azure_rm_virtualmachinescaleset:
    resource_group: myResourceGroup
    name: testvmss
    vm_size: Standard_DS1_v2
    capacity: 2
    virtual_network_name: testvnet
    upgrade_policy: Manual
    subnet_name: testsubnet
    admin_username: adminUser
    admin_password: password01
    managed_disk_type: Standard_LRS
    image: customimage001

- name: Create a VMSS with over 100 instances
  azure_rm_virtualmachinescaleset:
    resource_group: myResourceGroup
    name: testvmss
    vm_size: Standard_DS1_v2
    capacity: 120
    single_placement_group: False
    virtual_network_name: testvnet
    upgrade_policy: Manual
    subnet_name: testsubnet
    admin_username: adminUser
    admin_password: password01
    managed_disk_type: Standard_LRS
    image: customimage001

- name: Create a VMSS with a custom image from a particular resource group
  azure_rm_virtualmachinescaleset:
    resource_group: myResourceGroup
    name: testvmss
    vm_size: Standard_DS1_v2
    capacity: 2
    virtual_network_name: testvnet
    upgrade_policy: Manual
    subnet_name: testsubnet
    admin_username: adminUser
    admin_password: password01
    managed_disk_type: Standard_LRS
    image:
      name: customimage001
      resource_group: myResourceGroup
'''

RETURN = '''
azure_vmss:
    description:
        - Facts about the current state of the object.
        - Note that facts are not part of the registered output but available directly.
    returned: always
    type: dict
    sample: {
        "properties": {
            "overprovision": true,
             "scaleInPolicy": {
                    "rules": [
                        "NewestVM"
                    ]
            },
            "singlePlacementGroup": true,
            "upgradePolicy": {
                "mode": "Manual"
            },
            "virtualMachineProfile": {
                "networkProfile": {
                    "networkInterfaceConfigurations": [
                        {
                            "name": "testvmss",
                            "properties": {
                                "dnsSettings": {
                                    "dnsServers": []
                                },
                                "enableAcceleratedNetworking": false,
                                "ipConfigurations": [
                                    {
                                        "name": "default",
                                        "properties": {
                                            "privateIPAddressVersion": "IPv4",
                                            "subnet": {
                                                "id": "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroup/myResourceGroup/providers/Microsoft.Network/virtualNetworks/testvnet/subnets/testsubnet"
                                            }
                                        }
                                    }
                                ],
                                "primary": true
                            }
                        }
                    ]
                },
                "osProfile": {
                    "adminUsername": "testuser",
                    "computerNamePrefix": "testvmss",
                    "linuxConfiguration": {
                        "disablePasswordAuthentication": true,
                        "ssh": {
                            "publicKeys": [
                                {
                                    "keyData": "",
                                    "path": "/home/testuser/.ssh/authorized_keys"
                                }
                            ]
                        }
                    },
                    "secrets": []
                },
                "scheduledEventsProfile": {
                        "terminateNotificationProfile": {
                            "enable": true,
                            "notBeforeTimeout": "PT10M"
                        }
                },
                "storageProfile": {
                    "dataDisks": [
                        {
                            "caching": "ReadWrite",
                            "createOption": "empty",
                            "diskSizeGB": 64,
                            "lun": 0,
                            "managedDisk": {
                                "storageAccountType": "Standard_LRS"
                            }
                        }
                    ],
                    "imageReference": {
                        "offer": "CoreOS",
                        "publisher": "CoreOS",
                        "sku": "Stable",
                        "version": "899.17.0"
                    },
                    "osDisk": {
                        "caching": "ReadWrite",
                        "createOption": "fromImage",
                        "managedDisk": {
                            "storageAccountType": "Standard_LRS"
                        }
                    }
                }
            }
        },
        "sku": {
            "capacity": 2,
            "name": "Standard_DS1_v2",
            "tier": "Standard"
        },
        "tags": null,
        "type": "Microsoft.Compute/virtualMachineScaleSets"
    }
'''  # NOQA

import base64

try:
    from msrestazure.azure_exceptions import CloudError
    from msrestazure.tools import parse_resource_id

except ImportError:
    # This is handled in azure_rm_common
    pass

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase, azure_id_to_dict, format_resource_id
from ansible.module_utils.basic import to_native, to_bytes


AZURE_OBJECT_CLASS = 'VirtualMachineScaleSet'

AZURE_ENUM_MODULES = ['azure.mgmt.compute.models']


class AzureRMVirtualMachineScaleSet(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            resource_group=dict(type='str', required=True),
            name=dict(type='str', required=True),
            state=dict(choices=['present', 'absent'], default='present', type='str'),
            location=dict(type='str'),
            short_hostname=dict(type='str'),
            vm_size=dict(type='str'),
            tier=dict(type='str', choices=['Basic', 'Standard']),
            capacity=dict(type='int', default=1),
            upgrade_policy=dict(type='str', choices=['Automatic', 'Manual']),
            admin_username=dict(type='str'),
            admin_password=dict(type='str', no_log=True),
            ssh_password_enabled=dict(type='bool', default=True),
            ssh_public_keys=dict(type='list'),
            image=dict(type='raw'),
            os_disk_caching=dict(type='str', aliases=['disk_caching'], choices=['ReadOnly', 'ReadWrite'],
                                 default='ReadOnly'),
            os_type=dict(type='str', choices=['Linux', 'Windows'], default='Linux'),
            managed_disk_type=dict(type='str', choices=['Standard_LRS', 'Premium_LRS']),
            data_disks=dict(type='list'),
            subnet_name=dict(type='str', aliases=['subnet']),
            load_balancer=dict(type='str'),
            application_gateway=dict(type='str'),
            virtual_network_resource_group=dict(type='str'),
            virtual_network_name=dict(type='str', aliases=['virtual_network']),
            remove_on_absent=dict(type='list', default=['all']),
            enable_accelerated_networking=dict(type='bool'),
            security_group=dict(type='raw', aliases=['security_group_name']),
            overprovision=dict(type='bool', default=True),
            single_placement_group=dict(type='bool', default=True),
            zones=dict(type='list'),
            custom_data=dict(type='str'),
            plan=dict(type='dict', options=dict(publisher=dict(type='str', required=True),
                      product=dict(type='str', required=True), name=dict(type='str', required=True),
                      promotion_code=dict(type='str'))),
            scale_in_policy=dict(type='str', choices=['Default', 'OldestVM', 'NewestVM']),
            terminate_event_timeout_minutes=dict(type='int')
        )

        self.resource_group = None
        self.name = None
        self.state = None
        self.location = None
        self.short_hostname = None
        self.vm_size = None
        self.capacity = None
        self.tier = None
        self.upgrade_policy = None
        self.admin_username = None
        self.admin_password = None
        self.ssh_password_enabled = None
        self.ssh_public_keys = None
        self.image = None
        self.os_disk_caching = None
        self.managed_disk_type = None
        self.data_disks = None
        self.os_type = None
        self.subnet_name = None
        self.virtual_network_resource_group = None
        self.virtual_network_name = None
        self.tags = None
        self.differences = None
        self.load_balancer = None
        self.application_gateway = None
        self.enable_accelerated_networking = None
        self.security_group = None
        self.overprovision = None
        self.single_placement_group = None
        self.zones = None
        self.custom_data = None
        self.plan = None
        self.scale_in_policy = None
        self.terminate_event_timeout_minutes = None

        mutually_exclusive = [('load_balancer', 'application_gateway')]
        self.results = dict(
            changed=False,
            actions=[],
            ansible_facts=dict(azure_vmss=None)
        )

        super(AzureRMVirtualMachineScaleSet, self).__init__(
            derived_arg_spec=self.module_arg_spec,
            supports_check_mode=True,
            mutually_exclusive=mutually_exclusive)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()) + ['tags']:
            setattr(self, key, kwargs[key])

        if self.module._name == 'azure_rm_virtualmachine_scaleset':
            self.module.deprecate("The 'azure_rm_virtualmachine_scaleset' module has been renamed to 'azure_rm_virtualmachinescaleset'", version='2.12')

        # make sure options are lower case
        self.remove_on_absent = set([resource.lower() for resource in self.remove_on_absent])

        # convert elements to ints
        self.zones = [int(i) for i in self.zones] if self.zones else None

        # default virtual_network_resource_group to resource_group
        if not self.virtual_network_resource_group:
            self.virtual_network_resource_group = self.resource_group

        changed = False
        results = dict()
        vmss = None
        disable_ssh_password = None
        subnet = None
        image_reference = None
        load_balancer_backend_address_pools = None
        load_balancer_inbound_nat_pools = None
        load_balancer = None
        application_gateway = None
        application_gateway_backend_address_pools = None
        support_lb_change = True

        resource_group = self.get_resource_group(self.resource_group)
        if not self.location:
            # Set default location
            self.location = resource_group.location

        if self.custom_data:
            self.custom_data = to_native(base64.b64encode(to_bytes(self.custom_data)))

        if self.state == 'present':
            # Verify parameters and resolve any defaults

            if self.vm_size and not self.vm_size_is_valid():
                self.fail("Parameter error: vm_size {0} is not valid for your subscription and location.".format(
                    self.vm_size
                ))

            # if self.virtual_network_name:
            #     virtual_network = self.get_virtual_network(self.virtual_network_name)

            if self.ssh_public_keys:
                msg = "Parameter error: expecting ssh_public_keys to be a list of type dict where " \
                    "each dict contains keys: path, key_data."
                for key in self.ssh_public_keys:
                    if not isinstance(key, dict):
                        self.fail(msg)
                    if not key.get('path') or not key.get('key_data'):
                        self.fail(msg)

            if self.image and isinstance(self.image, dict):
                if all(key in self.image for key in ('publisher', 'offer', 'sku', 'version')):
                    marketplace_image = self.get_marketplace_image_version()
                    if self.image['version'] == 'latest':
                        self.image['version'] = marketplace_image.name
                        self.log("Using image version {0}".format(self.image['version']))

                    image_reference = self.compute_models.ImageReference(
                        publisher=self.image['publisher'],
                        offer=self.image['offer'],
                        sku=self.image['sku'],
                        version=self.image['version']
                    )
                elif self.image.get('name'):
                    custom_image = True
                    image_reference = self.get_custom_image_reference(
                        self.image.get('name'),
                        self.image.get('resource_group'))
                elif self.image.get('id'):
                    try:
                        image_reference = self.compute_models.ImageReference(id=self.image['id'])
                    except Exception as exc:
                        self.fail("id Error: Cannot get image from the reference id - {0}".format(self.image['id']))
                else:
                    self.fail("parameter error: expecting image to contain [publisher, offer, sku, version], [name, resource_group] or [id]")
            elif self.image and isinstance(self.image, str):
                custom_image = True
                image_reference = self.get_custom_image_reference(self.image)
            elif self.image:
                self.fail("parameter error: expecting image to be a string or dict not {0}".format(type(self.image).__name__))

            disable_ssh_password = not self.ssh_password_enabled

            if self.load_balancer:
                load_balancer = self.get_load_balancer(self.load_balancer)
                load_balancer_backend_address_pools = ([self.compute_models.SubResource(id=resource.id)
                                                        for resource in load_balancer.backend_address_pools]
                                                       if load_balancer.backend_address_pools else None)
                load_balancer_inbound_nat_pools = ([self.compute_models.SubResource(id=resource.id)
                                                    for resource in load_balancer.inbound_nat_pools]
                                                   if load_balancer.inbound_nat_pools else None)

            if self.application_gateway:
                application_gateway = self.get_application_gateway(self.application_gateway)
                application_gateway_backend_address_pools = ([self.compute_models.SubResource(id=resource.id)
                                                              for resource in application_gateway.backend_address_pools]
                                                             if application_gateway.backend_address_pools else None)

        try:
            self.log("Fetching virtual machine scale set {0}".format(self.name))
            vmss = self.compute_client.virtual_machine_scale_sets.get(self.resource_group, self.name)
            self.check_provisioning_state(vmss, self.state)
            vmss_dict = self.serialize_vmss(vmss)

            if self.state == 'present':
                differences = []
                results = vmss_dict

                if self.os_disk_caching and \
                   self.os_disk_caching != vmss_dict['properties']['virtualMachineProfile']['storageProfile']['osDisk']['caching']:
                    self.log('CHANGED: virtual machine scale set {0} - OS disk caching'.format(self.name))
                    differences.append('OS Disk caching')
                    changed = True
                    vmss_dict['properties']['virtualMachineProfile']['storageProfile']['osDisk']['caching'] = self.os_disk_caching

                if self.capacity and \
                   self.capacity != vmss_dict['sku']['capacity']:
                    self.log('CHANGED: virtual machine scale set {0} - Capacity'.format(self.name))
                    differences.append('Capacity')
                    changed = True
                    vmss_dict['sku']['capacity'] = self.capacity

                if self.data_disks and \
                   len(self.data_disks) != len(vmss_dict['properties']['virtualMachineProfile']['storageProfile'].get('dataDisks', [])):
                    self.log('CHANGED: virtual machine scale set {0} - Data Disks'.format(self.name))
                    differences.append('Data Disks')
                    changed = True

                if self.upgrade_policy and \
                   self.upgrade_policy != vmss_dict['properties']['upgradePolicy']['mode']:
                    self.log('CHANGED: virtual machine scale set {0} - Upgrade Policy'.format(self.name))
                    differences.append('Upgrade Policy')
                    changed = True
                    vmss_dict['properties']['upgradePolicy']['mode'] = self.upgrade_policy

                if image_reference and \
                   image_reference.as_dict() != vmss_dict['properties']['virtualMachineProfile']['storageProfile']['imageReference']:
                    self.log('CHANGED: virtual machine scale set {0} - Image'.format(self.name))
                    differences.append('Image')
                    changed = True
                    vmss_dict['properties']['virtualMachineProfile']['storageProfile']['imageReference'] = image_reference.as_dict()

                update_tags, vmss_dict['tags'] = self.update_tags(vmss_dict.get('tags', dict()))
                if update_tags:
                    differences.append('Tags')
                    changed = True

                if bool(self.overprovision) != bool(vmss_dict['properties']['overprovision']):
                    differences.append('overprovision')
                    changed = True

                if bool(self.single_placement_group) != bool(vmss_dict['properties']['singlePlacementGroup']):
                    differences.append('single_placement_group')
                    changed = True

                vmss_dict['zones'] = [int(i) for i in vmss_dict['zones']] if 'zones' in vmss_dict and vmss_dict['zones'] else None
                if self.zones != vmss_dict['zones']:
                    self.log("CHANGED: virtual machine scale sets {0} zones".format(self.name))
                    differences.append('Zones')
                    changed = True
                    vmss_dict['zones'] = self.zones

                if self.terminate_event_timeout_minutes:
                    timeout = self.terminate_event_timeout_minutes
                    if timeout < 5 or timeout > 15:
                        self.fail("terminate_event_timeout_minutes should >= 5 and <= 15")
                    iso_8601_format = "PT" + str(timeout) + "M"
                    old = vmss_dict['properties']['virtualMachineProfile'].get('scheduledEventsProfile', {}).\
                        get('terminateNotificationProfile', {}).get('notBeforeTimeout', "")
                    if old != iso_8601_format:
                        differences.append('terminateNotification')
                        changed = True
                        vmss_dict['properties']['virtualMachineProfile'].setdefault('scheduledEventsProfile', {})['terminateNotificationProfile'] = {
                            'notBeforeTimeout': iso_8601_format,
                            "enable": 'true'
                        }

                if self.scale_in_policy and self.scale_in_policy != vmss_dict['properties'].get('scaleInPolicy', {}).get('rules', [""])[0]:
                    self.log("CHANGED: virtual machine sale sets {0} scale in policy".format(self.name))
                    differences.append('scaleInPolicy')
                    changed = True
                    vmss_dict['properties'].setdefault('scaleInPolicy', {})['rules'] = [self.scale_in_policy]

                nicConfigs = vmss_dict['properties']['virtualMachineProfile']['networkProfile']['networkInterfaceConfigurations']

                backend_address_pool = nicConfigs[0]['properties']['ipConfigurations'][0]['properties'].get('loadBalancerBackendAddressPools', [])
                backend_address_pool += nicConfigs[0]['properties']['ipConfigurations'][0]['properties'].get('applicationGatewayBackendAddressPools', [])
                lb_or_ag_id = None
                if (len(nicConfigs) != 1 or len(backend_address_pool) != 1):
                    support_lb_change = False  # Currently not support for the vmss contains more than one loadbalancer
                    self.module.warn('Updating more than one load balancer on VMSS is currently not supported')
                else:
                    if load_balancer:
                        lb_or_ag_id = "{0}/".format(load_balancer.id)
                    elif application_gateway:
                        lb_or_ag_id = "{0}/".format(application_gateway.id)

                    backend_address_pool_id = backend_address_pool[0].get('id')
                    if lb_or_ag_id is not None and (bool(lb_or_ag_id) != bool(backend_address_pool_id) or not backend_address_pool_id.startswith(lb_or_ag_id)):
                        differences.append('load_balancer')
                        changed = True

                if self.custom_data:
                    if self.custom_data != vmss_dict['properties']['virtualMachineProfile']['osProfile'].get('customData'):
                        differences.append('custom_data')
                        changed = True
                        vmss_dict['properties']['virtualMachineProfile']['osProfile']['customData'] = self.custom_data

                self.differences = differences

            elif self.state == 'absent':
                self.log("CHANGED: virtual machine scale set {0} exists and requested state is 'absent'".format(self.name))
                results = dict()
                changed = True

        except CloudError:
            self.log('Virtual machine scale set {0} does not exist'.format(self.name))
            if self.state == 'present':
                self.log("CHANGED: virtual machine scale set {0} does not exist but state is 'present'.".format(self.name))
                changed = True

        self.results['changed'] = changed
        self.results['ansible_facts']['azure_vmss'] = results

        if self.check_mode:
            return self.results

        if changed:
            if self.state == 'present':
                if not vmss:
                    # Create the VMSS
                    if self.vm_size is None:
                        self.fail("vm size must be set")

                    self.log("Create virtual machine scale set {0}".format(self.name))
                    self.results['actions'].append('Created VMSS {0}'.format(self.name))

                    if self.os_type == 'Linux':
                        if disable_ssh_password and not self.ssh_public_keys:
                            self.fail("Parameter error: ssh_public_keys required when disabling SSH password.")

                    if not self.virtual_network_name:
                        self.fail("virtual network name is required")

                    if self.subnet_name:
                        subnet = self.get_subnet(self.virtual_network_name, self.subnet_name)

                    if not self.short_hostname:
                        self.short_hostname = self.name

                    if not image_reference:
                        self.fail("Parameter error: an image is required when creating a virtual machine.")

                    managed_disk = self.compute_models.VirtualMachineScaleSetManagedDiskParameters(storage_account_type=self.managed_disk_type)

                    if self.security_group:
                        nsg = self.parse_nsg()
                        if nsg:
                            self.security_group = self.network_models.NetworkSecurityGroup(id=nsg.get('id'))

                    plan = None
                    if self.plan:
                        plan = self.compute_models.Plan(name=self.plan.get('name'), product=self.plan.get('product'),
                                                        publisher=self.plan.get('publisher'),
                                                        promotion_code=self.plan.get('promotion_code'))

                    os_profile = None
                    if self.admin_username or self.custom_data or self.ssh_public_keys:
                        os_profile = self.compute_models.VirtualMachineScaleSetOSProfile(
                            admin_username=self.admin_username,
                            computer_name_prefix=self.short_hostname,
                            custom_data=self.custom_data
                        )

                    vmss_resource = self.compute_models.VirtualMachineScaleSet(
                        location=self.location,
                        overprovision=self.overprovision,
                        single_placement_group=self.single_placement_group,
                        tags=self.tags,
                        upgrade_policy=self.compute_models.UpgradePolicy(
                            mode=self.upgrade_policy
                        ),
                        sku=self.compute_models.Sku(
                            name=self.vm_size,
                            capacity=self.capacity,
                            tier=self.tier,
                        ),
                        plan=plan,
                        virtual_machine_profile=self.compute_models.VirtualMachineScaleSetVMProfile(
                            os_profile=os_profile,
                            storage_profile=self.compute_models.VirtualMachineScaleSetStorageProfile(
                                os_disk=self.compute_models.VirtualMachineScaleSetOSDisk(
                                    managed_disk=managed_disk,
                                    create_option=self.compute_models.DiskCreateOptionTypes.from_image,
                                    caching=self.os_disk_caching,
                                ),
                                image_reference=image_reference,
                            ),
                            network_profile=self.compute_models.VirtualMachineScaleSetNetworkProfile(
                                network_interface_configurations=[
                                    self.compute_models.VirtualMachineScaleSetNetworkConfiguration(
                                        name=self.name,
                                        primary=True,
                                        ip_configurations=[
                                            self.compute_models.VirtualMachineScaleSetIPConfiguration(
                                                name='default',
                                                subnet=self.compute_models.ApiEntityReference(
                                                    id=subnet.id
                                                ),
                                                primary=True,
                                                load_balancer_backend_address_pools=load_balancer_backend_address_pools,
                                                load_balancer_inbound_nat_pools=load_balancer_inbound_nat_pools,
                                                application_gateway_backend_address_pools=application_gateway_backend_address_pools
                                            )
                                        ],
                                        enable_accelerated_networking=self.enable_accelerated_networking,
                                        network_security_group=self.security_group
                                    )
                                ]
                            )
                        ),
                        zones=self.zones
                    )

                    if self.scale_in_policy:
                        vmss_resource.scale_in_policy = self.gen_scale_in_policy()

                    if self.terminate_event_timeout_minutes:
                        vmss_resource.virtual_machine_profile.scheduled_events_profile = self.gen_scheduled_event_profile()

                    if self.admin_password:
                        vmss_resource.virtual_machine_profile.os_profile.admin_password = self.admin_password

                    if self.os_type == 'Linux' and os_profile:
                        vmss_resource.virtual_machine_profile.os_profile.linux_configuration = self.compute_models.LinuxConfiguration(
                            disable_password_authentication=disable_ssh_password
                        )

                    if self.ssh_public_keys:
                        ssh_config = self.compute_models.SshConfiguration()
                        ssh_config.public_keys = \
                            [self.compute_models.SshPublicKey(path=key['path'], key_data=key['key_data']) for key in self.ssh_public_keys]
                        vmss_resource.virtual_machine_profile.os_profile.linux_configuration.ssh = ssh_config

                    if self.data_disks:
                        data_disks = []

                        for data_disk in self.data_disks:
                            data_disk_managed_disk = self.compute_models.VirtualMachineScaleSetManagedDiskParameters(
                                storage_account_type=data_disk.get('managed_disk_type', None)
                            )

                            data_disk['caching'] = data_disk.get(
                                'caching',
                                self.compute_models.CachingTypes.read_only
                            )

                            data_disks.append(self.compute_models.VirtualMachineScaleSetDataDisk(
                                lun=data_disk.get('lun', None),
                                caching=data_disk.get('caching', None),
                                create_option=self.compute_models.DiskCreateOptionTypes.empty,
                                disk_size_gb=data_disk.get('disk_size_gb', None),
                                managed_disk=data_disk_managed_disk,
                            ))

                        vmss_resource.virtual_machine_profile.storage_profile.data_disks = data_disks

                    if self.plan:
                        try:
                            plan_name = self.plan.get('name')
                            plan_product = self.plan.get('product')
                            plan_publisher = self.plan.get('publisher')
                            term = self.marketplace_client.marketplace_agreements.get(
                                publisher_id=plan_publisher, offer_id=plan_product, plan_id=plan_name)
                            term.accepted = True
                            self.marketplace_client.marketplace_agreements.create(
                                publisher_id=plan_publisher, offer_id=plan_product, plan_id=plan_name, parameters=term)
                        except Exception as exc:
                            self.fail(("Error accepting terms for virtual machine {0} with plan {1}. " +
                                       "Only service admin/account admin users can purchase images " +
                                       "from the marketplace. - {2}").format(self.name, self.plan, str(exc)))

                    self.log("Create virtual machine with parameters:")
                    self.create_or_update_vmss(vmss_resource)

                elif self.differences and len(self.differences) > 0:
                    self.log("Update virtual machine scale set {0}".format(self.name))
                    self.results['actions'].append('Updated VMSS {0}'.format(self.name))

                    vmss_resource = self.get_vmss()
                    vmss_resource.virtual_machine_profile.storage_profile.os_disk.caching = self.os_disk_caching
                    vmss_resource.sku.capacity = self.capacity
                    vmss_resource.overprovision = self.overprovision
                    vmss_resource.single_placement_group = self.single_placement_group

                    if support_lb_change:
                        if self.load_balancer:
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].load_balancer_backend_address_pools = load_balancer_backend_address_pools
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].load_balancer_inbound_nat_pools = load_balancer_inbound_nat_pools
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].application_gateway_backend_address_pools = None
                        elif self.application_gateway:
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].application_gateway_backend_address_pools = application_gateway_backend_address_pools
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].load_balancer_backend_address_pools = None
                            vmss_resource.virtual_machine_profile.network_profile.network_interface_configurations[0] \
                                .ip_configurations[0].load_balancer_inbound_nat_pools = None

                    if self.data_disks is not None:
                        data_disks = []
                        for data_disk in self.data_disks:
                            data_disks.append(self.compute_models.VirtualMachineScaleSetDataDisk(
                                lun=data_disk['lun'],
                                caching=data_disk['caching'],
                                create_option=self.compute_models.DiskCreateOptionTypes.empty,
                                disk_size_gb=data_disk['disk_size_gb'],
                                managed_disk=self.compute_models.VirtualMachineScaleSetManagedDiskParameters(
                                    storage_account_type=data_disk.get('managed_disk_type', None)
                                ),
                            ))
                        vmss_resource.virtual_machine_profile.storage_profile.data_disks = data_disks

                    if self.scale_in_policy:
                        vmss_resource.scale_in_policy = self.gen_scale_in_policy()

                    if self.terminate_event_timeout_minutes:
                        vmss_resource.virtual_machine_profile.scheduled_events_profile = self.gen_scheduled_event_profile()

                    if image_reference is not None:
                        vmss_resource.virtual_machine_profile.storage_profile.image_reference = image_reference
                    self.log("Update virtual machine with parameters:")
                    self.create_or_update_vmss(vmss_resource)

                self.results['ansible_facts']['azure_vmss'] = self.serialize_vmss(self.get_vmss())

            elif self.state == 'absent':
                # delete the VM
                self.log("Delete virtual machine scale set {0}".format(self.name))
                self.results['ansible_facts']['azure_vmss'] = None
                self.delete_vmss(vmss)

        # until we sort out how we want to do this globally
        del self.results['actions']

        return self.results

    def get_vmss(self):
        '''
        Get the VMSS

        :return: VirtualMachineScaleSet object
        '''
        try:
            vmss = self.compute_client.virtual_machine_scale_sets.get(self.resource_group, self.name)
            return vmss
        except CloudError as exc:
            self.fail("Error getting virtual machine scale set {0} - {1}".format(self.name, str(exc)))

    def get_virtual_network(self, name):
        try:
            vnet = self.network_client.virtual_networks.get(self.virtual_network_resource_group, name)
            return vnet
        except CloudError as exc:
            self.fail("Error fetching virtual network {0} - {1}".format(name, str(exc)))

    def get_subnet(self, vnet_name, subnet_name):
        self.log("Fetching subnet {0} in virtual network {1}".format(subnet_name, vnet_name))
        try:
            subnet = self.network_client.subnets.get(self.virtual_network_resource_group, vnet_name, subnet_name)
        except CloudError as exc:
            self.fail("Error: fetching subnet {0} in virtual network {1} - {2}".format(
                subnet_name,
                vnet_name,
                str(exc)))
        return subnet

    def get_load_balancer(self, id):
        id_dict = parse_resource_id(id)
        try:
            return self.network_client.load_balancers.get(id_dict.get('resource_group', self.resource_group), id_dict.get('name'))
        except CloudError as exc:
            self.fail("Error fetching load balancer {0} - {1}".format(id, str(exc)))

    def get_application_gateway(self, id):
        id_dict = parse_resource_id(id)
        try:
            return self.network_client.application_gateways.get(id_dict.get('resource_group', self.resource_group), id_dict.get('name'))
        except CloudError as exc:
            self.fail("Error fetching application_gateway {0} - {1}".format(id, str(exc)))

    def serialize_vmss(self, vmss):
        '''
        Convert a VirtualMachineScaleSet object to dict.

        :param vm: VirtualMachineScaleSet object
        :return: dict
        '''

        result = self.serialize_obj(vmss, AZURE_OBJECT_CLASS, enum_modules=AZURE_ENUM_MODULES)
        result['id'] = vmss.id
        result['name'] = vmss.name
        result['type'] = vmss.type
        result['location'] = vmss.location
        result['tags'] = vmss.tags

        return result

    def delete_vmss(self, vmss):
        self.log("Deleting virtual machine scale set {0}".format(self.name))
        self.results['actions'].append("Deleted virtual machine scale set {0}".format(self.name))
        try:
            poller = self.compute_client.virtual_machine_scale_sets.delete(self.resource_group, self.name)
            # wait for the poller to finish
            self.get_poller_result(poller)
        except CloudError as exc:
            self.fail("Error deleting virtual machine scale set {0} - {1}".format(self.name, str(exc)))

        return True

    def get_marketplace_image_version(self):
        try:
            versions = self.compute_client.virtual_machine_images.list(self.location,
                                                                       self.image['publisher'],
                                                                       self.image['offer'],
                                                                       self.image['sku'])
        except CloudError as exc:
            self.fail("Error fetching image {0} {1} {2} - {3}".format(self.image['publisher'],
                                                                      self.image['offer'],
                                                                      self.image['sku'],
                                                                      str(exc)))
        if versions and len(versions) > 0:
            if self.image['version'] == 'latest':
                return versions[len(versions) - 1]
            for version in versions:
                if version.name == self.image['version']:
                    return version

        self.fail("Error could not find image {0} {1} {2} {3}".format(self.image['publisher'],
                                                                      self.image['offer'],
                                                                      self.image['sku'],
                                                                      self.image['version']))

    def get_custom_image_reference(self, name, resource_group=None):
        try:
            if resource_group:
                vm_images = self.compute_client.images.list_by_resource_group(resource_group)
            else:
                vm_images = self.compute_client.images.list()
        except Exception as exc:
            self.fail("Error fetching custom images from subscription - {0}".format(str(exc)))

        for vm_image in vm_images:
            if vm_image.name == name:
                self.log("Using custom image id {0}".format(vm_image.id))
                return self.compute_models.ImageReference(id=vm_image.id)

        self.fail("Error could not find image with name {0}".format(name))

    def create_or_update_vmss(self, params):
        try:
            poller = self.compute_client.virtual_machine_scale_sets.create_or_update(self.resource_group, self.name, params)
            self.get_poller_result(poller)
        except CloudError as exc:
            self.fail("Error creating or updating virtual machine {0} - {1}".format(self.name, str(exc)))

    def vm_size_is_valid(self):
        '''
        Validate self.vm_size against the list of virtual machine sizes available for the account and location.

        :return: boolean
        '''
        try:
            sizes = self.compute_client.virtual_machine_sizes.list(self.location)
        except CloudError as exc:
            self.fail("Error retrieving available machine sizes - {0}".format(str(exc)))
        for size in sizes:
            if size.name == self.vm_size:
                return True
        return False

    def parse_nsg(self):
        nsg = self.security_group
        resource_group = self.resource_group
        if isinstance(self.security_group, dict):
            nsg = self.security_group.get('name')
            resource_group = self.security_group.get('resource_group', self.resource_group)
        id = format_resource_id(val=nsg,
                                subscription_id=self.subscription_id,
                                namespace='Microsoft.Network',
                                types='networkSecurityGroups',
                                resource_group=resource_group)
        name = azure_id_to_dict(id).get('name')
        return dict(id=id, name=name)

    def gen_scheduled_event_profile(self):
        if self.terminate_event_timeout_minutes is None:
            return None

        scheduledEventProfile = self.compute_models.ScheduledEventsProfile()
        terminationProfile = self.compute_models.TerminateNotificationProfile()
        terminationProfile.not_before_timeout = "PT" + str(self.terminate_event_timeout_minutes) + "M"
        terminationProfile.enable = True
        scheduledEventProfile.terminate_notification_profile = terminationProfile
        return scheduledEventProfile

    def gen_scale_in_policy(self):
        if self.scale_in_policy is None:
            return None

        return self.compute_models.ScaleInPolicy(rules=[self.scale_in_policy])


def main():
    AzureRMVirtualMachineScaleSet()


if __name__ == '__main__':
    main()
