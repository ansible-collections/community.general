from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.ilo_redfish_utils import iLORedfishUtils

__metaclass__ = type

DOCUMENTATION = '''
---
module: iLO Redfish Info
short_description: Builds Redfish URIs locally and sends them to remote OOB controllers to get information back.
                For use with HPE iLO operations that require Redfish OEM extensions.
description:
    - "Provides an interface to get information back"
requirements:
    - "python >= 3.8"
    - "ansible >= 3.2"
author:
    - "Bhavya B (@Bhavya06)"
'''

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

CATEGORY_COMMANDS_ALL = {
    "Accounts": ["ListiLOUsers"],
    "Serverclone": ["SaveUsers", "SaveEthernetInterface", "SaveSmartStorage"],
    "Systems": ["SaveBIOSConfig"],
    "Sessions": ["GetiLOSessions"]
}

CATEGORY_COMMANDS_DEFAULT = {}


def main():
    result = {}
    category_list = []
    module = AnsibleModule(
        argument_spec=dict(
            category=dict(type='list', default=['Systems']),
            command=dict(type='list'),
            baseuri=dict(required=True),
            username=dict(),
            password=dict(),
            auth_token=dict(),
            timeout=dict(type='int', default=10)
        ),
        supports_check_mode=False
    )

    is_old_facts = module._name == 'redfish_facts'
    if is_old_facts:
        module.deprecate("The 'redfish_facts' module has been renamed to 'redfish_info', "
                         "and the renamed one no longer returns ansible_facts", version='2.13')

    session_id = None
    creds = {"user": module.params['username'],
             "pswd": module.params['password'],
             "token": module.params['auth_token']}

    timeout = module.params['timeout']
    if module.params['baseuri'] is None:
        module.fail_json(msg=to_native("Baseuri is empty."))

    root_uri = "https://" + module.params['baseuri']
    # Auto_login = False
    rf_utils = iLORedfishUtils(creds, root_uri, timeout, module)

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

    if category == "Accounts":
        resource = rf_utils._find_accountservice_resource()
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])

        for command in command_list:
            if command == "ListiLOUsers":
                result = rf_utils.list_iLOusers()
                result['id'] = session_id

    elif category == "Serverclone":
        for command in command_list:
            if command == "SaveUsers":
                resource = rf_utils._find_accountservice_resource(session_id)
                if resource['ret'] is False:
                    module.fail_json(msg=resource['msg'])
                result = rf_utils.accountSave(session_id)

            elif command == "SaveEthernetInterface":
                resource = rf_utils._find_managers_resource(session_id)
                if(resource['ret'] is False):
                    module.fail_json(msg=to_native(resource['msg']))
                result = rf_utils.ethernetInterfaceSave(session_id)

            elif command == "SaveSmartStorage":
                resource = rf_utils._find_systems_resource(session_id)
                if resource['ret'] is False:
                    module.fail_json(msg=resource['msg'])
                result = rf_utils.SmartStorageSave(session_id)

    elif category == "Systems":
        resource = rf_utils._find_systems_resource(session_id)
        if resource['ret'] is False:
            module.fail_json(msg=resource['msg'])

        for command in command_list:
            if command == "SaveBIOSConfig":
                result = rf_utils.save_biosconfig(session_id)

    elif category == "Sessions":
        for command in command_list:
            if command == "GetiLOSessions":
                result = rf_utils.getiLOSessions()

    if result['ret'] is True:
        del result['ret']
        if is_old_facts:
            module.exit_json(ansible_facts=dict(redfish_facts=result))
        else:
            module.exit_json(redfish_facts=result)
    else:
        module.fail_json(msg=to_native(result))


if __name__ == '__main__':
    main()
