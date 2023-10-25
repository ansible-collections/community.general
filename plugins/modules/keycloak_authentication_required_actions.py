#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_authentication_required_actions

short_description: Allows administration of Keycloak authentication required actions

description:
    - This module can register, update and delete required actions.
    - It also filters out any duplicate required actions by their alias. The first occurrence is preserved.

version_added: 7.1.0

attributes:
    check_mode:
        support: full
    diff_mode:
        support: full

options:
    realm:
        description:
            - The name of the realm in which are the authentication required actions.
        required: true
        type: str
    required_actions:
        elements: dict
        description:
            - Authentication required action.
        suboptions:
            alias:
                description:
                    - Unique name of the required action.
                required: true
                type: str
            config:
                description:
                    - Configuration for the required action.
                type: dict
            defaultAction:
                description:
                    - Indicates, if any new user will have the required action assigned to it.
                type: bool
            enabled:
                description:
                    - Indicates, if the required action is enabled or not.
                type: bool
            name:
                description:
                    - Displayed name of the required action. Required for registration.
                type: str
            priority:
                description:
                    - Priority of the required action.
                type: int
            providerId:
                description:
                    - Provider ID of the required action. Required for registration.
                type: str
        type: list
    state:
        choices: [ "absent", "present" ]
        description:
            - Control if the realm authentication required actions are going to be registered/updated (V(present)) or deleted (V(absent)).
        required: true
        type: str

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
    - Skrekulko (@Skrekulko)
'''

EXAMPLES = '''
- name: Register a new required action.
  community.general.keycloak_authentication_required_actions:
    auth_client_id: "admin-cli"
    auth_keycloak_url: "http://localhost:8080"
    auth_password: "password"
    auth_realm: "master"
    auth_username: "admin"
    realm: "master"
    required_action:
      - alias: "TERMS_AND_CONDITIONS"
        name: "Terms and conditions"
        providerId: "TERMS_AND_CONDITIONS"
        enabled: true
    state: "present"

- name: Update the newly registered required action.
  community.general.keycloak_authentication_required_actions:
    auth_client_id: "admin-cli"
    auth_keycloak_url: "http://localhost:8080"
    auth_password: "password"
    auth_realm: "master"
    auth_username: "admin"
    realm: "master"
    required_action:
      - alias: "TERMS_AND_CONDITIONS"
        enabled: false
    state: "present"

- name: Delete the updated registered required action.
  community.general.keycloak_authentication_required_actions:
    auth_client_id: "admin-cli"
    auth_keycloak_url: "http://localhost:8080"
    auth_password: "password"
    auth_realm: "master"
    auth_username: "admin"
    realm: "master"
    required_action:
      - alias: "TERMS_AND_CONDITIONS"
    state: "absent"
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Representation of the authentication required actions after module execution.
    returned: on success
    type: complex
    contains:
        alias:
            description:
                - Unique name of the required action.
            sample: test-provider-id
            type: str
        config:
            description:
                - Configuration for the required action.
            sample: {}
            type: dict
        defaultAction:
            description:
                - Indicates, if any new user will have the required action assigned to it.
            sample: false
            type: bool
        enabled:
            description:
                - Indicates, if the required action is enabled or not.
            sample: false
            type: bool
        name:
            description:
                - Displayed name of the required action. Required for registration.
            sample: Test provider ID
            type: str
        priority:
            description:
                - Priority of the required action.
            sample: 90
            type: int
        providerId:
            description:
                - Provider ID of the required action. Required for registration.
            sample: test-provider-id
            type: str

'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule


def sanitize_required_actions(objects):
    for obj in objects:
        alias = obj['alias']
        name = obj['name']
        provider_id = obj['providerId']

        if not name:
            obj['name'] = alias

        if provider_id != alias:
            obj['providerId'] = alias

    return objects


def filter_duplicates(objects):
    filtered_objects = {}

    for obj in objects:
        alias = obj["alias"]

        if alias not in filtered_objects:
            filtered_objects[alias] = obj

    return list(filtered_objects.values())


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        realm=dict(type='str', required=True),
        required_actions=dict(
            type='list',
            elements='dict',
            options=dict(
                alias=dict(type='str', required=True),
                config=dict(type='dict'),
                defaultAction=dict(type='bool'),
                enabled=dict(type='bool'),
                name=dict(type='str'),
                priority=dict(type='int'),
                providerId=dict(type='str')
            )
        ),
        state=dict(type='str', choices=['present', 'absent'], required=True)
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
        required_together=([['auth_realm', 'auth_username', 'auth_password']])
    )

    result = dict(changed=False, msg='', end_state={}, diff=dict(before={}, after={}))

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Convenience variables
    realm = module.params.get('realm')
    desired_required_actions = module.params.get('required_actions')
    state = module.params.get('state')

    # Sanitize required actions
    desired_required_actions = sanitize_required_actions(desired_required_actions)

    # Filter out duplicate required actions
    desired_required_actions = filter_duplicates(desired_required_actions)

    # Get required actions
    before_required_actions = kc.get_required_actions(realm=realm)

    if state == 'present':
        # Initialize empty lists to hold the required actions that need to be
        # registered, updated, and original ones of the updated one
        register_required_actions = []
        before_updated_required_actions = []
        updated_required_actions = []

        # Loop through the desired required actions and check if they exist in the before required actions
        for desired_required_action in desired_required_actions:
            found = False

            # Loop through the before required actions and check if the aliases match
            for before_required_action in before_required_actions:
                if desired_required_action['alias'] == before_required_action['alias']:
                    update_required = False

                    # Fill in the parameters
                    for k, v in before_required_action.items():
                        if k not in desired_required_action or desired_required_action[k] is None:
                            desired_required_action[k] = v

                    # Loop through the keys of the desired and before required actions
                    # and check if there are any differences between them
                    for key in desired_required_action.keys():
                        if key in before_required_action and desired_required_action[key] != before_required_action[key]:
                            update_required = True
                            break

                    # If there are differences, add the before and desired required actions
                    # to their respective lists for updating
                    if update_required:
                        before_updated_required_actions.append(before_required_action)
                        updated_required_actions.append(desired_required_action)
                    found = True
                    break
            # If the desired required action is not found in the before required actions,
            # add it to the list of required actions to register
            if not found:
                # Check if name is provided
                if 'name' not in desired_required_action or desired_required_action['name'] is None:
                    module.fail_json(
                        msg='Unable to register required action %s in realm %s: name not included'
                        % (desired_required_action['alias'], realm)
                    )

                # Check if provider ID is provided
                if 'providerId' not in desired_required_action or desired_required_action['providerId'] is None:
                    module.fail_json(
                        msg='Unable to register required action %s in realm %s: providerId not included'
                        % (desired_required_action['alias'], realm)
                    )

                register_required_actions.append(desired_required_action)

        # Handle diff
        if module._diff:
            diff_required_actions = updated_required_actions.copy()
            diff_required_actions.extend(register_required_actions)

            result['diff'] = dict(
                before=before_updated_required_actions,
                after=diff_required_actions
            )

        # Handle changed
        if register_required_actions or updated_required_actions:
            result['changed'] = True

        # Handle check mode
        if module.check_mode:
            if register_required_actions or updated_required_actions:
                result['change'] = True
                result['msg'] = 'Required actions would be registered/updated'
            else:
                result['change'] = False
                result['msg'] = 'Required actions would not be registered/updated'

            module.exit_json(**result)

        # Register required actions
        if register_required_actions:
            for register_required_action in register_required_actions:
                kc.register_required_action(realm=realm, rep=register_required_action)
                kc.update_required_action(alias=register_required_action['alias'], realm=realm, rep=register_required_action)

        # Update required actions
        if updated_required_actions:
            for updated_required_action in updated_required_actions:
                kc.update_required_action(alias=updated_required_action['alias'], realm=realm, rep=updated_required_action)

        # Initialize the final list of required actions
        final_required_actions = []

        # Iterate over the before_required_actions
        for before_required_action in before_required_actions:
            # Check if there is an updated_required_action with the same alias
            updated_required_action_found = False

            for updated_required_action in updated_required_actions:
                if updated_required_action['alias'] == before_required_action['alias']:
                    # Merge the two dictionaries, favoring the values from updated_required_action
                    merged_dict = {}
                    for key in before_required_action.keys():
                        if key in updated_required_action:
                            merged_dict[key] = updated_required_action[key]
                        else:
                            merged_dict[key] = before_required_action[key]

                    for key in updated_required_action.keys():
                        if key not in before_required_action:
                            merged_dict[key] = updated_required_action[key]

                    # Add the merged dictionary to the final list of required actions
                    final_required_actions.append(merged_dict)

                    # Mark the updated_required_action as found
                    updated_required_action_found = True

                    # Stop looking for updated_required_action
                    break

            # If no matching updated_required_action was found, add the before_required_action to the final list of required actions
            if not updated_required_action_found:
                final_required_actions.append(before_required_action)

        # Append any remaining updated_required_actions that were not merged
        for updated_required_action in updated_required_actions:
            if not any(updated_required_action['alias'] == action['alias'] for action in final_required_actions):
                final_required_actions.append(updated_required_action)

        # Append newly registered required actions
        final_required_actions.extend(register_required_actions)

        # Handle message and end state
        result['msg'] = 'Required actions registered/updated'
        result['end_state'] = final_required_actions
    else:
        # Filter out the deleted required actions
        final_required_actions = []
        delete_required_actions = []

        for before_required_action in before_required_actions:
            delete_action = False

            for desired_required_action in desired_required_actions:
                if before_required_action['alias'] == desired_required_action['alias']:
                    delete_action = True
                    break

            if not delete_action:
                final_required_actions.append(before_required_action)
            else:
                delete_required_actions.append(before_required_action)

        # Handle diff
        if module._diff:
            result['diff'] = dict(
                before=before_required_actions,
                after=final_required_actions
            )

        # Handle changed
        if delete_required_actions:
            result['changed'] = True

        # Handle check mode
        if module.check_mode:
            if final_required_actions:
                result['change'] = True
                result['msg'] = 'Required actions would be deleted'
            else:
                result['change'] = False
                result['msg'] = 'Required actions would not be deleted'

            module.exit_json(**result)

        # Delete required actions
        if delete_required_actions:
            for delete_required_action in delete_required_actions:
                kc.delete_required_action(alias=delete_required_action['alias'], realm=realm)

        # Handle message and end state
        result['msg'] = 'Required actions deleted'
        result['end_state'] = final_required_actions

    module.exit_json(**result)


if __name__ == '__main__':
    main()
