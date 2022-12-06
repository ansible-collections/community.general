#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 Hewlett Packard Enterprise, Inc. All rights reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: ilo_redfish_config
short_description: Sets or updates configuration attributes on HPE iLO with Redfish OEM extensions
version_added: 7.0.0
description:
  - Builds Redfish URIs locally and sends them to iLO to
    set or update a configuration attribute.
  - For use with HPE iLO operations that require Redfish OEM extensions.
options:
  category:
    required: true
    type: str
    description:
      - Command category to execute on iLO.
    choices: ['Manager', 'Systems']
  command:
    required: true
    description:
      - List of commands to execute on iLO.
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of iLO.
    type: str
  username:
    required: false
    description:
      - Username for authenticating to iLO.
    type: str
  password:
    required: false
    description:
      - Password for authenticating to iLO.
    type: str
  auth_token:
    required: false
    description:
      - Security token for authenticating to iLO.
    type: str
  timeout:
    required: false
    description:
      - Timeout in seconds for URL requests to iLO controller.
      - The default value for this param is 10 but that is being deprecated
        and it will be replaced with 60 in community.general 5.7.0.
    type: int
  attribute_name:
    required: false
    description:
      - Name of the attribute to be configured.
    type: str
  attribute_value:
    required: false
    description:
      - Value of the attribute to be configured.
    type: str
  raid_details:
    required: false
    description:
      - List of RAID details that need to be configured in the given server
    type: list
    elements: dict
    suboptions:
      LogicalDriveName:
        required: false
        description:
          - Logical drive name that needs to be configured in the given server
        type: str
      Raid:
        required: false
        description:
          - Type of RAID
        type: str
      DataDrives:
        required: false
        description:
          - Specifies the data drive details like media type, interface type, disk count and size
        type: dict
      DataDriveCount:
        required: false
        description:
          - Number of physical drives that is required to create specified RAID
        type: int
      DataDriveMediaType:
        required: false
        description:
          - Media type of the disk
        type: str
      DataDriveInterfaceType:
        required: false
        description:
          - Interface type of the disk
        type: str
      DataDriveMinimumSizeGiB:
        required: false
        description:
          - Minimum size required in the physical drive
        type: int
  logical_drives_names:
    required: false
    description:
      - logical drives names which are to be deleted
    type: list
    elements: str
  snmpv3_usernames:
    required: false
    description:
      - List of SNMPv3 user names that need to be deleted from the given server
    type: list
    elements: str
  cert_file:
    required: false
    description:
      - absolute path to the server cert file
    type: str
  key_file:
    required: false
    description:
      - absolute path to the server key file
    type: str
  snmpv3_users:
    required: false
    description:
      - List of SNMPv3 users that needs to be added in the given server
    type: list
    elements: dict
    suboptions:
      security_name:
        required: false
        description:
          - SNMPv3 security name associated with SNMPv3trap or SNMPv3Inform set on SNMPAlertProtocol
          - Alphanumeric value with 1-32 characters
        type: str
      auth_protocol:
        required: false
        description:
          - Sets the message digest algorithm to use for encoding the authorization passphrase
          - The message digest is calculated over an appropriate portion of an SNMP message and is included as part of the message sent to the recipient
          - Supported Auth protocols are MD5, SHA, and SHA256
        type: str
      auth_passphrase:
        required: false
        description:
          - Sets the passphrase to use for sign operations
          - String with 8-49 characters
        type: str
      privacy_protocol:
        required: false
        description:
          - Sets the encryption algorithm to use for encoding the privacy passphrase
          - A portion of an SNMP message is encrypted before transmission
          - Supported privacy protocols are AES and DES
        type: str
      privacy_passphrase:
        required: false
        description:
          - Sets the passphrase to use for encrypt operations
          - String with 8-49 characters
        type: str
      user_engine_id:
        required: false
        description:
          - The SNMPv3 Engine ID is the unique identifier of an SNMP engine that belongs to an SNMP agent entity
          - This value must be a hexadecimal string with an even number of 10 to 64 characters, excluding first two characters, 0x (example 0x01020304abcdef)
        type: str
  alert_destinations:
    required: false
    description:
      - List of alert destination that needs to be added in the given server
    type: list
    elements: dict
    suboptions:
      alert_destination:
        required: false
        description:
          - IP address/hostname/FQDN of remote management system that receives SNMP alerts
        type: str
      snmp_alert_protocol:
        required: false
        description:
          - SNMP protocol associated with the AlertDestination
          - The supported SNMP alert protocols are SNMPv1Trap, SNMPv3Trap, and SNMPv3Inform
        type: str
      trap_community:
        required: false
        description:
          - Configuring trap community string
          - This option is supported for SNMPv1Trap, SNMPv3Trap, and SNMPv3Inform alert protocols
        type: str
  service_attributes:
    required: false
    description:
      - BIOS service attributes that needs to be configured in the given server
    type: dict
author:
  - Bhavya B (@bhavya06)
  - Gayathiri Devi Ramasamy (@Gayathirideviramasamy)
  - T S Kushal (@TSKushal)
  - Varni H P (@varini-hp)
  - Prativa Nayak (@prativa-n)
'''

EXAMPLES = '''
  - name: Disable WINS Registration
    community.general.ilo_redfish_config:
      category: Manager
      command: SetWINSReg
      baseuri: 15.X.X.X
      username: Admin
      password: Testpass123
      attribute_name: WINSRegistration

  - name: Set Time Zone
    community.general.ilo_redfish_config:
      category: Manager
      command: SetTimeZone
      baseuri: 15.X.X.X
      username: Admin
      password: Testpass123
      attribute_name: TimeZone
      attribute_value: Chennai

  - name: Set NTP Servers
    community.general.ilo_redfish_config:
      category: Manager
      command: SetNTPServers
      baseuri: 15.X.X.X
      username: Admin
      password: Testpass123
      attribute_name: StaticNTPServers
      attribute_value: X.X.X.X

  - name: Create logical drive
    ilo_redfish_config:
      category: Systems
      command: CreateLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      raid_details:
        - LogicalDriveName: LD1
          Raid: Raid1
          DataDrives:
              DataDriveCount: 2
              DataDriveMediaType: HDD
              DataDriveInterfaceType: SAS
              DataDriveMinimumSizeGiB: 0

  - name: Create logical drives with particular physical drives
    ilo_redfish_config:
      category: Systems
      command: CreateLogicalDrivesWithParticularPhysicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      raid_details:
      - LogicalDriveName: LD1
        Raid: Raid1
        CapacityGB: 1200,
        DataDrives: ["1I:1:1", "1I:1:2"]

  - name: Delete all logical drives
    ilo_redfish_config:
      category: Systems
      command: DeleteAllLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Delete specified logical drives
    ilo_redfish_config:
      category: Systems
      command: DeleteSpecifiedLogicalDrives
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      logical_drives_names: ["LD1", "LD2"]

  - name: Enable secure boot
    ilo_redfish_config:
      category: Systems
      command: EnableSecureBoot
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Deleting all the SNMPv3 users
    ilo_redfish_config:
      category: Manager
      command: DeleteAllSNMPv3Users
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Deleting all the SNMP alert destinations
    ilo_redfish_config:
      category: Manager
      command: DeleteAllSNMPAlertDestinations
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"

  - name: Deleting specified SNMPv3 users
    ilo_redfish_config:
      category: Manager
      command: DeleteSpecifiedSNMPv3Users
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      snmpv3_usernames:
        - user1
        - user2

  - name: Creating SNMPv3 users
    ilo_redfish_config:
      category: Manager
      command: CreateSNMPv3Users
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      snmpv3_users:
        - security_name: "Sec1"
          auth_protocol: "SHA"
          auth_passphrase: "********"
          privacy_protocol: "AES"
          privacy_passphrase: "********"
          user_engine_id: "123450abdcef"

  - name: Updating specified SNMPv3 users
    ilo_redfish_config:
      category: Manager
      command: UpdateSNMPv3Users
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      snmpv3_users:
        - security_name: "Sec1"
          auth_protocol: "SHA"
          auth_passphrase: "********"
          privacy_protocol: "AES"
          privacy_passphrase: "********"
          user_engine_id: "123450abdcef"

  - name: Creating SNMP alert destinations
    ilo_redfish_config:
      category: Manager
      command: CreateSNMPAlertDestinations
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      alert_destinations:
        - snmp_alert_protocol: "SNMPv1Trap"
          trap_community: "public"
          alert_destination: "************"
          security_name: "Sec1"

  - name: Configure service BIOS attributes
    ilo_redfish_config:
      category: Systems
      command: SetServiceBiosAttributes
      baseuri: "***.***.***.***"
      username: "abcxyz"
      password: "******"
      service_attributes:
        ConnectSequenceTrace: "Disabled"
        CustomDebugBlkIo: "Disabled"

'''

RETURN = '''
ilo_redfish_config:
    description: Returns the status of the operation performed on the iLO.
    type: dict
    contains:
        command:
            description: Returns the output msg and whether the function executed successfully.
            type: dict
            contains:
                ret:
                    description: Return True/False based on whether the operation was performed succesfully.
                    type: bool
                msg:
                    description: Status of the operation performed on the iLO.
                    type: str
    returned: always
'''

CATEGORY_COMMANDS_ALL = {
    "Manager": [
        "SetTimeZone",
        "SetDNSserver",
        "SetDomainName",
        "SetNTPServers",
        "SetWINSReg",
        "DeleteAllSNMPv3Users",
        "DeleteSpecifiedSNMPv3Users",
        "DeleteAllSNMPAlertDestinations",
        "UpdateSNMPv3Users",
        "CreateSNMPv3Users",
        "CreateSNMPAlertDestinations",
    ],
    "Systems": [
        "SetServiceBiosAttributes",
        "DeleteAllLogicalDrives",
        "DeleteSpecifiedLogicalDrives",
        "CreateLogicalDrives",
        "CreateLogicalDrivesWithParticularPhysicalDrives",
        "EnableSecureBoot"
    ]
}

HAS_iLO_REDFISH = True

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
try:
    from ansible_collections.community.general.plugins.module_utils.ilo_redfish_utils import (
        iLORedfishUtils, ilo_certificate_login
    )
except ImportError as e:
    iLO_REDFISH_IMP_ERR = traceback.format_exc()
    HAS_iLO_REDFISH = False


def main():
    result = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True, choices=list(
                CATEGORY_COMMANDS_ALL.keys())),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            attribute_name=dict(),
            attribute_value=dict(),
            timeout=dict(type='int'),
            service_attributes=dict(type='dict'),
            raid_details=dict(type='list', elements='dict'),
            logical_drives_names=dict(type='list', elements='str'),
            cert_file=dict(type='str'),
            key_file=dict(type='str'),
            snmpv3_usernames=dict(type='list', elements='str'),
            snmpv3_users=dict(type='list', elements='dict'),
            alert_destinations=dict(type='list', elements='dict')
        ),
        required_together=[
            ('username', 'password'),
            ('cert_file', 'key_file')
        ],
        required_one_of=[
            ('username', 'auth_token', 'cert_file'),
        ],
        mutually_exclusive=[
            ('username', 'auth_token', 'cert_file'),
        ],
        supports_check_mode=False
    )

    if not HAS_iLO_REDFISH:
        module.fail_json(msg="missing required fucntions in ilo_redfish_utils.py")

    category = module.params['category']
    command_list = module.params['command']

    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}

    timeout = module.params['timeout']
    if module.params['timeout'] is None:
        timeout = 10
        module.deprecate(
            'The default value {0} for parameter param1 is being deprecated and it will be replaced by {1}'.format(
                10, 60
            ),
            version='8.0.0',
            collection_name='community.general'
        )

    root_uri = "https://" + module.params['baseuri']

    if module.params["cert_file"]:
        creds["token"] = ilo_certificate_login(root_uri, module, module.params["cert_file"], module.params["key_file"])

    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)
    changed = False

    offending = [
        cmd for cmd in command_list if cmd not in CATEGORY_COMMANDS_ALL[category]]

    if offending:
        module.fail_json(msg=to_native("Invalid Command(s): '%s'. Allowed Commands = %s" % (
            offending, CATEGORY_COMMANDS_ALL[category])))

    if category == "Manager":
        exception_list = [
            "DeleteAllSNMPv3Users",
            "DeleteSpecifiedSNMPv3Users",
            "DeleteAllSNMPAlertDestinations",
            "UpdateSNMPv3Users",
            "CreateSNMPv3Users",
            "CreateSNMPAlertDestinations"
        ]
        for command in command_list:
            if command not in exception_list:
                result[command] = {}
                if not module.params["attribute_name"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "attribute_name params is required"
                    module.fail_json(result)
                mgr_attributes = {
                    "mgr_attr_name": module.params["attribute_name"],
                    "mgr_attr_value": module.params["attribute_value"],
                }
        resource = rf_utils._find_managers_resource()
        if not resource["ret"]:
            result[command] = resource
            module.fail_json(msg=to_native(result))

        dispatch = dict(
            SetTimeZone=rf_utils.set_time_zone,
            SetDNSserver=rf_utils.set_dns_server,
            SetDomainName=rf_utils.set_domain_name,
            SetNTPServers=rf_utils.set_ntp_server,
            SetWINSReg=rf_utils.set_wins_registration,
            DeleteAllSNMPv3Users=rf_utils.delete_all_snmpv3_users,
            DeleteSpecifiedSNMPv3Users=rf_utils.delete_snmpv3_users,
            DeleteAllSNMPAlertDestinations=rf_utils.delete_all_snmp_alert_destinations,
            UpdateSNMPv3Users=rf_utils.update_snmpv3_users,
            CreateSNMPv3Users=rf_utils.create_snmpv3_users,
            CreateSNMPAlertDestinations=rf_utils.create_alert_destinations,
        )

        for command in command_list:
            result[command] = {}

            if command in ["DeleteAllSNMPv3Users", "DeleteAllSNMPAlertDestinations"]:
                result[command] = dispatch[command]()
            elif command == "DeleteSpecifiedSNMPv3Users":
                if not module.params["snmpv3_usernames"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "'snmpv3_usernames' parameter is required"
                    module.fail_json(result)
                result[command] = dispatch[command](module.params['snmpv3_usernames'])
            elif command in ["UpdateSNMPv3Users", "CreateSNMPv3Users"]:
                if not module.params["snmpv3_users"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "'snmpv3_users' parameter is required"
                    module.fail_json(result)
                result[command] = dispatch[command](module.params['snmpv3_users'])
            elif command in ["CreateSNMPAlertDestinations"]:
                if not module.params["alert_destinations"]:
                    result[command]['ret'] = False
                    result[command]['msg'] = "'alert_destinations' parameter is required"
                    module.fail_json(result)
                result[command] = dispatch[command](module.params['alert_destinations'])
            else:
                result[command] = dispatch[command](mgr_attributes)
            if "changed" in result[command]:
                changed |= result[command]["changed"]

    elif category == "Systems":
        dispatch = dict(
            SetServiceBiosAttributes=rf_utils.set_service_bios_attributes,
            DeleteAllLogicalDrives=rf_utils.delete_all_logical_drives,
            DeleteSpecifiedLogicalDrives=rf_utils.delete_specified_logical_drives,
            CreateLogicalDrives=rf_utils.create_logical_drives,
            CreateLogicalDrivesWithParticularPhysicalDrives=rf_utils.create_logical_drives_with_particular_physical_drives,
            EnableSecureBoot=rf_utils.enable_secure_boot

        )

        for command in command_list:
            if command == "SetServiceBiosAttributes":
                result[command] = dispatch[command](module.params["service_attributes"])
            elif command == "DeleteAllLogicalDrives":
                result[command] = dispatch[command]()
            elif command == "DeleteSpecifiedLogicalDrives":
                result[command] = dispatch[command](module.params["logical_drives_names"])
            elif command == "CreateLogicalDrives":
                result[command] = dispatch[command](module.params["raid_details"])
            elif command == "CreateLogicalDrivesWithParticularPhysicalDrives":
                result[command] = dispatch[command](module.params["raid_details"])
            elif command == "EnableSecureBoot":
                result[command] = dispatch[command]()
            if "changed" in result[command]:
                changed |= result[command]["changed"]

    if not result[command]['ret']:
        module.fail_json(msg=result)

    module.exit_json(ilo_redfish_config=result, changed=changed)


if __name__ == '__main__':
    main()
