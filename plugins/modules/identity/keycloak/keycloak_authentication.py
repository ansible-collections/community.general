#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, INSPQ <philippe.gauthier@inspq.qc.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_authentication
short_description: Configure authentication in Keycloak
description:
    - This module actually can only make a copy of an existing authentication flow, add an execution to it and configure it.
    - It can also delete the flow.
version_added: "3.3.0"
options:
    realm:
        description:
            - The name of the realm in which is the authentication.
        required: true
        type: str
    alias:
        description:
            - Alias for the authentication flow.
        required: true
        type: str
    description:
        description:
            - Description of the flow.
        type: str
    providerId:
        description:
            - C(providerId) for the new flow when not copied from an existing flow.
        type: str
    copyFrom:
        description:
            - C(flowAlias) of the authentication flow to use for the copy.
        type: str
    authenticationExecutions:
        description:
            - Configuration structure for the executions.
        type: list
        elements: dict
        suboptions:
            providerId:
                description:
                    - C(providerID) for the new flow when not copied from an existing flow.
                type: str
            displayName:
                description:
                    - Name of the execution or subflow to create or update.
                type: str
            requirement:
                description:
                    - Control status of the subflow or execution.
                choices: [ "REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL" ]
                type: str
            flowAlias:
                description:
                    - Alias of parent flow.
                type: str
            authenticationConfig:
                description:
                    - Describe the config of the authentication.
                type: dict
            index:
                description:
                    - Priority order of the execution.
                type: int
    state:
        description:
            - Control if the authentication flow must exists or not.
        choices: [ "present", "absent" ]
        default: present
        type: str
    force:
        type: bool
        default: false
        description:
            - If C(true), allows to remove the authentication flow and recreate it.
extends_documentation_fragment:
- community.general.keycloak

author:
    - Philippe Gauthier (@elfelip)
    - Gaëtan Daubresse (@Gaetan2907)
'''

EXAMPLES = '''
    - name: Create an authentication flow from first broker login and add an execution to it.
      community.general.keycloak_authentication:
        auth_keycloak_url: http://localhost:8080/auth
        auth_realm: master
        auth_username: admin
        auth_password: password
        realm: master
        alias: "Copy of first broker login"
        copyFrom: "first broker login"
        authenticationExecutions:
          - providerId: "test-execution1"
            requirement: "REQUIRED"
            authenticationConfig:
              alias: "test.execution1.property"
              config:
                test1.property: "value"
          - providerId: "test-execution2"
            requirement: "REQUIRED"
            authenticationConfig:
              alias: "test.execution2.property"
              config:
                test2.property: "value"
        state: present

    - name: Re-create the authentication flow
      community.general.keycloak_authentication:
        auth_keycloak_url: http://localhost:8080/auth
        auth_realm: master
        auth_username: admin
        auth_password: password
        realm: master
        alias: "Copy of first broker login"
        copyFrom: "first broker login"
        authenticationExecutions:
          - providerId: "test-provisioning"
            requirement: "REQUIRED"
            authenticationConfig:
              alias: "test.provisioning.property"
              config:
                test.provisioning.property: "value"
        state: present
        force: true

    - name: Create an authentication flow with subflow containing an execution.
      community.general.keycloak_authentication:
        auth_keycloak_url: http://localhost:8080/auth
        auth_realm: master
        auth_username: admin
        auth_password: password
        realm: master
        alias: "Copy of first broker login"
        copyFrom: "first broker login"
        authenticationExecutions:
          - providerId: "test-execution1"
            requirement: "REQUIRED"
          - displayName: "New Subflow"
            requirement: "REQUIRED"
          - providerId: "auth-cookie"
            requirement: "REQUIRED"
            flowAlias: "New Sublow"
        state: present

    - name: Remove authentication.
      community.general.keycloak_authentication:
        auth_keycloak_url: http://localhost:8080/auth
        auth_realm: master
        auth_username: admin
        auth_password: password
        realm: master
        alias: "Copy of first broker login"
        state: absent
'''

RETURN = '''
flow:
  description: JSON representation for the authentication.
  returned: on success
  type: dict
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak \
    import KeycloakAPI, camel, keycloak_argument_spec, get_token, KeycloakError, is_struct_included
from ansible.module_utils.basic import AnsibleModule


def find_exec_in_executions(searched_exec, executions):
    """
    Search if exec is contained in the executions.
    :param searched_exec: Execution to search for.
    :param executions: List of executions.
    :return: Index of the execution, -1 if not found..
    """
    for i, existing_exec in enumerate(executions, start=0):
        if ("providerId" in existing_exec and "providerId" in searched_exec and
                existing_exec["providerId"] == searched_exec["providerId"] or
                "displayName" in existing_exec and "displayName" in searched_exec and
                existing_exec["displayName"] == searched_exec["displayName"]):
            return i
    return -1


def create_or_update_executions(kc, config, realm='master'):
    """
    Create or update executions for an authentication flow.
    :param kc: Keycloak API access.
    :param config: Representation of the authentication flow including it's executions.
    :param realm: Realm
    :return: tuple (changed, dict(before, after)
        WHERE
        bool changed indicates if changes have been made
        dict(str, str) shows state before and after creation/update
    """
    try:
        changed = False
        after = ""
        before = ""
        if "authenticationExecutions" in config:
            # Get existing executions on the Keycloak server for this alias
            existing_executions = kc.get_executions_representation(config, realm=realm)
            for new_exec_index, new_exec in enumerate(config["authenticationExecutions"], start=0):
                if new_exec["index"] is not None:
                    new_exec_index = new_exec["index"]
                exec_found = False
                # Get flowalias parent if given
                if new_exec["flowAlias"] is not None:
                    flow_alias_parent = new_exec["flowAlias"]
                else:
                    flow_alias_parent = config["alias"]
                # Check if same providerId or displayName name between existing and new execution
                exec_index = find_exec_in_executions(new_exec, existing_executions)
                if exec_index != -1:
                    # Remove key that doesn't need to be compared with existing_exec
                    exclude_key = ["flowAlias"]
                    for index_key, key in enumerate(new_exec, start=0):
                        if new_exec[key] is None:
                            exclude_key.append(key)
                    # Compare the executions to see if it need changes
                    if not is_struct_included(new_exec, existing_executions[exec_index], exclude_key) or exec_index != new_exec_index:
                        exec_found = True
                        before += str(existing_executions[exec_index]) + '\n'
                    id_to_update = existing_executions[exec_index]["id"]
                    # Remove exec from list in case 2 exec with same name
                    existing_executions[exec_index].clear()
                elif new_exec["providerId"] is not None:
                    kc.create_execution(new_exec, flowAlias=flow_alias_parent, realm=realm)
                    exec_found = True
                    exec_index = new_exec_index
                    id_to_update = kc.get_executions_representation(config, realm=realm)[exec_index]["id"]
                    after += str(new_exec) + '\n'
                elif new_exec["displayName"] is not None:
                    kc.create_subflow(new_exec["displayName"], flow_alias_parent, realm=realm)
                    exec_found = True
                    exec_index = new_exec_index
                    id_to_update = kc.get_executions_representation(config, realm=realm)[exec_index]["id"]
                    after += str(new_exec) + '\n'
                if exec_found:
                    changed = True
                    if exec_index != -1:
                        # Update the existing execution
                        updated_exec = {
                            "id": id_to_update
                        }
                        # add the execution configuration
                        if new_exec["authenticationConfig"] is not None:
                            kc.add_authenticationConfig_to_execution(updated_exec["id"], new_exec["authenticationConfig"], realm=realm)
                        for key in new_exec:
                            # remove unwanted key for the next API call
                            if key != "flowAlias" and key != "authenticationConfig":
                                updated_exec[key] = new_exec[key]
                        if new_exec["requirement"] is not None:
                            kc.update_authentication_executions(flow_alias_parent, updated_exec, realm=realm)
                        diff = exec_index - new_exec_index
                        kc.change_execution_priority(updated_exec["id"], diff, realm=realm)
                        after += str(kc.get_executions_representation(config, realm=realm)[new_exec_index]) + '\n'
        return changed, dict(before=before, after=after)
    except Exception as e:
        kc.module.fail_json(msg='Could not create or update executions for authentication flow %s in realm %s: %s'
                            % (config["alias"], realm, str(e)))


def main():
    """
    Module execution
    :return:
    """
    argument_spec = keycloak_argument_spec()
    meta_args = dict(
        realm=dict(type='str', required=True),
        alias=dict(type='str', required=True),
        providerId=dict(type='str'),
        description=dict(type='str'),
        copyFrom=dict(type='str'),
        authenticationExecutions=dict(type='list', elements='dict',
                                      options=dict(
                                          providerId=dict(type='str'),
                                          displayName=dict(type='str'),
                                          requirement=dict(choices=["REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL"], type='str'),
                                          flowAlias=dict(type='str'),
                                          authenticationConfig=dict(type='dict'),
                                          index=dict(type='int'),
                                      )),
        state=dict(choices=["absent", "present"], default='present'),
        force=dict(type='bool', default=False),
    )
    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']])
                           )

    result = dict(changed=False, msg='', flow={})
    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)
    realm = module.params.get('realm')
    state = module.params.get('state')
    force = module.params.get('force')

    new_auth_repr = {
        "alias": module.params.get("alias"),
        "copyFrom": module.params.get("copyFrom"),
        "providerId": module.params.get("providerId"),
        "authenticationExecutions": module.params.get("authenticationExecutions"),
        "description": module.params.get("description"),
        "builtIn": module.params.get("builtIn"),
        "subflow": module.params.get("subflow"),
    }

    auth_repr = kc.get_authentication_flow_by_alias(alias=new_auth_repr["alias"], realm=realm)
    if auth_repr == {}:  # Authentication flow does not exist
        if state == 'present':  # If desired state is present
            result['changed'] = True
            if module._diff:
                result['diff'] = dict(before='', after=new_auth_repr)
            if module.check_mode:
                module.exit_json(**result)
            # If copyFrom is defined, create authentication flow from a copy
            if "copyFrom" in new_auth_repr and new_auth_repr["copyFrom"] is not None:
                auth_repr = kc.copy_auth_flow(config=new_auth_repr, realm=realm)
            else:  # Create an empty authentication flow
                auth_repr = kc.create_empty_auth_flow(config=new_auth_repr, realm=realm)
            # If the authentication still not exist on the server, raise an exception.
            if auth_repr is None:
                result['msg'] = "Authentication just created not found: " + str(new_auth_repr)
                module.fail_json(**result)
            # Configure the executions for the flow
            create_or_update_executions(kc=kc, config=new_auth_repr, realm=realm)
            # Get executions created
            exec_repr = kc.get_executions_representation(config=new_auth_repr, realm=realm)
            if exec_repr is not None:
                auth_repr["authenticationExecutions"] = exec_repr
            result['flow'] = auth_repr
        elif state == 'absent':  # If desired state is absent.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['msg'] = new_auth_repr["alias"] + ' absent'
    else:  # The authentication flow already exist
        if state == 'present':  # if desired state is present
            if force:  # If force option is true
                # Delete the actual authentication flow
                result['changed'] = True
                if module._diff:
                    result['diff'] = dict(before=auth_repr, after=new_auth_repr)
                if module.check_mode:
                    module.exit_json(**result)
                kc.delete_authentication_flow_by_id(id=auth_repr["id"], realm=realm)
                # If copyFrom is defined, create authentication flow from a copy
                if "copyFrom" in new_auth_repr and new_auth_repr["copyFrom"] is not None:
                    auth_repr = kc.copy_auth_flow(config=new_auth_repr, realm=realm)
                else:  # Create an empty authentication flow
                    auth_repr = kc.create_empty_auth_flow(config=new_auth_repr, realm=realm)
                # If the authentication still not exist on the server, raise an exception.
                if auth_repr is None:
                    result['msg'] = "Authentication just created not found: " + str(new_auth_repr)
                    module.fail_json(**result)
            # Configure the executions for the flow
            if module.check_mode:
                module.exit_json(**result)
            changed, diff = create_or_update_executions(kc=kc, config=new_auth_repr, realm=realm)
            result['changed'] |= changed
            if module._diff:
                result['diff'] = diff
            # Get executions created
            exec_repr = kc.get_executions_representation(config=new_auth_repr, realm=realm)
            if exec_repr is not None:
                auth_repr["authenticationExecutions"] = exec_repr
            result['flow'] = auth_repr
        elif state == 'absent':  # If desired state is absent
            result['changed'] = True
            # Delete the authentication flow alias.
            if module._diff:
                result['diff'] = dict(before=auth_repr, after='')
            if module.check_mode:
                module.exit_json(**result)
            kc.delete_authentication_flow_by_id(id=auth_repr["id"], realm=realm)
            result['msg'] = 'Authentication flow: {alias} id: {id} is deleted'.format(alias=new_auth_repr['alias'],
                                                                                      id=auth_repr["id"])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
