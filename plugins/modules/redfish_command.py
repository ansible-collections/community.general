#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redfish_command
short_description: Manages Out-Of-Band controllers using Redfish APIs
description:
  - Builds Redfish URIs locally and sends them to remote OOB controllers to
    perform an action.
  - Manages OOB controller ex. reboot, log management.
  - Manages OOB controller users ex. add, remove, update.
  - Manages system power ex. on, off, graceful and forced reboot.
extends_documentation_fragment:
  - community.general.attributes
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
  session_uri:
    description:
      - URI of the session resource.
    type: str
    version_added: 2.3.0
  id:
    required: false
    aliases: [ account_id ]
    description:
      - ID of account to delete/modify.
      - Can also be used in account creation to work around vendor issues where the ID of the new user is required in the POST request.
    type: str
  new_username:
    required: false
    aliases: [ account_username ]
    description:
      - Username of account to add/delete/modify.
    type: str
  new_password:
    required: false
    aliases: [ account_password ]
    description:
      - New password of account to add/modify.
    type: str
  roleid:
    required: false
    aliases: [ account_roleid ]
    description:
      - Role of account to add/modify.
    type: str
  account_types:
    required: false
    aliases: [ account_accounttypes ]
    description:
      - Array of account types to apply to a user account.
    type: list
    elements: str
    version_added: '7.2.0'
  oem_account_types:
    required: false
    aliases: [ account_oemaccounttypes ]
    description:
      - Array of OEM account types to apply to a user account.
    type: list
    elements: str
    version_added: '7.2.0'
  bootdevice:
    required: false
    description:
      - Boot device when setting boot configuration.
    type: str
  timeout:
    description:
      - Timeout in seconds for HTTP requests to OOB controller.
      - The default value for this parameter changed from V(10) to V(60)
        in community.general 9.0.0.
    type: int
    default: 60
  boot_override_mode:
    description:
      - Boot mode when using an override.
    type: str
    choices: [ Legacy, UEFI ]
    version_added: 3.5.0
  uefi_target:
    required: false
    description:
      - UEFI boot target when bootdevice is "UefiTarget".
    type: str
  boot_next:
    required: false
    description:
      - BootNext target when bootdevice is "UefiBootNext".
    type: str
  update_username:
    required: false
    aliases: [ account_updatename ]
    description:
      - New user name for updating account_username.
    type: str
    version_added: '0.2.0'
  account_properties:
    required: false
    description:
      - Properties of account service to update.
    type: dict
    default: {}
    version_added: '0.2.0'
  resource_id:
    required: false
    description:
      - ID of the System, Manager or Chassis to modify.
    type: str
    version_added: '0.2.0'
  update_image_uri:
    required: false
    description:
      - URI of the image for the update.
    type: str
    version_added: '0.2.0'
  update_image_file:
    required: false
    description:
      - Filename, with optional path, of the image for the update.
    type: path
    version_added: '7.1.0'
  update_protocol:
    required: false
    description:
      - Protocol for the update.
    type: str
    version_added: '0.2.0'
  update_targets:
    required: false
    description:
      - List of target resource URIs to apply the update to.
    type: list
    elements: str
    default: []
    version_added: '0.2.0'
  update_creds:
    required: false
    description:
      - Credentials for retrieving the update image.
    type: dict
    version_added: '0.2.0'
    suboptions:
      username:
        required: false
        description:
          - Username for retrieving the update image.
        type: str
      password:
        required: false
        description:
          - Password for retrieving the update image.
        type: str
  update_apply_time:
    required: false
    description:
      - Time when to apply the update.
    type: str
    choices:
      - Immediate
      - OnReset
      - AtMaintenanceWindowStart
      - InMaintenanceWindowOnReset
      - OnStartUpdateRequest
    version_added: '6.1.0'
  update_oem_params:
    required: false
    description:
      - Properties for HTTP Multipart Push Updates.
    type: dict
    version_added: '7.5.0'
  update_handle:
    required: false
    description:
      - Handle to check the status of an update in progress.
    type: str
    version_added: '6.1.0'
  virtual_media:
    required: false
    description:
      - Options for VirtualMedia commands.
    type: dict
    version_added: '0.2.0'
    suboptions:
      media_types:
        required: false
        description:
          - List of media types appropriate for the image.
        type: list
        elements: str
        default: []
      image_url:
        required: false
        description:
          - URL of the image to insert or eject.
        type: str
      inserted:
        required: false
        description:
          - Indicates that the image is treated as inserted on command completion.
        type: bool
        default: true
      write_protected:
        required: false
        description:
          - Indicates that the media is treated as write-protected.
        type: bool
        default: true
      username:
        required: false
        description:
          - Username for accessing the image URL.
        type: str
      password:
        required: false
        description:
          - Password for accessing the image URL.
        type: str
      transfer_protocol_type:
        required: false
        description:
          - Network protocol to use with the image.
        type: str
      transfer_method:
        required: false
        description:
          - Transfer method to use with the image.
        type: str
  strip_etag_quotes:
    description:
      - Removes surrounding quotes of etag used in C(If-Match) header
        of C(PATCH) requests.
      - Only use this option to resolve bad vendor implementation where
        C(If-Match) only matches the unquoted etag string.
    type: bool
    default: false
    version_added: 3.7.0
  bios_attributes:
    required: false
    description:
      - BIOS attributes that needs to be verified in the given server.
    type: dict
    version_added: 6.4.0
  reset_to_defaults_mode:
    description:
      - Mode to apply when reseting to default.
    type: str
    choices: [ ResetAll, PreserveNetworkAndUsers, PreserveNetwork ]
    version_added: 8.6.0
  wait:
    required: false
    description:
      - Block until the service is ready again.
    type: bool
    default: false
    version_added: 9.1.0
  wait_timeout:
    required: false
    description:
      - How long to block until the service is ready again before giving up.
    type: int
    default: 120
    version_added: 9.1.0
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

author:
  - "Jose Delarosa (@jose-delarosa)"
  - "T S Kushal (@TSKushal)"
'''

EXAMPLES = '''
  - name: Restart system power gracefully
    community.general.redfish_command:
      category: Systems
      command: PowerGracefulRestart
      resource_id: 437XR1138R2
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Turn system power off
    community.general.redfish_command:
      category: Systems
      command: PowerForceOff
      resource_id: 437XR1138R2

  - name: Restart system power forcefully
    community.general.redfish_command:
      category: Systems
      command: PowerForceRestart
      resource_id: 437XR1138R2

  - name: Shutdown system power gracefully
    community.general.redfish_command:
      category: Systems
      command: PowerGracefulShutdown
      resource_id: 437XR1138R2

  - name: Turn system power on
    community.general.redfish_command:
      category: Systems
      command: PowerOn
      resource_id: 437XR1138R2

  - name: Reboot system power
    community.general.redfish_command:
      category: Systems
      command: PowerReboot
      resource_id: 437XR1138R2

  - name: Set one-time boot device to {{ bootdevice }}
    community.general.redfish_command:
      category: Systems
      command: SetOneTimeBoot
      resource_id: 437XR1138R2
      bootdevice: "{{ bootdevice }}"
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Set one-time boot device to UefiTarget of "/0x31/0x33/0x01/0x01"
    community.general.redfish_command:
      category: Systems
      command: SetOneTimeBoot
      resource_id: 437XR1138R2
      bootdevice: "UefiTarget"
      uefi_target: "/0x31/0x33/0x01/0x01"
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Set one-time boot device to BootNext target of "Boot0001"
    community.general.redfish_command:
      category: Systems
      command: SetOneTimeBoot
      resource_id: 437XR1138R2
      bootdevice: "UefiBootNext"
      boot_next: "Boot0001"
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Set persistent boot device override
    community.general.redfish_command:
      category: Systems
      command: EnableContinuousBootOverride
      resource_id: 437XR1138R2
      bootdevice: "{{ bootdevice }}"
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Set one-time boot to BiosSetup
    community.general.redfish_command:
      category: Systems
      command: SetOneTimeBoot
      boot_next: BiosSetup
      boot_override_mode: Legacy
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Disable persistent boot device override
    community.general.redfish_command:
      category: Systems
      command: DisableBootOverride

  - name: Set system indicator LED to blink using security token for auth
    community.general.redfish_command:
      category: Systems
      command: IndicatorLedBlink
      resource_id: 437XR1138R2
      baseuri: "{{ baseuri }}"
      auth_token: "{{ result.session.token }}"

  - name: Add user
    community.general.redfish_command:
      category: Accounts
      command: AddUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      new_username: "{{ new_username }}"
      new_password: "{{ new_password }}"
      roleid: "{{ roleid }}"

  - name: Add user with specified account types
    community.general.redfish_command:
      category: Accounts
      command: AddUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      new_username: "{{ new_username }}"
      new_password: "{{ new_password }}"
      roleid: "{{ roleid }}"
      account_types:
      - Redfish
      - WebUI

  - name: Add user using new option aliases
    community.general.redfish_command:
      category: Accounts
      command: AddUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"
      account_password: "{{ account_password }}"
      account_roleid: "{{ account_roleid }}"

  - name: Delete user
    community.general.redfish_command:
      category: Accounts
      command: DeleteUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"

  - name: Disable user
    community.general.redfish_command:
      category: Accounts
      command: DisableUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"

  - name: Enable user
    community.general.redfish_command:
      category: Accounts
      command: EnableUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"

  - name: Add and enable user
    community.general.redfish_command:
      category: Accounts
      command: AddUser,EnableUser
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      new_username: "{{ new_username }}"
      new_password: "{{ new_password }}"
      roleid: "{{ roleid }}"

  - name: Update user password
    community.general.redfish_command:
      category: Accounts
      command: UpdateUserPassword
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"
      account_password: "{{ account_password }}"

  - name: Update user role
    community.general.redfish_command:
      category: Accounts
      command: UpdateUserRole
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"
      roleid: "{{ roleid }}"

  - name: Update user name
    community.general.redfish_command:
      category: Accounts
      command: UpdateUserName
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"
      account_updatename: "{{ account_updatename }}"

  - name: Update user name
    community.general.redfish_command:
      category: Accounts
      command: UpdateUserName
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_username: "{{ account_username }}"
      update_username: "{{ update_username }}"

  - name: Update AccountService properties
    community.general.redfish_command:
      category: Accounts
      command: UpdateAccountServiceProperties
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      account_properties:
        AccountLockoutThreshold: 5
        AccountLockoutDuration: 600

  - name: Clear Manager Logs with a timeout of 20 seconds
    community.general.redfish_command:
      category: Manager
      command: ClearLogs
      resource_id: BMC
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      timeout: 20

  - name: Create session
    community.general.redfish_command:
      category: Sessions
      command: CreateSession
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
    register: result

  - name: Set chassis indicator LED to blink using security token for auth
    community.general.redfish_command:
      category: Chassis
      command: IndicatorLedBlink
      resource_id: 1U
      baseuri: "{{ baseuri }}"
      auth_token: "{{ result.session.token }}"

  - name: Delete session using security token created by CreateSesssion above
    community.general.redfish_command:
      category: Sessions
      command: DeleteSession
      baseuri: "{{ baseuri }}"
      auth_token: "{{ result.session.token }}"
      session_uri: "{{ result.session.uri }}"

  - name: Clear Sessions
    community.general.redfish_command:
      category: Sessions
      command: ClearSessions
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Simple update
    community.general.redfish_command:
      category: Update
      command: SimpleUpdate
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      update_image_uri: https://example.com/myupdate.img

  - name: Simple update with additional options
    community.general.redfish_command:
      category: Update
      command: SimpleUpdate
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      update_image_uri: //example.com/myupdate.img
      update_protocol: FTP
      update_targets:
        - /redfish/v1/UpdateService/FirmwareInventory/BMC
      update_creds:
        username: operator
        password: supersecretpwd

  - name: Multipart HTTP push update; timeout is 600 seconds to allow for a
      large image transfer
    community.general.redfish_command:
      category: Update
      command: MultipartHTTPPushUpdate
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      timeout: 600
      update_image_file: ~/images/myupdate.img

  - name: Multipart HTTP push with additional options; timeout is 600 seconds
      to allow for a large image transfer
    community.general.redfish_command:
      category: Update
      command: MultipartHTTPPushUpdate
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      timeout: 600
      update_image_file: ~/images/myupdate.img
      update_targets:
        - /redfish/v1/UpdateService/FirmwareInventory/BMC
      update_oem_params:
        PreserveConfiguration: false

  - name: Perform requested operations to continue the update
    community.general.redfish_command:
      category: Update
      command: PerformRequestedOperations
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      update_handle: /redfish/v1/TaskService/TaskMonitors/735

  - name: Insert Virtual Media
    community.general.redfish_command:
      category: Systems
      command: VirtualMediaInsert
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      virtual_media:
        image_url: 'http://example.com/images/SomeLinux-current.iso'
        media_types:
          - CD
          - DVD
      resource_id: 1

  - name: Insert Virtual Media
    community.general.redfish_command:
      category: Manager
      command: VirtualMediaInsert
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      virtual_media:
        image_url: 'http://example.com/images/SomeLinux-current.iso'
        media_types:
          - CD
          - DVD
      resource_id: BMC

  - name: Eject Virtual Media
    community.general.redfish_command:
      category: Systems
      command: VirtualMediaEject
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      virtual_media:
        image_url: 'http://example.com/images/SomeLinux-current.iso'
      resource_id: 1

  - name: Eject Virtual Media
    community.general.redfish_command:
      category: Manager
      command: VirtualMediaEject
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      virtual_media:
        image_url: 'http://example.com/images/SomeLinux-current.iso'
      resource_id: BMC

  - name: Restart manager power gracefully
    community.general.redfish_command:
      category: Manager
      command: GracefulRestart
      resource_id: BMC
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"

  - name: Restart manager power gracefully and wait for it to be available
    community.general.redfish_command:
      category: Manager
      command: GracefulRestart
      resource_id: BMC
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      wait: True

  - name: Restart manager power gracefully
    community.general.redfish_command:
      category: Manager
      command: PowerGracefulRestart
      resource_id: BMC

  - name: Turn manager power off
    community.general.redfish_command:
      category: Manager
      command: PowerForceOff
      resource_id: BMC

  - name: Restart manager power forcefully
    community.general.redfish_command:
      category: Manager
      command: PowerForceRestart
      resource_id: BMC

  - name: Shutdown manager power gracefully
    community.general.redfish_command:
      category: Manager
      command: PowerGracefulShutdown
      resource_id: BMC

  - name: Turn manager power on
    community.general.redfish_command:
      category: Manager
      command: PowerOn
      resource_id: BMC

  - name: Reboot manager power
    community.general.redfish_command:
      category: Manager
      command: PowerReboot
      resource_id: BMC

  - name: Factory reset manager to defaults
    community.general.redfish_command:
      category: Manager
      command: ResetToDefaults
      resource_id: BMC
      reset_to_defaults_mode: ResetAll

  - name: Verify BIOS attributes
    community.general.redfish_command:
      category: Systems
      command: VerifyBiosAttributes
      baseuri: "{{ baseuri }}"
      username: "{{ username }}"
      password: "{{ password }}"
      bios_attributes:
        SubNumaClustering: "Disabled"
        WorkloadProfile: "Virtualization-MaxPerformance"
'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
return_values:
    description: Dictionary containing command-specific response data from the action.
    returned: on success
    type: dict
    version_added: 6.1.0
    sample: {
        "update_status": {
            "handle": "/redfish/v1/TaskService/TaskMonitors/735",
            "messages": [],
            "resets_requested": [],
            "ret": true,
            "status": "New"
        }
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.common.text.converters import to_native


# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["PowerOn", "PowerForceOff", "PowerForceRestart", "PowerGracefulRestart",
                "PowerGracefulShutdown", "PowerReboot", "PowerCycle", "SetOneTimeBoot", "EnableContinuousBootOverride", "DisableBootOverride",
                "IndicatorLedOn", "IndicatorLedOff", "IndicatorLedBlink", "VirtualMediaInsert", "VirtualMediaEject", "VerifyBiosAttributes"],
    "Chassis": ["IndicatorLedOn", "IndicatorLedOff", "IndicatorLedBlink"],
    "Accounts": ["AddUser", "EnableUser", "DeleteUser", "DisableUser",
                 "UpdateUserRole", "UpdateUserPassword", "UpdateUserName",
                 "UpdateAccountServiceProperties"],
    "Sessions": ["ClearSessions", "CreateSession", "DeleteSession"],
    "Manager": ["GracefulRestart", "ClearLogs", "VirtualMediaInsert",
                "ResetToDefaults",
                "VirtualMediaEject", "PowerOn", "PowerForceOff", "PowerForceRestart",
                "PowerGracefulRestart", "PowerGracefulShutdown", "PowerReboot"],
    "Update": ["SimpleUpdate", "MultipartHTTPPushUpdate", "PerformRequestedOperations"],
}


def main():
    result = {}
    return_values = {}
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(required=True),
            command=dict(required=True, type='list', elements='str'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(no_log=True),
            auth_token=dict(no_log=True),
            session_uri=dict(),
            id=dict(aliases=["account_id"]),
            new_username=dict(aliases=["account_username"]),
            new_password=dict(aliases=["account_password"], no_log=True),
            roleid=dict(aliases=["account_roleid"]),
            account_types=dict(type='list', elements='str', aliases=["account_accounttypes"]),
            oem_account_types=dict(type='list', elements='str', aliases=["account_oemaccounttypes"]),
            update_username=dict(type='str', aliases=["account_updatename"]),
            account_properties=dict(type='dict', default={}),
            bootdevice=dict(),
            timeout=dict(type='int', default=60),
            uefi_target=dict(),
            boot_next=dict(),
            boot_override_mode=dict(choices=['Legacy', 'UEFI']),
            resource_id=dict(),
            update_image_uri=dict(),
            update_image_file=dict(type='path'),
            update_protocol=dict(),
            update_targets=dict(type='list', elements='str', default=[]),
            update_oem_params=dict(type='dict'),
            update_creds=dict(
                type='dict',
                options=dict(
                    username=dict(),
                    password=dict(no_log=True)
                )
            ),
            update_apply_time=dict(choices=['Immediate', 'OnReset', 'AtMaintenanceWindowStart',
                                            'InMaintenanceWindowOnReset', 'OnStartUpdateRequest']),
            update_handle=dict(),
            virtual_media=dict(
                type='dict',
                options=dict(
                    media_types=dict(type='list', elements='str', default=[]),
                    image_url=dict(),
                    inserted=dict(type='bool', default=True),
                    write_protected=dict(type='bool', default=True),
                    username=dict(),
                    password=dict(no_log=True),
                    transfer_protocol_type=dict(),
                    transfer_method=dict(),
                )
            ),
            strip_etag_quotes=dict(type='bool', default=False),
            reset_to_defaults_mode=dict(choices=['ResetAll', 'PreserveNetworkAndUsers', 'PreserveNetwork']),
            bios_attributes=dict(type="dict"),
            wait=dict(type='bool', default=False),
            wait_timeout=dict(type='int', default=120),
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
        supports_check_mode=False
    )

    category = module.params['category']
    command_list = module.params['command']

    # admin credentials used for authentication
    creds = {'user': module.params['username'],
             'pswd': module.params['password'],
             'token': module.params['auth_token']}

    # user to add/modify/delete
    user = {
        'account_id': module.params['id'],
        'account_username': module.params['new_username'],
        'account_password': module.params['new_password'],
        'account_roleid': module.params['roleid'],
        'account_accounttypes': module.params['account_types'],
        'account_oemaccounttypes': module.params['oem_account_types'],
        'account_updatename': module.params['update_username'],
        'account_properties': module.params['account_properties'],
        'account_passwordchangerequired': None,
    }

    # timeout
    timeout = module.params['timeout']

    # System, Manager or Chassis ID to modify
    resource_id = module.params['resource_id']

    # update options
    update_opts = {
        'update_image_uri': module.params['update_image_uri'],
        'update_image_file': module.params['update_image_file'],
        'update_protocol': module.params['update_protocol'],
        'update_targets': module.params['update_targets'],
        'update_creds': module.params['update_creds'],
        'update_apply_time': module.params['update_apply_time'],
        'update_oem_params': module.params['update_oem_params'],
        'update_handle': module.params['update_handle'],
    }

    # Boot override options
    boot_opts = {
        'bootdevice': module.params['bootdevice'],
        'uefi_target': module.params['uefi_target'],
        'boot_next': module.params['boot_next'],
        'boot_override_mode': module.params['boot_override_mode'],
    }

    # VirtualMedia options
    virtual_media = module.params['virtual_media']

    # Etag options
    strip_etag_quotes = module.params['strip_etag_quotes']

    # BIOS Attributes options
    bios_attributes = module.params['bios_attributes']

    # ciphers
    ciphers = module.params['ciphers']

    # Build root URI
    root_uri = "https://" + module.params['baseuri']
    rf_utils = RedfishUtils(creds, root_uri, timeout, module,
                            resource_id=resource_id, data_modification=True, strip_etag_quotes=strip_etag_quotes,
                            ciphers=ciphers)

    # Check that Category is valid
    if category not in CATEGORY_COMMANDS_ALL:
        module.fail_json(msg=to_native("Invalid Category '%s'. Valid Categories = %s" % (category, list(CATEGORY_COMMANDS_ALL.keys()))))

    # Check that all commands are valid
    for cmd in command_list:
        # Fail if even one command given is invalid
        if cmd not in CATEGORY_COMMANDS_ALL[category]:
            module.fail_json(msg=to_native("Invalid Command '%s'. Valid Commands = %s" % (cmd, CATEGORY_COMMANDS_ALL[category])))

    # Organize by Categories / Commands
    if category == "Accounts":
        ACCOUNTS_COMMANDS = {
            "AddUser": rf_utils.add_user,
            "EnableUser": rf_utils.enable_user,
            "DeleteUser": rf_utils.delete_user,
            "DisableUser": rf_utils.disable_user,
            "UpdateUserRole": rf_utils.update_user_role,
            "UpdateUserPassword": rf_utils.update_user_password,
            "UpdateUserName": rf_utils.update_user_name,
            "UpdateAccountServiceProperties": rf_utils.update_accountservice_properties
        }

        # execute only if we find an Account service resource
        result = rf_utils._find_accountservice_resource()
        if result['ret'] is False:
            # If a password change is required and the user is attempting to
            # modify their password, try to proceed.
            user['account_passwordchangerequired'] = rf_utils.check_password_change_required(result)
            if len(command_list) == 1 and command_list[0] == "UpdateUserPassword" and user['account_passwordchangerequired']:
                result = rf_utils.update_user_password(user)
            else:
                module.fail_json(msg=to_native(result['msg']))
        else:
            for command in command_list:
                result = ACCOUNTS_COMMANDS[command](user)

    elif category == "Systems":
        # execute only if we find a System resource
        result = rf_utils._find_systems_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            if command.startswith('Power'):
                result = rf_utils.manage_system_power(command)
            elif command == "SetOneTimeBoot":
                boot_opts['override_enabled'] = 'Once'
                result = rf_utils.set_boot_override(boot_opts)
            elif command == "EnableContinuousBootOverride":
                boot_opts['override_enabled'] = 'Continuous'
                result = rf_utils.set_boot_override(boot_opts)
            elif command == "DisableBootOverride":
                boot_opts['override_enabled'] = 'Disabled'
                result = rf_utils.set_boot_override(boot_opts)
            elif command.startswith('IndicatorLed'):
                result = rf_utils.manage_system_indicator_led(command)
            elif command == 'VirtualMediaInsert':
                result = rf_utils.virtual_media_insert(virtual_media, category)
            elif command == 'VirtualMediaEject':
                result = rf_utils.virtual_media_eject(virtual_media, category)
            elif command == 'VerifyBiosAttributes':
                result = rf_utils.verify_bios_attributes(bios_attributes)

    elif category == "Chassis":
        result = rf_utils._find_chassis_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        led_commands = ["IndicatorLedOn", "IndicatorLedOff", "IndicatorLedBlink"]

        # Check if more than one led_command is present
        num_led_commands = sum([command in led_commands for command in command_list])
        if num_led_commands > 1:
            result = {'ret': False, 'msg': "Only one IndicatorLed command should be sent at a time."}
        else:
            for command in command_list:
                if command in led_commands:
                    result = rf_utils.manage_chassis_indicator_led(command)

    elif category == "Sessions":
        # execute only if we find SessionService resources
        resource = rf_utils._find_sessionservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])

        for command in command_list:
            if command == "ClearSessions":
                result = rf_utils.clear_sessions()
            elif command == "CreateSession":
                result = rf_utils.create_session()
            elif command == "DeleteSession":
                result = rf_utils.delete_session(module.params['session_uri'])

    elif category == "Manager":
        # execute only if we find a Manager service resource
        result = rf_utils._find_managers_resource()
        if result['ret'] is False:
            module.fail_json(msg=to_native(result['msg']))

        for command in command_list:
            # standardize on the Power* commands, but allow the the legacy
            # GracefulRestart command
            if command == 'GracefulRestart':
                command = 'PowerGracefulRestart'

            if command.startswith('Power'):
                result = rf_utils.manage_manager_power(command, module.params['wait'], module.params['wait_timeout'])
            elif command == 'ClearLogs':
                result = rf_utils.clear_logs()
            elif command == 'VirtualMediaInsert':
                result = rf_utils.virtual_media_insert(virtual_media, category)
            elif command == 'VirtualMediaEject':
                result = rf_utils.virtual_media_eject(virtual_media, category)
            elif command == 'ResetToDefaults':
                result = rf_utils.manager_reset_to_defaults(module.params['reset_to_defaults_mode'])

    elif category == "Update":
        # execute only if we find UpdateService resources
        resource = rf_utils._find_updateservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])

        for command in command_list:
            if command == "SimpleUpdate":
                result = rf_utils.simple_update(update_opts)
                if 'update_status' in result:
                    return_values['update_status'] = result['update_status']
            elif command == "MultipartHTTPPushUpdate":
                result = rf_utils.multipath_http_push_update(update_opts)
                if 'update_status' in result:
                    return_values['update_status'] = result['update_status']
            elif command == "PerformRequestedOperations":
                result = rf_utils.perform_requested_update_operations(update_opts['update_handle'])

    # Return data back or fail with proper message
    if result['ret'] is True:
        del result['ret']
        changed = result.get('changed', True)
        session = result.get('session', dict())
        module.exit_json(changed=changed, session=session,
                         msg='Action was successful',
                         return_values=return_values)
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
