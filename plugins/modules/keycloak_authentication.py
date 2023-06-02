#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2019, INSPQ <philippe.gauthier@inspq.qc.ca>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_authentication

short_description: Configure authentication in Keycloak

description:
    - This module supports creation, making a copy, deletion and configuration of an authentication flow.
    - It can also add or update an authentication execution to a flow (step or sub-flow). Deletion is not supported.
    - This module also supports registration, update and deletion of an authentication required action.

version_added: "7.0.0"

attributes:
    check_mode:
        support: full
    diff_mode:
        support: full

options:
    bind_flow:
        description:
            - Assign the authentication flow to be used by a realm authentication flow.
        choices: [ "browserFlow", "clientAuthenticationFlow", "directGrantFlow", "dockerAuthenticationFlow", "registrationFlow", "resetCredentialsFlow" ]
        type: str
    config:
        description:
            - Configuration for a configurable authentication flow.
        suboptions:
            alias:
                description:
                    - Unique name of the configuration.
                type: str
            config:
                description:
                    - The inner parameters of the configuration specific to the authentication execution.
                type: dict
            id:
                description:
                    - ID of the configuration used for updating.
                type: str
        type: dict
    copy_from:
        description:
            - Unique name of the authentication flow to copy from.
        type: str
    execution:
        description:
            - Authentication execution (step or sub-flow) of the authentication flow.
        suboptions:
            alias:
                description:
                    - Name of the authentication execution taken from its configuration.
                type: str
            authenticationConfig:
                description:
                    - ID of the authentication execution's configuration.
                type: str
            authenticationFlow:
                description:
                    - Indicates, if the authentication execution is a step (false) or a sub-flow (true).
                required: true
                type: bool
            configurable:
                description:
                    - Indicates, if the authentication execution is configurable (depends on the provider).
                type: bool
            description:
                description:
                    - Description of the authentication execution.
                type: str
            displayName:
                description:
                    - Display name of the authentication execution.
                type: str
            flowId:
                description:
                    - ID of the authentication execution sub-flow.
                type: str
            id:
                description:
                    - ID of the authentication execution (step or sub-flow).
                type: str
            index:
                description:
                    - The priortiy of an inner authentication execution of its outer authentication execution.
                type: int
            level:
                description:
                    - The priority of the authentication execution in the authentication flow.
                type: int
            providerId:
                description:
                    - ID (specific name) of the provider.
                required: true
                type: str
            requirement:
                choices: [ "REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL" ]
                default: "DISABLED"
                description:
                    - Indicates the requirement of the authentication flow.
                type: str
            requirementChoices:
                elements: str
                default: [ "REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL" ]
                description:
                    - A list of requirement choices of the authentication execution.
                type: list
            flowType:
                choices: [ "basic-flow", "client-flow" ]
                default: "basic-flow"
                description:
                    - Indicates the flow type of the authentication execution (sub-flow).
                type: str
        type: dict
    flow:
        description:
            - Authentication flow.
        suboptions:
            alias:
                description:
                    - Unique name of the authentication flow.
                required: true
                type: str
            builtIn:
                default: false
                description:
                    - Indicates, if the authentication is built-in or not.
                type: bool
            description:
                description:
                    - Description of the authentication flow.
                type: str
            id:
                description:
                    - ID of the authentication flow.
                type: str
            providerId:
                choices: [ "basic-flow", "client-flow" ]
                default: "basic-flow"
                description:
                    - Indicates, if the authentication flow is a basic or a client flow.
                type: str
            topLevel:
                default: true
                description:
                    - Indicates, if the authentication flow is top-level or not.
                type: bool
        type: dict
    realm:
        description:
            - Name of the realm, to which the authentication is modified using this module.
        required: true
        type: str
    required_action:
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
                default: false
                description:
                    - Indicates, if any new user will have the required action assigned to it.
                type: bool
            enabled:
                default: false
                description:
                    - Indicates, if the required action is enabled or not.
                type: bool
            name:
                description:
                    - Displayed name of the required action.
                type: str
            priority:
                description:
                    - Priority of the required action.
                type: int
            providerId:
                description:
                    - Provider ID of the required action.
                type: str
        type: dict
    state:
        choices: [ "absent", "present" ]
        description:
            - Control if the realm authentication is going to be updated (creation/update) or deleted.
        required: true
        type: str

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
    - Philippe Gauthier (@elfelip)
    - Gaëtan Daubresse (@Gaetan2907)
'''

EXAMPLES = '''
    - name: Create an authentication flow with a configurable execution step with a configuration to it, and add assign it to a realm authentication flow.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        bind_flow: "resetCredentialsFlow"
        config:
          alias: "Require OTP for password reset"
          config:
            defaultOtpOutcome: "force"
            otpControlAttribute: "force"
        execution:
          authenticationFlow: False
          displayName: "Conditional OTP Form"
          providerId: "auth-conditional-otp-form"
          requirement: "REQUIRED"
        flow:
          alias: "test_flow"
          description: "This is a test flow."
        realm: "master"
        state: "present"

    - name: Add an authentication execution sub-flow to the newly created authentication flow.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        execution:
          alias: "test_sub_flow"
          authenticationFlow: True
          description: "This is a test sub-flow."
          providerId: "registration-page-form"
          type: "basic-flow"
        flow:
          alias: "test_flow"
        realm: "master"
        state: "present"

    - name: Add an authentication execution step to the newly created authentication execution sub-flow.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        execution:
          authenticationFlow: False
          providerId: "reset-credentials-choose-user"
          requirement: "REQUIRED"
        flow:
          alias: "test_sub_flow"
        realm: "master"
        state: "present"

    - name: Delete the authentication flow.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        flow:
          alias: "test_flow"
        realm: "master"
        state: "absent"

    - name: Register a new required action.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        realm: "master"
        require_action:
          alias: "test_required_action"
          name: "Test Required Action"
          enabled: true
          defaultAction: false
          priority: 999
        state: "present"

    - name: Update the newly registered required action.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        realm: "master"
        require_action:
          alias: "test_flow"
          priority: 111
        state: "present"

    - name: Delete the updated registered required action.
      community.general.keycloak_authentication:
        auth_client_id: "admin-cli"
        auth_keycloak_url: "http://localhost:8080"
        auth_password: "password"
        auth_realm: "master"
        auth_username: "admin"
        realm: "master"
        require_action:
          alias: "test_required_action"
        state: "absent"
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Representation of the authentication after module execution.
    returned: on success
    type: dict
    sample: {
      "alias": "Copy of first broker login",
      "authenticationExecutions": [
        {
          "alias": "review profile config",
          "authenticationConfig": {
            "alias": "review profile config",
            "config": { "update.profile.on.first.login": "missing" },
            "id": "6f09e4fb-aad4-496a-b873-7fa9779df6d7"
          },
          "configurable": true,
          "displayName": "Review Profile",
          "id": "8f77dab8-2008-416f-989e-88b09ccf0b4c",
          "index": 0,
          "level": 0,
          "providerId": "idp-review-profile",
          "requirement": "REQUIRED",
          "requirementChoices": [ "REQUIRED", "ALTERNATIVE", "DISABLED" ]
        }
      ],
      "builtIn": false,
      "description": "Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account",
      "id": "bc228863-5887-4297-b898-4d988f8eaa5c",
      "providerId": "basic-flow",
      "topLevel": true
    }
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak \
    import KeycloakAPI, keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        bind_flow=dict(
            type='str',
            choices=[
                "browserFlow",
                "clientAuthenticationFlow",
                "directGrantFlow",
                "dockerAuthenticationFlow",
                "registrationFlow",
                "resetCredentialsFlow",
            ]
        ),
        config=dict(
            type='dict',
            options=dict(
                alias=dict(type='str'),
                config=dict(type='dict'),
                id=dict(type='str')
            )
        ),
        copy_from=dict(type='str'),
        execution=dict(
            type='dict',
            options=dict(
                alias=dict(type='str'),
                authenticationConfig=dict(type='str'),
                authenticationFlow=dict(type='bool', required=True),
                configurable=dict(type='bool'),
                description=dict(type='str'),
                displayName=dict(type='str'),
                flowId=dict(type='str'),
                id=dict(type='str'),
                index=dict(type='int'),
                level=dict(type='int'),
                providerId=dict(type='str', required=True),
                requirement=dict(
                    type='str',
                    default='DISABLED',
                    choices=[
                        "REQUIRED",
                        "ALTERNATIVE",
                        "DISABLED",
                        "CONDITIONAL"
                    ]
                ),
                requirementChoices=dict(
                    default=["REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL"],
                    elements="str",
                    type="list",
                ),
                flowType=dict(
                    type='str',
                    default='basic-flow',
                    choices=[
                        "basic-flow",
                        "client-flow",
                    ]
                ),
            )
        ),
        flow=dict(
            type='dict',
            options=dict(
                alias=dict(type='str', required=True),
                builtIn=dict(type='bool', default=False),
                description=dict(type='str'),
                id=dict(type='str'),
                providerId=dict(
                    type='str',
                    default='basic-flow',
                    choices=[
                        'basic-flow',
                        'client-flow',
                    ]
                ),
                topLevel=dict(type='bool', default=True)
            )
        ),
        realm=dict(type='str', required=True),
        required_action=dict(
            type='dict',
            options=dict(
                alias=dict(type='str', required=True),
                config=dict(type='dict'),
                defaultAction=dict(type='bool', default=False),
                enabled=dict(type='bool', default=False),
                name=dict(type='str'),
                priority=dict(type='int'),
                providerId=dict(type='str')
            )
        ),
        state=dict(
            type='str',
            choices=['absent', 'present'],
            required=True
        ),
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
    bind_flow = module.params.get('bind_flow')
    desired_config = module.params.get('config')
    copy_from = module.params.get('copy_from')
    desired_execution = module.params.get('execution')
    desired_flow = module.params.get('flow')
    desired_required_action = module.params.get('required_action')
    realm = module.params.get('realm')
    state = module.params.get('state')

    # Delete unused parameters
    dicts = [desired_execution, desired_flow, desired_required_action]
    for d in dicts:
        if d is not None:
            for k in list(d.keys()):
                if d[k] is None:
                    del d[k]

    if state == 'present':
        # Handle authentication flow
        if desired_flow:
            # Get authentication flow
            before_flow = kc.get_authentication_flow_by_alias(
                alias=desired_flow['alias'],
                realm=realm
            )

            if before_flow:
                # Get authentication executions
                before_executions = kc.get_authentication_executions(
                    alias=desired_flow['alias'],
                    realm=realm
                )
            else:
                before_executions = []

            # Update
            if before_flow:
                # Fill in parameters
                for k, v in before_flow.items():
                    if k not in desired_flow or desired_flow[k] is None:
                        desired_flow[k] = v

                # Differences found
                if desired_flow != before_flow:
                    if not module.check_mode:
                        kc.update_authentication_flow(
                            realm=realm,
                            id=desired_flow['id'],
                            flow=desired_flow
                        )

                        desired_flow = kc.get_authentication_flow_by_alias(
                            alias=desired_flow['alias'],
                            realm=realm
                        )

                    if module._diff:
                        result['diff']['before']["flow"] = before_flow
                        result['diff']['after']["flow"] = desired_flow

                    result['changed'] = True
                    result['end_state']["flow"] = desired_flow
            # Create
            else:
                # Create from a copy
                if copy_from:
                    if not module.check_mode:
                        kc.copy_authentication_flow(
                            alias=copy_from,
                            name=desired_flow['alias'],
                            realm=realm
                        )
                else:
                    if not module.check_mode:
                        kc.create_authentication_flow(
                            flow=desired_flow,
                            realm=realm
                        )

                    desired_flow = kc.get_authentication_flow_by_alias(
                        alias=desired_flow['alias'],
                        realm=realm
                    )

                if module._diff:
                    result['diff']['before']['flow'] = {}
                    result['diff']['after']['flow'] = desired_flow

                result['changed'] = True
                result['end_state']['flow'] = desired_flow

            # Bind flow
            if bind_flow:
                # Get realm info
                realm_info = kc.get_realm_info_by_id(
                    realm=realm
                )

                # Not assigned yet
                if (
                    (bind_flow in realm_info and realm_info[bind_flow] != desired_flow['alias']) or
                    bind_flow not in realm_info
                ):
                    if not module.check_mode:
                        kc.update_realm(
                            realmrep={
                                bind_flow: desired_flow['alias']
                            },
                            realm=realm
                        )

                        if module._diff:
                            result['diff']['before']['bind_flow'] = {
                                bind_flow: realm_info[bind_flow]
                            }
                            result['diff']['after']['bind_flow'] = {
                                bind_flow: desired_flow['alias']
                            }

                    result['changed'] = True
                    result['end_state']['bind_flow'] = {
                        bind_flow: desired_flow['alias']
                    }

            # Handle authentication execution (step and sub-flow)
            if desired_execution:
                # Try to find closest match
                found_match = False
                if before_executions:
                    # Search using ID or flow ID
                    for before_execution in before_executions:
                        if (
                            'id' in desired_execution and 'id' in before_execution and
                            desired_execution['id'] == before_execution['id']
                        ) or (
                            'flowId' in desired_execution and 'flowId' in before_execution and
                            desired_execution['flowId'] == before_execution['flowId']
                        ):
                            found_match = True
                            break

                    if not found_match:
                        # Search using index and level
                        for before_execution in before_executions:
                            if (
                                'index' in desired_execution and 'index' in before_execution and
                                'level' in desired_execution and 'level' in before_execution and
                                desired_execution['index'] == before_execution['index'] and
                                desired_execution['level'] == before_execution['level']
                            ):
                                found_match = True
                                break

                    if not found_match:
                        # Search using displayName
                        for before_execution in before_executions:
                            if (
                                'displayName' in desired_execution and 'displayName' in before_execution and
                                desired_execution['displayName'] == before_execution['displayName']
                            ):
                                found_match = True
                                break

                    # Update
                    if found_match:
                        # Sanitize authentication execution step (authenticationFlow not needed during update)
                        del desired_execution['authenticationFlow']

                        # Fill in parameters
                        for k, v in before_execution.items():
                            if k not in desired_execution or desired_execution[k] is None:
                                desired_execution[k] = v

                        # Sanitize
                        del desired_execution['flowType']

                        # Differences found
                        if desired_execution != before_execution:
                            if not module.check_mode:
                                kc.update_authentication_execution(
                                    alias=desired_flow['alias'],
                                    rep=desired_execution,
                                    realm=realm
                                )

                                # Handle priority (index) increase/decrease
                                if before_execution['index'] - desired_execution['index'] != 0:
                                    kc.change_execution_priority(
                                        executionId=desired_execution['id'],
                                        diff=before_execution['index'] - desired_execution['index'],
                                        realm=realm
                                    )

                            if module._diff:
                                result['diff']['before']['execution'] = before_execution

                            result['changed'] = True

                # Create (also not found)
                if found_match is False:
                    if not module.check_mode:
                        # Sub-Flow
                        if desired_execution['authenticationFlow']:
                            data = {}
                            if 'alias' in desired_execution:
                                data['alias'] = desired_execution['alias']
                            else:
                                data['alias'] = desired_execution['displayName']
                            data['provider'] = 'registration-page-form'
                            data['type'] = desired_execution['flowType']
                            kc.create_authentication_execution_subflow(
                                alias=desired_flow['alias'],
                                data=data,
                                realm=realm
                            )

                            # Find the newly create authentication execution
                            before_executions = kc.get_authentication_executions(
                                alias=desired_flow['alias'],
                                realm=realm
                            )

                            for index, before_execution in enumerate(before_executions):
                                parentFound = False

                                # Looking for parent flow (sub-flow)
                                if (
                                    'authenticationFlow' in before_execution and before_execution['authenticationFlow'] and
                                    before_execution['displayName'] == desired_flow['alias']
                                ):
                                    parentFound = True
                                    parentLevel = before_execution['level']

                                if parentFound:
                                    # Level difference found
                                    if before_execution == parentLevel:
                                        # Get the previous one
                                        before_execution = before_executions[index]
                                        break
                        # Step
                        else:
                            data = {}
                            data['provider'] = desired_execution['providerId']
                            kc.create_authentication_execution_step(
                                alias=desired_flow['alias'],
                                data=data,
                                realm=realm
                            )

                            # Get the newly created authentication execution step
                            before_execution = kc.get_authentication_executions(
                                alias=desired_flow['alias'],
                                realm=realm
                            )[-1]

                        # Sanitize
                        del desired_execution['flowType']
                        del desired_execution['authenticationFlow']

                        # Fill in parameters
                        for k, v in before_execution.items():
                            if k not in desired_execution or desired_execution[k] is None:
                                desired_execution[k] = v

                        kc.update_authentication_execution(
                            alias=desired_flow['alias'],
                            rep=desired_execution,
                            realm=realm
                        )

                        # Handle priority (index) increase/decrease
                        if before_execution['index'] - desired_execution['index'] != 0:
                            kc.change_execution_priority(
                                executionId=desired_execution['id'],
                                diff=before_execution['index'] - desired_execution['index'],
                                realm=realm
                            )

                    if module._diff:
                        result['diff']['before']['execution'] = {}

                    result['changed'] = True

                # Handle authentication execution configuration (only if configurable)
                if desired_config and 'configurable' in desired_execution and desired_execution['configurable']:
                    # Update
                    if 'authenticationConfig' in desired_execution and desired_execution['authenticationConfig']:
                        before_config = kc.get_authenticator_config(
                            id=desired_execution['authenticationConfig'],
                            realm=realm
                        )

                        # Fill in parameters
                        for k, v in before_config.items():
                            if k not in desired_config or desired_config[k] is None:
                                desired_config[k] = v

                        # Differences found
                        if desired_config != before_config:
                            if not module.check_mode:
                                kc.update_authenticator_config(
                                    id=desired_config['id'],
                                    rep=desired_config,
                                    realm=realm
                                )

                            if module._diff:
                                result['diff']['before']['config'] = before_config
                    # Create
                    else:
                        if not module.check_mode:
                            kc.create_authenticator_config(
                                executionId=desired_execution['id'],
                                rep=desired_config,
                                realm=realm
                            )

                        if module._diff:
                            result['diff']['before']['config'] = {}

                    # Get the latest version of the authentication execution
                    desired_execution = list(
                        filter(lambda execution: execution['id'] == desired_execution['id'], kc.get_authentication_executions(
                            alias=desired_flow['alias'],
                            realm=realm
                        ))
                    )[0]

                    # Get the lastest version of the authenticator configuration
                    desired_config = kc.get_authenticator_config(
                        id=desired_execution['authenticationConfig'],
                        realm=realm
                    )

                    if module._diff:
                        result['diff']['after']['config'] = desired_config

                    result['changed'] = True
                    result['end_state']['config'] = desired_config

                # Get the latest version of the authentication execution
                desired_execution = list(
                    filter(lambda execution: execution['id'] == desired_execution['id'], kc.get_authentication_executions(
                        alias=desired_flow['alias'],
                        realm=realm
                    ))
                )[0]

                if module._diff:
                    result['diff']['execution']['after'] = desired_execution

                result['end_state']['execution'] = desired_execution

        # Handle required action
        if desired_required_action:
            # Get required action
            before_required_action = kc.get_required_action(
                alias=desired_required_action['alias'],
                realm=realm
            )

            # Update
            if before_required_action:
                # Fill in parameters
                for k, v in before_required_action.items():
                    if k not in desired_required_action or desired_required_action[k] is None:
                        desired_required_action[k] = v

                # Differences found
                if desired_required_action != before_required_action:
                    if module._diff:
                        result['diff']['before']['required_action'] = before_required_action
                        result['diff']['after']['required_action'] = desired_required_action

                    if not module.check_mode:
                        kc.update_required_action(
                            alias=desired_required_action['alias'],
                            realm=realm,
                            rep=desired_required_action
                        )

                    result['changed'] = True
                    result['end_state']['required_action'] = desired_required_action
            # Register
            else:
                # Use the alias as the name of the required action if not provided
                if 'name' not in desired_required_action:
                    desired_required_action['name'] = desired_required_action['alias']

                # providerId == alias, so set it, if it's not already
                if 'providerId' not in desired_required_action:
                    desired_required_action['providerId'] = desired_required_action['alias']

                if not module.check_mode:
                    kc.register_required_action(
                        rep=desired_required_action,
                        realm=realm
                    )

                # Get the newly registered required action
                before_required_action = kc.get_required_action(
                    alias=desired_required_action['alias'],
                    realm=realm
                )

                # Fill in parameters
                for k, v in before_required_action.items():
                    if k not in desired_required_action or desired_required_action[k] is None:
                        desired_required_action[k] = v

                if module._diff:
                    result['diff']['before']['required_action'] = {}
                    result['diff']['after']['required_action'] = desired_required_action

                result['changed'] = True
                result['end_state']['required_action'] = desired_required_action
    else:
        # Handling flow and executions
        if desired_flow:
            # Get authentication flow:
            before_flow = kc.get_authentication_flow_by_alias(
                alias=desired_flow['alias'],
                realm=realm
            )

            # Delete
            if before_flow:
                if module._diff:
                    result['diff']['before']['required_action'] = before_flow
                    result['diff']['after']['required_action'] = {}

                if not module.check_mode:
                    kc.delete_authentication_flow_by_id(
                        id=before_flow['id'],
                        realm=realm
                    )

                result['changed'] = True
                result['end_state']['authentication_flow'] = {}

        # Handle required action
        if desired_required_action:
            # Get required action
            before_required_action = kc.get_required_action(
                alias=desired_required_action['alias'],
                realm=realm
            )

            # Delete
            if before_required_action:
                if module._diff:
                    result['diff']['before']['required_action'] = before_required_action
                    result['diff']['after']['required_action'] = {}

                if not module.check_mode:
                    kc.delete_required_action(
                        alias=desired_required_action['alias'],
                        realm=realm
                    )

                result['changed'] = True
                result['end_state']['required_action'] = {}

    # Handle msg
    if result['changed']:
        if module.check_mode:
            result['msg'] = 'Authentication would be updated'
        else:
            result['msg'] = 'Authentication updated'
    else:
        if module.check_mode:
            result['msg'] = 'Authentication would not be updated'
        else:
            result['msg'] = 'Authentication not updated'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
