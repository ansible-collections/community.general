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
    import KeycloakAPI, camel, keycloak_argument_spec, get_token, KeycloakError, is_struct_included
from ansible.module_utils.basic import AnsibleModule
import copy

def find_exec_in_executions(searched_exec, executions, excluded_ids):
    """
    Search if exec is contained in the executions.
    :param searched_exec: Execution to search for.
    :param executions: List of executions.
    :return: Index of the execution, -1 if not found..
    """
    for i, existing_exec in enumerate(executions, start=0):
        if hasSameName(searched_exec, existing_exec) and\
                existing_exec["level"] == searched_exec["level"] and\
                compare_config_aliases(existing_exec, searched_exec) and\
                existing_exec.get("id") not in excluded_ids:
            return i
    return -1

def compare_config_aliases(exec1, exec2):
    return "authenticationConfig" not in exec1 or "authenticationConfig" not in exec2 or\
            exec1["authenticationConfig"]["alias"] == exec2["authenticationConfig"]["alias"]    

def get_identifier(execution):
    if execution.get("providerId") and not execution.get("displayName"):
        return execution["providerId"]
    elif execution.get("displayName"):
        return execution["displayName"]
    else:
        raise Exception("could not find any name for execution {exec}".format(execution))

def create_authentication_execution(kc, config, new_exec, flow_alias_parent, isFlow, realm='master'):

    updated_exec = {}

    # Add authentication execution (or subflow) and returns its id (given by keycloak)
    if isFlow:
        kc.create_subflow(new_exec["displayName"], flow_alias_parent, realm=realm)
    else:
        for key in new_exec: 
            if key != "flowAlias" and key != "authenticationConfig":
                updated_exec[key] = new_exec[key]
        kc.create_execution(updated_exec, flowAlias=flow_alias_parent, realm=realm)

def hasSameName(new_exec, other_exec):
    if "providerId" in other_exec and "providerId" in new_exec:
        return other_exec["providerId"] == new_exec["providerId"]
    elif "displayName" in other_exec and "displayName" in new_exec:
        return other_exec["displayName"] == new_exec["displayName"]

def update_authentication_execution(kc, flow_alias_parent, new_exec, check_mode, realm):
    updated_exec = {}
    for key in new_exec:
        # Prepare updated execution. Configuration has been updated already.
        if key != "flowAlias" and key != "authenticationConfig":
            updated_exec[key] = new_exec[key]
    if not check_mode:
        kc.update_authentication_executions(flow_alias_parent, updated_exec, realm=realm)


def add_error_line(err_msg_lines, err_msg, flow, exec_name, subflow = None, expected = None, actual = None):
    err_msg_lines["lines"] += ["Flow {flow}{subflow}, Execution: {exec_name}: {err_msg}{expected}{actual}.".format(\
                        flow=flow, subflow=", subflow " + subflow if subflow is not None else "", err_msg=err_msg.capitalize(),\
                        exec_name=exec_name, \
                        expected=" (Expected : " + str(expected) if expected is not None else "",\
                        actual=", Actual : " + str(actual) if actual is not None else "")]

def create_diff_key(execution):
    return "{subflow}{ex_id}".format(subflow=(execution["flowAlias"] + " / ") if execution.get("flowAlias") else "",\
            ex_id=get_identifier(execution))

def remove_keys_for_diff(ex):
    ex_copy = copy.deepcopy(ex)
    ex_for_diff = dict((k, ex_copy[k]) for k in ex_copy if ex_copy[k] and k != "flowAlias")
    return ex_for_diff   


def add_diff_entry(new_exec, old_exec, before, after):
    # Create a "before" execution and an "after" execution. In order to make the diff useful in check_mode, the keys that are not specified in the "after"
    # execution (e.g. an ID) have values taken directly from the "before" execution.
    # If we do not do that, diff mode would tell you that some key/value pairs (e.g. {'id':'some_id') has been deleted, whereas it was
    # simply not given yet.
    exec_key = create_diff_key(new_exec if new_exec != {} else old_exec)
    old_ex_for_diff = remove_keys_for_diff(old_exec)
    new_ex_for_diff = remove_keys_for_diff(new_exec)
    before["executions"][exec_key] = old_ex_for_diff
    after["executions"][exec_key] = old_ex_for_diff | new_ex_for_diff
    if after["executions"][exec_key].get("authenticationConfig") and before["executions"][exec_key].get("authenticationConfig"):
        after["executions"][exec_key]["authenticationConfig"] = before["executions"][exec_key]["authenticationConfig"] | after["executions"][exec_key]["authenticationConfig"]


def create_or_update_executions(kc, config, check_mode, new_flow=False, realm='master'):
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
        after = {"executions":{}}
        before = {"executions":{}}
        err_msg = {"lines":[]}
        if "authenticationExecutions" in config:
            # Get existing executions on the Keycloak server for this alias
            existing_executions = kc.get_executions_representation(config, realm=realm)
            new_executions = config["authenticationExecutions"] if config["authenticationExecutions"] is not None else []
            level_indices = []
            current_level = -1
            # Construct levels reference 
            levels = {}
            for execution in new_executions:
                if execution.get("flowAlias") is None:
                    level = 0
                else:
                    level = levels[execution["flowAlias"]] + 1
                levels.update({get_identifier(execution) : level})
                execution["level"] = level

            # Keep track of ids of execution we handled already to account for dupplicates
            changed_executions_ids = []

            # Remove extra executions if any. Iterate backwards so we don't stumble upon concurrency issues
            # when deleting subflows
            new_executions_copy = copy.deepcopy(new_executions)
            deleted_subflow_aliases = []
            existing_exec_index = len(existing_executions) - 1
            while existing_exec_index >= 0:
                existing_exec = existing_executions[existing_exec_index]
                found_index = find_exec_in_executions(existing_exec, new_executions_copy, [])
                if found_index == -1:
                    changed = True
                    before["executions"][create_diff_key(existing_exec)] = remove_keys_for_diff(existing_exec)
                    add_error_line(err_msg_lines=err_msg, err_msg="extra execution", flow=config["alias"],\
                        exec_name=get_identifier(existing_exec)) 
                    if not check_mode:
                        kc.delete_authentication_execution(existing_exec["id"], realm=realm)
                else:
                    new_executions_copy[found_index].clear()
                existing_exec_index -= 1

            # Update existing executions after deletion
            if changed:
                existing_executions = kc.get_executions_representation(config, realm=realm)

            for new_exec_index, new_exec in enumerate(new_executions):

                if new_exec.get("flowAlias") is not None:
                    flow_alias_parent = new_exec["flowAlias"]
                else:
                    flow_alias_parent = config["alias"]

                # Update current level and index (level_indices is a sort of stack)
                # All of this is due to Keycloak storing indices relatively to the start
                # of each SUBflow: indices go back to 0 when entering a new subflow
                if new_exec["level"] >= len(level_indices):
                    level_indices.append(0)
                    current_level = new_exec["level"]
                elif new_exec["level"] < current_level:
                    current_level = new_exec["level"]
                    for i in range(current_level + 1, len(level_indices)):
                        level_indices[i] = 0
                    level_indices[current_level] += 1
                elif new_exec["level"] > current_level:
                    current_level = new_exec["level"]
                    level_indices[current_level] = 0
                else:
                    level_indices[current_level] += 1

                new_exec["index"] = level_indices[current_level]

                # Check if there exists an execution with same name/providerID, at the same level as new execution
                exec_index = find_exec_in_executions(new_exec, existing_executions, changed_executions_ids)
                if exec_index != -1:
                    # There exists an execution of same name/providerID at same level.
                    existing_exec = existing_executions[exec_index]
                    new_exec["id"] = existing_exec["id"]
                    
                    # Remove keys that have special comparison/update API calls
                    exclude_key = ["authenticationConfig", "flowAlias", "index"]
                    for index_key, key in enumerate(new_exec, start=0):
                        if new_exec[key] is None:
                            exclude_key.append(key)

                    exec_need_changes = not is_struct_included(new_exec, existing_exec, exclude_key)
                    
                    # Update execution
                    if exec_need_changes:
                        changed = True
                        update_authentication_execution(kc, flow_alias_parent, new_exec, check_mode, realm)
                        if new_exec["requirement"] != existing_exec["requirement"]:
                            add_error_line(err_msg_lines=err_msg, err_msg="wrong requirement", flow=config["alias"], exec_name=get_identifier(new_exec),\
                            expected = new_exec["requirement"], actual = existing_exec["requirement"])
                    add_diff_entry(new_exec, existing_exec, before, after)
                    
                    # Determine if config is different
                    config_changed = False
                    if new_exec.get("authenticationConfig") is not None:
                        # If the existing execution has no config, or a config with a different alias, then the config has changed
                        config_changed = "authenticationConfig" not in existing_exec or \
                            new_exec["authenticationConfig"]["alias"] != existing_exec["authenticationConfig"]["alias"] 

                        # Check all keys of the config
                        if not config_changed and new_exec["authenticationConfig"].get("config"):
                            for key in new_exec["authenticationConfig"]["config"]:
                                config_changed |= new_exec["authenticationConfig"]["config"][key] is not None and\
                                    new_exec["authenticationConfig"]["config"][key] != existing_exec["authenticationConfig"]["config"].get(key)
                        if config_changed:
                            if not check_mode:
                                kc.add_authenticationConfig_to_execution(new_exec["id"], new_exec["authenticationConfig"], realm=realm)
                            changed = True
                            add_error_line(err_msg_lines=err_msg, err_msg= "wrong config", flow = config["alias"], exec_name=get_identifier(new_exec), \
                                expected = str(new_exec["authenticationConfig"]), actual = str(existing_exec["authenticationConfig"] if "authenticationConfig" in existing_exec else None))
                    
                    # Check if there has been some reordering
                    if new_exec["index"] != existing_exec["index"]:
                        changed = True
                        shift = existing_exec["index"] - new_exec["index"]
                        if not check_mode:
                            kc.change_execution_priority(new_exec["id"], shift, realm=realm)
                            existing_executions = kc.get_executions_representation(config, realm=realm)
                        add_error_line(err_msg_lines=err_msg, err_msg="wrong index", flow=config["alias"], exec_name=get_identifier(new_exec),\
                        expected=new_exec["index"], actual= existing_exec["index"])
                else :
                    # Create new execution
                    if new_exec.get("providerId") is not None or new_exec.get("displayName") is not None :
                        isFlow = new_exec.get("displayName") is not None and new_exec.get("providerId") is None
                        if not check_mode:
                            create_authentication_execution(kc, config, new_exec, flow_alias_parent, isFlow, realm)
                            existing_executions = kc.get_executions_representation(config, realm=realm)
                            created_list = [execution for execution in existing_executions if hasSameName(new_exec, execution) and\
                                execution["id"] not in changed_executions_ids]
                            if len(created_list) != 1:
                                raise Exception("could not find newly created execution")
                            created = created_list[0]
                            new_exec["id"] = created["id"]
                            # We must update the execution after its creation in case KeyCloak did not set everything properly
                            # (This happens for example when the user doesn't specify the requirementChoice field explicitly)
                            update_authentication_execution(kc, flow_alias_parent, new_exec, check_mode, realm)
                            
                            # Keycloak creates new executions with the lowest priority
                            if not new_flow: # If the flow is new, we don't have to push executions up.
                                shift = created["index"] - level_indices[current_level]
                                if shift != 0:
                                    kc.change_execution_priority(new_exec["id"], shift, realm=realm)
                            if new_exec.get("authenticationConfig") is not None:
                                kc.add_authenticationConfig_to_execution(new_exec["id"], new_exec["authenticationConfig"], realm=realm)
                        add_error_line(err_msg_lines=err_msg, err_msg="missing execution", flow=config["alias"],\
                            exec_name=get_identifier(new_exec))
                        changed = True
                        after["executions"][create_diff_key(new_exec)] = remove_keys_for_diff(new_exec)
                if new_exec.get("id") is not None:
                    changed_executions_ids.append(new_exec["id"])
        for time in [before, after]:
            if time.get("executions") is not None:
                time["executions"] = dict(sorted(time["executions"].items()))
        return changed, dict(before=before, after=after), err_msg

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
        check=dict(type='bool'),
        authenticationExecutions=dict(type='list', elements='dict',
                                      options=dict(
                                          providerId=dict(type='str'),
                                          displayName=dict(type='str'),
                                          requirement=dict(choices=["REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL"], type='str'),
                                          flowAlias=dict(type='str'),
                                          authenticationConfig=dict(type='dict'),
                                          index=dict(type='int'),
                                      )),
        state=dict(choices=["absent", "present", "exact"], default='present'),
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

    # Cater for when it doesn't exist (an empty dict)
    if not auth_repr:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = new_auth_repr["alias"] + ' absent'
            module.exit_json(**result)

        elif state == 'present':
            # Process a creation
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before='', after=new_auth_repr)

            if module.check_mode:
                result['msg'] = "Flow {} was created.".format(new_auth_repr.get("alias"))
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
            create_or_update_executions(kc=kc, config=new_auth_repr, check_mode=module.check_mode or module.params["check"], new_flow= True, realm=realm)

            # Get executions created
            exec_repr = kc.get_executions_representation(config=new_auth_repr, realm=realm)
            if exec_repr is not None:
                auth_repr["authenticationExecutions"] = exec_repr
            result['end_state'] = auth_repr
            result['msg'] = "Flow {} was created.".format(auth_repr.get("alias"))

    else:
        if state == 'present':
            # Process an update

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
            changed, diff, err_msg = create_or_update_executions(kc=kc, config=new_auth_repr, \
                check_mode=module.check_mode or module.params["check"], new_flow= False, realm=realm)
            result['changed'] |= changed

            if module._diff:
                result['diff'] = diff

            # Get executions created
            exec_repr = kc.get_executions_representation(config=new_auth_repr, realm=realm)
            if exec_repr is not None:
                auth_repr["authenticationExecutions"] = exec_repr
            result['end_state'] = auth_repr
            result['msg'] = err_msg["lines"]

        else:
            # Process a deletion (because state was not 'present')
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=auth_repr, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            kc.delete_authentication_flow_by_id(id=auth_repr["id"], realm=realm)

            result['msg'] = 'Authentication flow: {alias} id: {id} is deleted'.format(alias=new_auth_repr['alias'],
                                                                                      id=auth_repr["id"])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
