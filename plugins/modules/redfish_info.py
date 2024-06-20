#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redfish_info
short_description: Manages Out-Of-Band controllers using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    get information back.
  - Information retrieved is placed in a location specified by the user.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  category:
    required: false
    description:
      - List of categories to execute on OOB controller.
    default: ['Systems']
    type: list
    elements: str
  command:
    required: false
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
  manager:
    description:
      - Name of manager on OOB controller to target.
    type: str
    version_added: '8.3.0'
  timeout:
    description:
      - Timeout in seconds for HTTP requests to OOB controller.
      - The default value for this parameter changed from V(10) to V(60)
        in community.general 9.0.0.
    type: int
    default: 60
  update_handle:
    required: false
    description:
      - Handle to check the status of an update in progress.
    type: str
    version_added: '6.1.0'
  ciphers:
    required: false
    description:
      - SSL/TLS Ciphers to use for the request.
      - 'When a list is provided, all ciphers are joined in order with V(:).'
      - See the L(OpenSSL Cipher List Format,https://www.openssl.org/docs/manmaster/man1/openssl-ciphers.html#CIPHER-LIST-FORMAT)
        for more details.
      - The available ciphers is dependent on the Python and OpenSSL/LibreSSL versions.
    type: list
    elements: str
    version_added: 9.2.0

author: "Jose Delarosa (@jose-delarosa)"
'''

EXAMPLES = '''
  - name: Get CPU inventory
    community.general.redfish_info:
      category: Systems
      command: GetCpuInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.cpu.entries | to_nice_json }}"

  - name: Get CPU model
    community.general.redfish_info:
      category: Systems
      command: GetCpuInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.cpu.entries.0.Model }}"

  - name: Get memory inventory
    community.general.redfish_info:
      category: Systems
      command: GetMemoryInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Get fan inventory with a timeout of 20 seconds
    community.general.redfish_info:
      category: Chassis
      command: GetFanInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      timeout: 20
    register: result

  - name: Get Virtual Media information
    community.general.redfish_info:
      category: Manager
      command: GetVirtualMedia
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.virtual_media.entries | to_nice_json }}"

  - name: Get Virtual Media information from Systems
    community.general.redfish_info:
      category: Systems
      command: GetVirtualMedia
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.virtual_media.entries | to_nice_json }}"

  - name: Get Volume Inventory
    community.general.redfish_info:
      category: Systems
      command: GetVolumeInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result
  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.volume.entries | to_nice_json }}"

  - name: Get Session information
    community.general.redfish_info:
      category: Sessions
      command: GetSessions
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts.session.entries | to_nice_json }}"

  - name: Get default inventory information
    community.general.redfish_info:
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result
  - name: Print fetched information
    ansible.builtin.debug:
      msg: "{{ result.redfish_facts | to_nice_json }}"

  - name: Get several inventories
    community.general.redfish_info:
      category: Systems
      command: GetNicInventory,GetBiosAttributes
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get default system inventory and user information
    community.general.redfish_info:
      category: Systems,Accounts
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get default system, user and firmware information
    community.general.redfish_info:
      category: ["Systems", "Accounts", "Update"]
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get Manager NIC inventory information
    community.general.redfish_info:
      category: Manager
      command: GetManagerNicInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get boot override information
    community.general.redfish_info:
      category: Systems
      command: GetBootOverride
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get chassis inventory
    community.general.redfish_info:
      category: Chassis
      command: GetChassisInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get all information available in the Manager category
    community.general.redfish_info:
      category: Manager
      command: all
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get firmware update capability information
    community.general.redfish_info:
      category: Update
      command: GetFirmwareUpdateCapabilities
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get firmware inventory
    community.general.redfish_info:
      category: Update
      command: GetFirmwareInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get service identification
    community.general.redfish_info:
      category: Manager
      command: GetServiceIdentification
      manager: "{{ manager }}"
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get software inventory
    community.general.redfish_info:
      category: Update
      command: GetSoftwareInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get the status of an update operation
    community.general.redfish_info:
      category: Update
      command: GetUpdateStatus
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      update_handle: /redfish/v1/TaskService/TaskMonitors/735

  - name: Get Manager Services
    community.general.redfish_info:
      category: Manager
      command: GetNetworkProtocols
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get all information available in all categories
    community.general.redfish_info:
      category: all
      command: all
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get system health report
    community.general.redfish_info:
      category: Systems
      command: GetHealthReport
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get chassis health report
    community.general.redfish_info:
      category: Chassis
      command: GetHealthReport
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get manager health report
    community.general.redfish_info:
      category: Manager
      command: GetHealthReport
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get manager Redfish Host Interface inventory
    community.general.redfish_info:
      category: Manager
      command: GetHostInterfaces
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get Manager Inventory
    community.general.redfish_info:
      category: Manager
      command: GetManagerInventory
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get HPE Thermal Config
    community.general.redfish_info:
      category: Chassis
      command: GetHPEThermalConfig
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get HPE Fan Percent Minimum
    community.general.redfish_info:
      category: Chassis
      command: GetHPEFanPercentMin
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Get BIOS registry
    community.general.redfish_info:
      category: Systems
      command: GetBiosRegistries
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Check the availability of the service with a timeout of 5 seconds
    community.general.redfish_info:
      category: Service
      command: CheckAvailability
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      timeout: 5
    register: result
'''

RETURN = '''
result:
    description: different results depending on task
    returned: always
    type: dict
    sample: List of CPUs on system
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils

CATEGORY_COMMANDS_ALL = {
    "Systems": ["GetSystemInventory", "GetPsuInventory", "GetCpuInventory",
                "GetMemoryInventory", "GetNicInventory", "GetHealthReport",
                "GetStorageControllerInventory", "GetDiskInventory", "GetVolumeInventory",
                "GetBiosAttributes", "GetBootOrder", "GetBootOverride", "GetVirtualMedia", "GetBiosRegistries"],
    "Chassis": ["GetFanInventory", "GetPsuInventory", "GetChassisPower",
                "GetChassisThermals", "GetChassisInventory", "GetHealthReport", "GetHPEThermalConfig", "GetHPEFanPercentMin"],
    "Accounts": ["ListUsers"],
    "Sessions": ["GetSessions"],
    "Update": ["GetFirmwareInventory", "GetFirmwareUpdateCapabilities", "GetSoftwareInventory",
               "GetUpdateStatus"],
    "Manager": ["GetManagerNicInventory", "GetVirtualMedia", "GetLogs", "GetNetworkProtocols",
                "GetHealthReport", "GetHostInterfaces", "GetManagerInventory", "GetServiceIdentification"],
    "Service": ["CheckAvailability"],
}

CATEGORY_COMMANDS_DEFAULT = {
    "Systems": "GetSystemInventory",
    "Chassis": "GetFanInventory",
    "Accounts": "ListUsers",
    "Update": "GetFirmwareInventory",
    "Sessions": "GetSessions",
    "Manager": "GetManagerNicInventory",
    "Service": "CheckAvailability",
}


def main():
    result = {}
    category_list = []
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(type='list', elements='str', default=['Systems']),
            command=dict(type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            timeout=dict(type='int', default=60),
            update_handle=dict(),
            manager=dict(),
            ciphers=dict(type='list', elements='str'),
        ),
        required_together=[
            ('username', 'password'),
        ],
        required_one_of=[
            ('username', 'auth_token'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token'),
        ],
        supports_check_mode=True,
    )

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # timeout
    timeout = module.params['timeout']

    # update handle
    update_handle = module.params['update_handle']

    # manager
    manager = module.params['manager']

    # ciphers
    ciphers = module.params['ciphers']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_utils = RedfishUtils(creds, root_uri, timeout, module, ciphers=ciphers)

    # Build Category list
    if "all" in module.params['category']:
        for entry in CATEGORY_COMMANDS_ALL:
            category_list.append(entry)
    else:
        # one or more categories specified
        category_list = module.params['category']

    for category in category_list:
        command_list = []
        # Build Command list for each Category
        if category in CATEGORY_COMMANDS_ALL:
            if not module.params['command']:
                # True if we don't specify a command --> use default
                command_list.append(CATEGORY_COMMANDS_DEFAULT[category])
            elif "all" in module.params['command']:
                for entry in range(len(CATEGORY_COMMANDS_ALL[category])):
                    command_list.append(CATEGORY_COMMANDS_ALL[category][entry])
            # one or more commands
            else:
                command_list = module.params['command']
                # Verify that all commands are valid
                for cmd in command_list:
                    # Fail if even one command given is invalid
                    if cmd not in CATEGORY_COMMANDS_ALL[category]:
                        module.fail_json(msg="Invalid Command: %s" % cmd)
        else:
            # Fail if even one category given is invalid
            module.fail_json(msg="Invalid Category: %s" % category)

        # Organize by Categories / Commands
        if category == "Service":
            # service-level commands are always available
            for command in command_list:
                if command == "CheckAvailability":
                    result["service"] = rf_utils.check_service_availability()

        elif category == "Systems":
            # execute only if we find a Systems resource
            resource = rf_utils._find_systems_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetSystemInventory":
                    result["system"] = rf_utils.get_multi_system_inventory()
                elif command == "GetCpuInventory":
                    result["cpu"] = rf_utils.get_multi_cpu_inventory()
                elif command == "GetMemoryInventory":
                    result["memory"] = rf_utils.get_multi_memory_inventory()
                elif command == "GetNicInventory":
                    result["nic"] = rf_utils.get_multi_nic_inventory(category)
                elif command == "GetStorageControllerInventory":
                    result["storage_controller"] = rf_utils.get_multi_storage_controller_inventory()
                elif command == "GetDiskInventory":
                    result["disk"] = rf_utils.get_multi_disk_inventory()
                elif command == "GetVolumeInventory":
                    result["volume"] = rf_utils.get_multi_volume_inventory()
                elif command == "GetBiosAttributes":
                    result["bios_attribute"] = rf_utils.get_multi_bios_attributes()
                elif command == "GetBootOrder":
                    result["boot_order"] = rf_utils.get_multi_boot_order()
                elif command == "GetBootOverride":
                    result["boot_override"] = rf_utils.get_multi_boot_override()
                elif command == "GetHealthReport":
                    result["health_report"] = rf_utils.get_multi_system_health_report()
                elif command == "GetVirtualMedia":
                    result["virtual_media"] = rf_utils.get_multi_virtualmedia(category)
                elif command == "GetBiosRegistries":
                    result["bios_registries"] = rf_utils.get_bios_registries()

        elif category == "Chassis":
            # execute only if we find Chassis resource
            resource = rf_utils._find_chassis_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetFanInventory":
                    result["fan"] = rf_utils.get_fan_inventory()
                elif command == "GetPsuInventory":
                    result["psu"] = rf_utils.get_psu_inventory()
                elif command == "GetChassisThermals":
                    result["thermals"] = rf_utils.get_chassis_thermals()
                elif command == "GetChassisPower":
                    result["chassis_power"] = rf_utils.get_chassis_power()
                elif command == "GetChassisInventory":
                    result["chassis"] = rf_utils.get_chassis_inventory()
                elif command == "GetHealthReport":
                    result["health_report"] = rf_utils.get_multi_chassis_health_report()
                elif command == "GetHPEThermalConfig":
                    result["hpe_thermal_config"] = rf_utils.get_hpe_thermal_config()
                elif command == "GetHPEFanPercentMin":
                    result["hpe_fan_percent_min"] = rf_utils.get_hpe_fan_percent_min()

        elif category == "Accounts":
            # execute only if we find an Account service resource
            resource = rf_utils._find_accountservice_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "ListUsers":
                    result["user"] = rf_utils.list_users()

        elif category == "Update":
            # execute only if we find UpdateService resources
            resource = rf_utils._find_updateservice_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetFirmwareInventory":
                    result["firmware"] = rf_utils.get_firmware_inventory()
                elif command == "GetSoftwareInventory":
                    result["software"] = rf_utils.get_software_inventory()
                elif command == "GetFirmwareUpdateCapabilities":
                    result["firmware_update_capabilities"] = rf_utils.get_firmware_update_capabilities()
                elif command == "GetUpdateStatus":
                    result["update_status"] = rf_utils.get_update_status(update_handle)

        elif category == "Sessions":
            # execute only if we find SessionService resources
            resource = rf_utils._find_sessionservice_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetSessions":
                    result["session"] = rf_utils.get_sessions()

        elif category == "Manager":
            # execute only if we find a Manager service resource
            resource = rf_utils._find_managers_resource()
            if resource['ret'] is False:
                module.fail_json(msg=resource['msg'])

            for command in command_list:
                if command == "GetManagerNicInventory":
                    result["manager_nics"] = rf_utils.get_multi_nic_inventory(category)
                elif command == "GetVirtualMedia":
                    result["virtual_media"] = rf_utils.get_multi_virtualmedia(category)
                elif command == "GetLogs":
                    result["log"] = rf_utils.get_logs()
                elif command == "GetNetworkProtocols":
                    result["network_protocols"] = rf_utils.get_network_protocols()
                elif command == "GetHealthReport":
                    result["health_report"] = rf_utils.get_multi_manager_health_report()
                elif command == "GetHostInterfaces":
                    result["host_interfaces"] = rf_utils.get_hostinterfaces()
                elif command == "GetManagerInventory":
                    result["manager"] = rf_utils.get_multi_manager_inventory()
                elif command == "GetServiceIdentification":
                    result["service_id"] = rf_utils.get_service_identification(manager)

    # Return data back
    module.exit_json(redfish_facts=result)


if __name__ == '__main__':
    main()
