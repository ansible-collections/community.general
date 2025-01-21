#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2019, INSPQ <philippe.gauthier@inspq.qc.ca>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import copy
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak \
    import KeycloakAPI, keycloak_argument_spec, get_token, KeycloakError, is_struct_included
from ansible.module_utils.basic import AnsibleModule

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

def hasSameName(new_exec, other_exec):
    for i in ["providerId", "displayName"]:
        if i in new_exec and i in other_exec:
            return new_exec[i] == other_exec[i]


def find_exec_in_executions(searched_exec, executions, excluded_ids = []):
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
    return exec1.get("authenticationConfig") is None or exec2.get("authenticationConfig") is None or\
            exec1["authenticationConfig"]["alias"] == exec2["authenticationConfig"]["alias"]


def get_by_keys(d: dict, ks: list):
    for k in ks:
        v = d.get(k)
        if v is not None:
            return k, v
    return None, None


def get_recursively(d: dict, ks: list):
    for k in ks:
        d = d.get(k)
        if d is None:
            return None
    return d


def get_identifier(execution):
    # For executions, Keycloak returns the providerId as displayName
    _, eid = get_by_keys(execution, ["displayName", "providerId"])
    if eid is None:
        raise Exception(
            "Could not find a name for execution {}".format(execution))

    alias = execution.get("alias")
    if alias is not None:
        eid = "{} ({})".format(eid, alias)

    return eid


def is_flow(execution):
    has_dn = execution.get("displayName") is not None
    no_pid = execution.get("providerId") is None
    return has_dn and no_pid


def validate_execution(execution):
    eids = ["providerId", "displayName"]
    _, eid = get_by_keys(execution, eids)
    if eid is None:
        raise Exception(
            "Execution: %s, has no identifier (among %s)" % (execution, eids))


def expand_execution(execution):
    if not is_flow(execution):
        execution["alias"] = get_recursively(
            execution, ["authenticationConfig", "alias"])


def create_authentication_execution(
        kc, config, new_exec, flow_alias_parent, realm='master'):
    # Add authentication execution (or subflow) and returns its id
    # (given by keycloak)
    response = None
    if is_flow(new_exec):
        response = kc.create_subflow(
            new_exec["displayName"], flow_alias_parent, realm=realm)
    else:
        updated_exec = {}
        for key in new_exec:
            if not key in ["flowAlias", "authenticationConfig"]:
                updated_exec[key] = new_exec[key]
        response = kc.create_execution(
            updated_exec, flowAlias=flow_alias_parent, realm=realm)

    exec_type = ("subflow" if is_flow(new_exec) else "execution")

    # https://datatracker.ietf.org/doc/html/rfc2616#section-14.30
    if response is None or not 'Location' in response.headers:
        raise Exception("No ID returned when creating %s" % exec_type)
    creation_id = response.headers['Location'].split('/')[-1]

    existing_execs = kc.get_executions_representation(config, realm=realm)
    # The ID returned in the response is the "flowId" for flows, we also want
    # the id
    created_exec = None
    id_key = "id"
    if is_flow(new_exec):
        new_exec["flowId"] = creation_id
        id_key = "flowId"
    created_list = [e for e in existing_execs if e.get(id_key) == creation_id]
    if len(created_list) == 0:
        raise Exception(
            "could not find newly created {} with {} '{}'".format(
                exec_type, id_key, creation_id))
    elif len(created_list) > 1:
        raise Exception(
            "multiple {}s with {} '{}': {}" % (
                exec_type, id_key, creation_id, created_list))
    created_exec = created_list[0]
    new_exec["id"] = created_exec["id"]

    return created_exec, existing_execs


def update_authentication_execution(kc, flow_alias_parent, new_exec, check_mode, realm):
    updated_exec = {}
    for key in new_exec:
        # Prepare updated execution. Configuration has been updated already.
        if key != "flowAlias" and key != "authenticationConfig":
            updated_exec[key] = new_exec[key]
    if not check_mode:
        kc.update_authentication_executions(flow_alias_parent, updated_exec, realm=realm)


def add_error_line(
        err_msg_lines, err_msg, flow, exec_name,
        subflow=None, expected=None, actual=None):
    exec_id_template = \
        "Flow {flow}{subflow}, Execution: {exec_name}: {err_msg}"
    err_msg_full = exec_id_template.format(
        flow=flow,
        subflow=", subflow " + subflow if subflow is not None else "",
        err_msg=err_msg.capitalize(),
        exec_name=exec_name)
    if expected is not None or actual is not None:
        exec_diff_template = " (Expected: {expected}, Actual: {actual})"
        err_msg_full += exec_diff_template.format(
            expected=str(expected) if expected is not None else "",
            actual=str(actual) if actual is not None else "")
    err_msg_lines["lines"] += [err_msg_full]


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


def correct_execution_index(kc, realm, existing_execs, new_exec):
    """
    Shifts the execution matching new_exec on the server side to match the
    new_exec's index and applies the server side modifications on the local
    objects

    :param kc: keycloak instance to use for server side modifications
    :param realm: realm on which modifications are applied
    :param existing_execs: current state of the server side executions
        (as returned by kc.get_executions_representation). Is modified to
        reflect server side changes
    :param new_exec: expected execution configuration
    """
    current_exec = [e for e in existing_execs if e["id"] == new_exec["id"]][0]
    shift = current_exec["index"] - new_exec["index"]
    if shift == 0:
        return existing_execs

    kc.change_execution_priority(new_exec["id"], shift, realm=realm)
    # Align the local representation with the server side changes
    for e in existing_execs:
        if e["level"] == new_exec["level"] and \
                e["index"] >= new_exec["index"] and \
                e["index"] < current_exec["index"]:
            e["index"] += 1
    current_exec["index"] = new_exec["index"]


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
            for e in new_executions:
                validate_execution(e)
                expand_execution(e)

            # Compute subflows/executions levels
            levels = {}
            for execution in new_executions:
                flow_alias = execution.get("flowAlias")
                if flow_alias is None:
                    level = 0
                else:
                    level = levels[flow_alias] + 1
                levels.update({get_identifier(execution) : level})
                execution["level"] = level

            # Remove extra executions if any. Iterate backwards so we don't stumble upon concurrency issues
            # when deleting subflows
            new_executions_copy = copy.deepcopy(new_executions)
            deleted_subflow_aliases = []
            for existing_exec in existing_executions[::-1]:
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

            # Update existing executions after deletion
            if changed:
                existing_executions = kc.get_executions_representation(config, realm=realm)

            # Keep track of ids of execution we handled already to account for duplicates
            changed_executions_ids = []

            levels_indices = []
            current_level = 0

            for new_exec in new_executions:
                flow_alias_parent = new_exec.get("flowAlias")
                if flow_alias_parent is None:
                    flow_alias_parent = config["alias"]

                # Update current level and index (levels_indices is a sort of stack)
                # All of this is due to Keycloak storing indices relatively to the start
                # of each SUBflow: indices go back to 0 when entering a new subflow e.g.
                # 0|1|
                # ---
                # 0|-|
                # -|0|
                # -|1|
                # 1|-|
                # -|0|
                previous_level = current_level
                current_level = new_exec["level"]
                if current_level == len(levels_indices):
                    # New level add an index for it
                    levels_indices.append(0)
                elif current_level > previous_level:
                    # Entered a subflow, reset level counter
                    levels_indices[current_level] = 0
                else:
                    levels_indices[current_level] += 1
                new_exec["index"] = levels_indices[current_level]

                # Check if there exists an execution with same name/providerID, at the same level as new execution
                exec_index = find_exec_in_executions(new_exec, existing_executions, changed_executions_ids)
                if exec_index != -1:
                    # There exists an execution of same name/providerID at same level.
                    existing_exec = existing_executions[exec_index]
                    new_exec["id"] = existing_exec["id"]

                    # Remove keys that have special comparison/update API calls
                    exclude_key = ["authenticationConfig", "flowAlias", "index"]

                    # Skip values that are None
                    exclude_key += [
                        k for k, v in new_exec.items() if v is None]

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
                    new_auth_conf = new_exec.get("authenticationConfig")
                    if new_auth_conf is not None:
                        # If the existing execution has no config, or a config with a different alias, then the config has changed
                        config_changed = "authenticationConfig" not in existing_exec or \
                            new_auth_conf["alias"] != existing_exec["authenticationConfig"]["alias"]

                        # Check all keys of the config
                        new_auth_conf_base = new_auth_conf.get("config")
                        if not config_changed and new_auth_conf_base is not None:
                            for k, v in new_auth_conf_base.items():
                                config_changed |= v is not None and\
                                    v != existing_exec["authenticationConfig"]["config"].get(k)
                        if config_changed:
                            if not check_mode:
                                kc.add_authenticationConfig_to_execution(new_exec["id"], new_exec["authenticationConfig"], realm=realm)
                            changed = True
                            add_error_line(err_msg_lines=err_msg, err_msg= "wrong config", flow = config["alias"],
                                exec_name = get_identifier(new_exec), \
                                expected = str(new_auth_conf), actual = str(existing_exec["authenticationConfig"] if "authenticationConfig" in existing_exec else None))

                    # Check if there has been some reordering
                    if new_exec["index"] != existing_exec["index"]:
                        changed = True
                        add_error_line(err_msg_lines=err_msg, err_msg="wrong index", flow=config["alias"],
                            exec_name=get_identifier(new_exec), expected=new_exec["index"],
                            actual=existing_exec["index"])
                        if not check_mode:
                            correct_execution_index(
                                kc, realm, existing_executions, new_exec)
                else:
                    if not check_mode:
                        created_execution, existing_executions = \
                            create_authentication_execution(
                                kc, config, new_exec, flow_alias_parent,
                                realm)
                        # We must update the execution after its creation
                        # in case KeyCloak did not set everything properly
                        # (This happens for example when the user doesn't
                        # specify the requirementChoice field explicitly)
                        update_authentication_execution(
                            kc, flow_alias_parent, new_exec, check_mode,
                            realm)

                        # Keycloak creates new executions with the lowest
                        # priority
                        if not new_flow:
                            # If the main flow is new, we don't have to
                            # push executions up.
                            correct_execution_index(
                                kc, realm, existing_executions, new_exec)

                        auth_conf = new_exec.get("authenticationConfig")
                        if auth_conf is not None:
                            kc.add_authenticationConfig_to_execution(
                                new_exec["id"],
                                auth_conf,
                                realm=realm)
                            # We need to update the execution as the alias is
                            # used for comparisons
                            created_execution["authenticationConfig"] = \
                                auth_conf
                            expand_execution(created_execution)

                    add_error_line(err_msg_lines=err_msg,
                                   err_msg="missing execution",
                                   flow=config["alias"],
                                   exec_name=get_identifier(new_exec))
                    changed = True
                    after["executions"][create_diff_key(new_exec)] = remove_keys_for_diff(new_exec)
            if new_exec.get("id") is not None:
                changed_executions_ids.append(new_exec["id"])
        # TODO fix the diff sorting to order based on the configuration order
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
                                          description=dict(type='str')
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

            # If the authentication still does not exist on the server, raise an exception.
            if auth_repr is None:
                result['msg'] = "Authentication flow just created not found: " + str(new_auth_repr)
                module.fail_json(**result)

            # Configure the executions for the flow
            create_or_update_executions(kc=kc, config=new_auth_repr, check_mode=module.check_mode or module.params["check"], new_flow=True, realm=realm)

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
