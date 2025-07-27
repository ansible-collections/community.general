#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: redfish_config
short_description: Manages Out-Of-Band controllers using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to set or update a configuration attribute.
  - Manages BIOS configuration settings.
  - Manages OOB controller configuration settings.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.redfish
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller.
    type: str
  command:
    required: true
    description:
      - List of commands to execute on OOB controller.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller.
    type: str
  username:
    description:
      - Username for authenticating to OOB controller.
    type: str
  password:
    description:
      - Password for authenticating to OOB controller.
    type: str
  auth_token:
    description:
      - Security token for authenticating to OOB controller.
    type: str
    version_added: 2.3.0
  bios_attributes:
    required: false
    description:
      - Dictionary of BIOS attributes to update.
    default: {}
    type: dict
    version_added: '0.2.0'
  timeout:
    description:
      - Timeout in seconds for HTTP requests to OOB controller.
      - The default value for this parameter changed from V(10) to V(60) in community.general 9.0.0.
    type: int
    default: 60
  boot_order:
    required: false
    description:
      - List of BootOptionReference strings specifying the BootOrder.
    default: []
    type: list
    elements: str
    version_added: '0.2.0'
  network_protocols:
    required: false
    description:
      - Setting dict of manager services to update.
    type: dict
    default: {}
    version_added: '0.2.0'
  resource_id:
    required: false
    description:
      - ID of the System, Manager or Chassis to modify.
    type: str
    version_added: '0.2.0'
  service_id:
    required: false
    description:
      - ID of the manager to update.
    type: str
    version_added: '8.4.0'
  nic_addr:
    required: false
    description:
      - EthernetInterface Address string on OOB controller.
    default: 'null'
    type: str
    version_added: '0.2.0'
  nic_config:
    required: false
    description:
      - Setting dict of EthernetInterface on OOB controller.
    type: dict
    default: {}
    version_added: '0.2.0'
  strip_etag_quotes:
    description:
      - Removes surrounding quotes of etag used in C(If-Match) header of C(PATCH) requests.
      - Only use this option to resolve bad vendor implementation where C(If-Match) only matches the unquoted etag string.
    type: bool
    default: false
    version_added: 3.7.0
  hostinterface_config:
    required: false
    description:
      - Setting dict of HostInterface on OOB controller.
    type: dict
    default: {}
    version_added: '4.1.0'
  hostinterface_id:
    required: false
    description:
      - Redfish HostInterface instance ID if multiple HostInterfaces are present.
    type: str
    version_added: '4.1.0'
  sessions_config:
    required: false
    description:
      - Setting dict of Sessions.
    type: dict
    default: {}
    version_added: '5.7.0'
  storage_subsystem_id:
    required: false
    description:
      - ID of the Storage Subsystem on which the volume is to be created.
    type: str
    default: ''
    version_added: '7.3.0'
  storage_none_volume_deletion:
    required: false
    description:
      - Indicates if all non-RAID volumes are automatically deleted prior to creating the new volume.
    type: bool
    default: false
    version_added: '9.5.0'
  volume_ids:
    required: false
    description:
      - List of IDs of volumes to be deleted.
    type: list
    default: []
    elements: str
    version_added: '7.3.0'
  secure_boot_enable:
    required: false
    description:
      - Setting parameter to enable or disable SecureBoot.
    type: bool
    default: true
    version_added: '7.5.0'
  volume_details:
    required: false
    description:
      - Setting dictionary of volume to be created.
      - If C(CapacityBytes) key is not specified in this dictionary, the size of the volume is determined by the Redfish service.
        It is possible the size is not the maximum available size.
    type: dict
    default: {}
    version_added: '7.5.0'
  power_restore_policy:
    description:
      - The desired power state of the system when power is restored after a power loss.
    type: str
    choices:
      - AlwaysOn
      - AlwaysOff
      - LastState
    version_added: '10.5.0'
  ciphers:
    version_added: 9.2.0
  validate_certs:
    version_added: 10.6.0
  ca_path:
    version_added: 10.6.0

author:
  - "Jose Delarosa (@jose-delarosa)"
  - "T S Kushal (@TSKushal)"
"""

EXAMPLES = r"""
- name: Set BootMode to UEFI
  community.general.redfish_config:
    category: Systems
    command: SetBiosAttributes
    resource_id: 437XR1138R2
    bios_attributes:
      BootMode: "Uefi"
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set multiple BootMode attributes
  community.general.redfish_config:
    category: Systems
    command: SetBiosAttributes
    resource_id: 437XR1138R2
    bios_attributes:
      BootMode: "Bios"
      OneTimeBootMode: "Enabled"
      BootSeqRetry: "Enabled"
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Enable PXE Boot for NIC1
  community.general.redfish_config:
    category: Systems
    command: SetBiosAttributes
    resource_id: 437XR1138R2
    bios_attributes:
      PxeDev1EnDis: Enabled
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set BIOS default settings with a timeout of 20 seconds
  community.general.redfish_config:
    category: Systems
    command: SetBiosDefaultSettings
    resource_id: 437XR1138R2
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    timeout: 20

- name: Set boot order
  community.general.redfish_config:
    category: Systems
    command: SetBootOrder
    boot_order:
      - Boot0002
      - Boot0001
      - Boot0000
      - Boot0003
      - Boot0004
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set boot order to the default
  community.general.redfish_config:
    category: Systems
    command: SetDefaultBootOrder
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set Manager Network Protocols
  community.general.redfish_config:
    category: Manager
    command: SetNetworkProtocols
    network_protocols:
      SNMP:
        ProtocolEnabled: true
        Port: 161
      HTTP:
        ProtocolEnabled: false
        Port: 8080
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set Manager NIC
  community.general.redfish_config:
    category: Manager
    command: SetManagerNic
    nic_config:
      DHCPv4:
        DHCPEnabled: false
      IPv4StaticAddresses:
        Address: 192.168.1.3
        Gateway: 192.168.1.1
        SubnetMask: 255.255.255.0
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Disable Host Interface
  community.general.redfish_config:
    category: Manager
    command: SetHostInterface
    hostinterface_config:
      InterfaceEnabled: false
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Enable Host Interface for HostInterface resource ID '2'
  community.general.redfish_config:
    category: Manager
    command: SetHostInterface
    hostinterface_config:
      InterfaceEnabled: true
    hostinterface_id: "2"
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set SessionService Session Timeout to 30 minutes
  community.general.redfish_config:
    category: Sessions
    command: SetSessionService
    sessions_config:
      SessionTimeout: 1800
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Enable SecureBoot
  community.general.redfish_config:
    category: Systems
    command: EnableSecureBoot
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"

- name: Set SecureBoot
  community.general.redfish_config:
    category: Systems
    command: SetSecureBoot
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    secure_boot_enable: true

- name: Delete All Volumes
  community.general.redfish_config:
    category: Systems
    command: DeleteVolumes
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    storage_subsystem_id: "DExxxxxx"
    volume_ids: ["volume1", "volume2"]

- name: Create Volume
  community.general.redfish_config:
    category: Systems
    command: CreateVolume
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    storage_subsystem_id: "DExxxxxx"
    volume_details:
      Name: "MR Volume"
      RAIDType: "RAID0"
      Drives:
        - "/redfish/v1/Systems/1/Storage/DE00B000/Drives/1"

- name: Set PowerRestorePolicy
  community.general.redfish_config:
    category: Systems
    command: SetPowerRestorePolicy
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
    power_restore_policy: "AlwaysOff"

- name: Set service identification to {{ service_id }}
  community.general.redfish_config:
    category: Manager
    command: SetServiceIdentification
    service_id: "{{ service_id }}"
    baseuri: "{{ baseuri }}"
    username: "{{ username }}"
    password: "{{ password }}"
"""

RETURN = r"""
msg:
  description: Message with action result or error description.
  returned: always
  type: str
  sample: "Action was successful"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils, REDFISH_COMMON_ARGUMENT_SPEC
from ansible.module_utils.common.text.converters import to_native


# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["SetBiosDefaultSettings", "SetBiosAttributes", "SetBootOrder",
                "SetDefaultBootOrder", "EnableSecureBoot", "SetSecureBoot", "DeleteVolumes", "CreateVolume",
                "SetPowerRestorePolicy"],
    "Manager": ["SetNetworkProtocols", "SetManagerNic", "SetHostInterface", "SetServiceIdentification"],
    "Sessions": ["SetSessionService"],
}


def main():
    result = {}
    argument_spec = dict(
        category=dict(required=True),
        command=dict(required=True, type='list', elements='str'),
        baseuri=dict(required=True),
        username=dict(),
        password=dict(no_log=True),
        auth_token=dict(no_log=True),
        bios_attributes=dict(type='dict', default={}),
        timeout=dict(type='int', default=60),
        boot_order=dict(type='list', elements='str', default=[]),
        network_protocols=dict(
            type='dict',
            default={}
        ),
        resource_id=dict(),
        service_id=dict(),
        nic_addr=dict(default='null'),
        nic_config=dict(
            type='dict',
            default={}
        ),
        strip_etag_quotes=dict(type='bool', default=False),
        hostinterface_config=dict(type='dict', default={}),
        hostinterface_id=dict(),
        sessions_config=dict(type='dict', default={}),
        storage_subsystem_id=dict(type='str', default=''),
        storage_none_volume_deletion=dict(type='bool', default=False),
        volume_ids=dict(type='list', default=[], elements='str'),
        secure_boot_enable=dict(type='bool', default=True),
        volume_details=dict(type='dict', default={}),
        power_restore_policy=dict(choices=['AlwaysOn', 'AlwaysOff', 'LastState']),
    )
    argument_spec.update(REDFISH_COMMON_ARGUMENT_SPEC)
    module = AnsibleModule(
        argument_spec,
        required_together=[
            ('username', 'password'),
        ],
        required_one_of=[
            ('username', 'auth_token'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token'),
        ],
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # BIOS attributes to update
    bios_attributes = module.params['bios_attributes']

    # boot order
    boot_order = module.params['boot_order']

    # System, Manager or Chassis ID to modify
    resource_id = module.params['resource_id']

    # manager nic
    nic_addr = module.params['nic_addr']
    nic_config = module.params['nic_config']

    # Etag options
    strip_etag_quotes = module.params['strip_etag_quotes']

    # HostInterface config options
    hostinterface_config = module.params['hostinterface_config']

    # HostInterface instance ID
    hostinterface_id = module.params['hostinterface_id']

    # Service Identification
    service_id = module.params['service_id']

    # Sessions config options
    sessions_config = module.params['sessions_config']

    # Volume deletion options
    storage_subsystem_id = module.params['storage_subsystem_id']
    volume_ids = module.params['volume_ids']

    # Set SecureBoot options
    secure_boot_enable = module.params['secure_boot_enable']

    # Volume creation options
    volume_details = module.params['volume_details']
    storage_subsystem_id = module.params['storage_subsystem_id']
    storage_none_volume_deletion = module.params['storage_none_volume_deletion']

    # Power Restore Policy
    power_restore_policy = module.params['power_restore_policy']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_utils = RedfishUtils(creds, root_uri, timeout, module,
                            resource_id=resource_id, data_modification=True, strip_etag_quotes=strip_etag_quotes)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # Organize by Categories / Commands
    if category == "Systems":
        # execute only if we find a System resource
        result = rf_utils._find_systems_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "SetBiosDefaultSettings":
                result = rf_utils.set_bios_default_settings()
            elif command == "SetBiosAttributes":
                result = rf_utils.set_bios_attributes(bios_attributes)
            elif command == "SetBootOrder":
                result = rf_utils.set_boot_order(boot_order)
            elif command == "SetDefaultBootOrder":
                result = rf_utils.set_default_boot_order()
            elif command == "EnableSecureBoot":
                result = rf_utils.enable_secure_boot()
            elif command == "SetSecureBoot":
                result = rf_utils.set_secure_boot(secure_boot_enable)
            elif command == "DeleteVolumes":
                result = rf_utils.delete_volumes(storage_subsystem_id, volume_ids)
            elif command == "CreateVolume":
                result = rf_utils.create_volume(volume_details, storage_subsystem_id, storage_none_volume_deletion)
            elif command == "SetPowerRestorePolicy":
                result = rf_utils.set_power_restore_policy(power_restore_policy)

    elif category == "Manager":
        # execute only if we find a Manager service resource
        result = rf_utils._find_managers_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "SetNetworkProtocols":
                result = rf_utils.set_network_protocols(module.params['network_protocols'])
            elif command == "SetManagerNic":
                result = rf_utils.set_manager_nic(nic_addr, nic_config)
            elif command == "SetHostInterface":
                result = rf_utils.set_hostinterface_attributes(hostinterface_config, hostinterface_id)
            elif command == "SetServiceIdentification":
                result = rf_utils.set_service_identification(service_id)

    elif category == "Sessions":
        # execute only if we find a Sessions resource
        result = rf_utils._find_sessionservice_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command == "SetSessionService":
                result = rf_utils.set_session_service(sessions_config)

    # Return data back or fail with proper message
    if result['ret'] is True:
        if result.get('warning'):
            module.warn(to_native(result['warning']))

        module.exit_json(changed=result['changed'], msg=to_native(result['msg']))
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
