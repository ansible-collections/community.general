#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018 Dell EMC Inc.
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

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
options:
  category:
    required: true
    description:
      - Category to execute on OOB controller
    type: str
  command:
    required: true
    description:
      - List of commands to execute on OOB controller
    type: list
    elements: str
  baseuri:
    required: true
    description:
      - Base URI of OOB controller
    type: str
  username:
    description:
      - Username for authentication with OOB controller
    type: str
  password:
    description:
      - Password for authentication with OOB controller
    type: str
  auth_token:
    description:
      - Security token for authentication with OOB controller
    type: str
    version_added: 2.3.0
  session_uri:
    description:
      - URI of the session resource
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
      - Username of account to add/delete/modify
    type: str
  new_password:
    required: false
    aliases: [ account_password ]
    description:
      - New password of account to add/modify
    type: str
  roleid:
    required: false
    aliases: [ account_roleid ]
    description:
      - Role of account to add/modify
    type: str
  bootdevice:
    required: false
    description:
      - bootdevice when setting boot configuration
    type: str
  timeout:
    description:
      - Timeout in seconds for URL requests to OOB controller
    default: 10
    type: int
  boot_override_mode:
    description:
      - Boot mode when using an override.
    type: str
    choices: [ Legacy, UEFI ]
    version_added: 3.5.0
  uefi_target:
    required: false
    description:
      - UEFI target when bootdevice is "UefiTarget"
    type: str
  boot_next:
    required: false
    description:
      - BootNext target when bootdevice is "UefiBootNext"
    type: str
  update_username:
    required: false
    aliases: [ account_updatename ]
    description:
      - new update user name for account_username
    type: str
    version_added: '0.2.0'
  account_properties:
    required: false
    description:
      - properties of account service to update
    type: dict
    version_added: '0.2.0'
  resource_id:
    required: false
    description:
      - The ID of the System, Manager or Chassis to modify
    type: str
    version_added: '0.2.0'
  update_image_uri:
    required: false
    description:
      - The URI of the image for the update
    type: str
    version_added: '0.2.0'
  update_protocol:
    required: false
    description:
      - The protocol for the update
    type: str
    version_added: '0.2.0'
  update_targets:
    required: false
    description:
      - The list of target resource URIs to apply the update to
    type: list
    elements: str
    version_added: '0.2.0'
  update_creds:
    required: false
    description:
      - The credentials for retrieving the update image
    type: dict
    version_added: '0.2.0'
    suboptions:
      username:
        required: false
        description:
          - The username for retrieving the update image
        type: str
      password:
        required: false
        description:
          - The password for retrieving the update image
        type: str
  virtual_media:
    required: false
    description:
      - The options for VirtualMedia commands
    type: dict
    version_added: '0.2.0'
    suboptions:
      media_types:
        required: false
        description:
          - The list of media types appropriate for the image
        type: list
        elements: str
      image_url:
        required: false
        description:
          - The URL od the image the insert or eject
        type: str
      inserted:
        required: false
        description:
          - Indicates if the image is treated as inserted on command completion
        type: bool
        default: True
      write_protected:
        required: false
        description:
          - Indicates if the media is treated as write-protected
        type: bool
        default: True
      username:
        required: false
        description:
          - The username for accessing the image URL
        type: str
      password:
        required: false
        description:
          - The password for accessing the image URL
        type: str
      transfer_protocol_type:
        required: false
        description:
          - The network protocol to use with the image
        type: str
      transfer_method:
        required: false
        description:
          - The transfer method to use with the image
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

author: "Jose Delarosa (@jose-delarosa)"
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
'''

RETURN = '''
msg:
    description: Message with action result or error description
    returned: always
    type: str
    sample: "Action was successful"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redfish_utils import RedfishUtils
from ansible.module_utils.common.text.converters import to_native


# More will be added as module features are expanded
CATEGORY_COMMANDS_ALL = {
    "Systems": ["PowerOn", "PowerForceOff", "PowerForceRestart", "PowerGracefulRestart",
                "PowerGracefulShutdown", "PowerReboot", "SetOneTimeBoot", "EnableContinuousBootOverride", "DisableBootOverride",
                "IndicatorLedOn", "IndicatorLedOff", "IndicatorLedBlink"],
    "Chassis": ["IndicatorLedOn", "IndicatorLedOff", "IndicatorLedBlink"],
    "Accounts": ["AddUser", "EnableUser", "DeleteUser", "DisableUser",
                 "UpdateUserRole", "UpdateUserPassword", "UpdateUserName",
                 "UpdateAccountServiceProperties"],
    "Sessions": ["ClearSessions", "CreateSession", "DeleteSession"],
    "Manager": ["GracefulRestart", "ClearLogs", "VirtualMediaInsert",
                "VirtualMediaEject", "PowerOn", "PowerForceOff", "PowerForceRestart",
                "PowerGracefulRestart", "PowerGracefulShutdown", "PowerReboot"],
    "Update": ["SimpleUpdate"]
}


def main():
    result = {}
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
            update_username=dict(type='str', aliases=["account_updatename"]),
            account_properties=dict(type='dict', default={}),
            bootdevice=dict(),
            timeout=dict(type='int', default=10),
            uefi_target=dict(),
            boot_next=dict(),
            boot_override_mode=dict(choices=['Legacy', 'UEFI']),
            resource_id=dict(),
            update_image_uri=dict(),
            update_protocol=dict(),
            update_targets=dict(type='list', elements='str', default=[]),
            update_creds=dict(
                type='dict',
                options=dict(
                    username=dict(),
                    password=dict(no_log=True)
                )
            ),
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
    user = {'account_id': module.params['id'],
            'account_username': module.params['new_username'],
            'account_password': module.params['new_password'],
            'account_roleid': module.params['roleid'],
            'account_updatename': module.params['update_username'],
            'account_properties': module.params['account_properties']}

    # timeout
    timeout = module.params['timeout']

    # System, Manager or Chassis ID to modify
    resource_id = module.params['resource_id']

    # update options
    update_opts = {
        'update_image_uri': module.params['update_image_uri'],
        'update_protocol': module.params['update_protocol'],
        'update_targets': module.params['update_targets'],
        'update_creds': module.params['update_creds']
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
            module.fail_json(msg=to_native(result['msg']))

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
                result = rf_utils.manage_manager_power(command)
            elif command == 'ClearLogs':
                result = rf_utils.clear_logs()
            elif command == 'VirtualMediaInsert':
                result = rf_utils.virtual_media_insert(virtual_media)
            elif command == 'VirtualMediaEject':
                result = rf_utils.virtual_media_eject(virtual_media)

    elif category == "Update":
        # execute only if we find UpdateService resources
        resource = rf_utils._find_updateservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])

        for command in command_list:
            if command == "SimpleUpdate":
                result = rf_utils.simple_update(update_opts)

    # Return data back or fail with proper message
    if result['ret'] is True:
        del result['ret']
        changed = result.get('changed', True)
        session = result.get('session', dict())
        module.exit_json(changed=changed, session=session,
                         msg='Action was successful')
    else:
        module.fail_json(msg=to_native(result['msg']))


if __name__ == '__main__':
    main()
