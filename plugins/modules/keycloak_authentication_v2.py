#!/usr/bin/python

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_authentication_v2

short_description: Configure authentication flows in Keycloak in an idempotent and safe manner.
version_added: 12.5.0
description:
  - This module allows the creation, deletion, and modification of Keycloak authentication flows using the Keycloak REST API.
  - Rather than modifying an existing flow in place, the module re-creates the flow using the B(Safe Swap) mechanism described below.
  - B(Safe Swap mechanism) - When an authentication flow needs to be updated, the module never modifies the existing flow in place.
     Instead it follows a multi-step swap procedure to ensure the flow is never left in an intermediate or unsafe state during the update.
     This is especially important when the flow is actively bound to a realm binding, a client override, or as an identity-provider
     login-flow or post-flow, because a partially-updated flow could inadvertently allow unauthorised access.
  - The B(Safe Swap mechanism) is as follows. 1. A new flow is created under a temporary name (the original alias plus a configurable suffix,
     for example C(myflow_tmp_for_swap)).
     2. All executions and their configurations are added to the new temporary flow. 3. If the existing flow is currently bound to a realm or a client,
     all bindings are redirected to the new temporary flow. This ensures continuity and avoids any gap in active authentication coverage.
     4. The old flow is deleted. 5. The temporary flow is renamed to the original alias, restoring the expected name.
  - B(Handling pre-existing temporary swap flows) - If a temporary swap flow already exists (for example, from a previously interrupted run),
     the module can optionally delete it before proceeding. This behaviour is controlled by the O(force_temporary_swap_flow_deletion) option.
     If the option is V(false) and a temporary flow already exists, the module will fail to prevent accidental data loss.
  - B(Idempotency) - If the existing flow already matches the desired configuration, no changes are made.
     The module compares a normalised representation of the existing flow against the desired state before deciding whether to trigger the Safe Swap procedure.
  - A depth of 4 sub-flows is supported.

attributes:
  check_mode:
    support: full
  diff_mode:
    support: full

options:
  realm:
    description:
      - The name of the realm in which the authentication flow resides.
    required: true
    type: str
  alias:
    description:
      - The name of the authentication flow.
    required: true
    type: str
  description:
    description:
      - A human-readable description of the flow.
    type: str
  providerId:
    description:
      - The C(providerId) for the new flow.
    choices: [basic-flow, client-flow]
    type: str
    default: basic-flow
  authenticationExecutions:
    description:
      - The desired execution configuration for the flow.
      - Executions at root level.
    type: list
    elements: dict
    suboptions:
      requirement:
        description:
          - The requirement status of the execution or sub-flow.
        choices: [REQUIRED, ALTERNATIVE, DISABLED, CONDITIONAL]
        type: str
        required: true
      providerId:
        description:
          - The C(providerId) of the execution.
        type: str
      authenticationConfig:
        description:
          - The configuration for the execution.
        type: dict
        suboptions:
          alias:
            description: Name of the execution config.
            type: str
            required: true
          config:
            description: Options for the execution config.
            required: true
            type: dict
      subFlow:
        description:
          - The name of the sub-flow.
        type: str
      subFlowType:
        description:
          - The type of the sub-flow.
        choices: [basic-flow, form-flow]
        default: basic-flow
        type: str
      authenticationExecutions:
        description:
          - The execution configuration for executions within the sub-flow.
          - Executions at sub level 1.
        type: list
        elements: dict
        suboptions:
          requirement:
            description:
              - The requirement status of the execution or sub-flow.
            choices: [REQUIRED, ALTERNATIVE, DISABLED, CONDITIONAL]
            type: str
            required: true
          providerId:
            description:
              - The C(providerId) of the execution.
            type: str
          authenticationConfig:
            description:
              - The configuration for the execution.
            type: dict
            suboptions:
              alias:
                description: Name of the execution config.
                type: str
                required: true
              config:
                description: Options for the execution config.
                required: true
                type: dict
          subFlow:
            description:
              - The name of the sub-flow.
            type: str
          subFlowType:
            description:
              - The type of the sub-flow.
            choices: [basic-flow, form-flow]
            default: basic-flow
            type: str
          authenticationExecutions:
            description:
              - The execution configuration for executions within the sub-flow.
              - Executions at sub level 2.
            type: list
            elements: dict
            suboptions:
              requirement:
                description:
                  - The requirement status of the execution or sub-flow.
                choices: [REQUIRED, ALTERNATIVE, DISABLED, CONDITIONAL]
                type: str
                required: true
              providerId:
                description:
                  - The C(providerId) of the execution.
                type: str
              authenticationConfig:
                description:
                  - The configuration for the execution.
                type: dict
                suboptions:
                  alias:
                    description: Name of the execution config.
                    type: str
                    required: true
                  config:
                    description: Options for the execution config.
                    required: true
                    type: dict
              subFlow:
                description:
                  - The name of the sub-flow.
                type: str
              subFlowType:
                description:
                  - The type of the sub-flow.
                choices: [basic-flow, form-flow]
                default: basic-flow
                type: str
              authenticationExecutions:
                description:
                  - The execution configuration for executions within the sub-flow.
                  - Executions at sub level 3.
                type: list
                elements: dict
                suboptions:
                  requirement:
                    description:
                      - The requirement status of the execution or sub-flow.
                    choices: [REQUIRED, ALTERNATIVE, DISABLED, CONDITIONAL]
                    type: str
                    required: true
                  providerId:
                    description:
                      - The C(providerId) of the execution.
                    type: str
                  authenticationConfig:
                    description:
                      - The configuration for the execution.
                    type: dict
                    suboptions:
                      alias:
                        description: Name of the execution config.
                        type: str
                        required: true
                      config:
                        description: Options for the execution config.
                        required: true
                        type: dict
                  subFlow:
                    description:
                      - The name of the sub-flow.
                    type: str
                  subFlowType:
                    description:
                      - The type of the sub-flow.
                    choices: [basic-flow, form-flow]
                    default: basic-flow
                    type: str
                  authenticationExecutions:
                    description:
                      - The execution configuration for executions within the sub-flow.
                      - Executions at sub level 4 (last sub level).
                    type: list
                    elements: dict
                    suboptions:
                      requirement:
                        description:
                          - The requirement status of the execution or sub-flow.
                        choices: [REQUIRED, ALTERNATIVE, DISABLED, CONDITIONAL]
                        type: str
                        required: true
                      providerId:
                        description:
                          - The C(providerId) of the execution.
                        type: str
                        required: true
                      authenticationConfig:
                        description:
                          - The configuration for the execution.
                        type: dict
                        suboptions:
                          alias:
                            description: Name of the execution config.
                            type: str
                            required: true
                          config:
                            description: Options for the execution config.
                            required: true
                            type: dict
  state:
    description:
      - Whether the authentication flow should exist or not.
    choices: [present, absent]
    default: present
    type: str
  temporary_swap_flow_suffix:
    description:
      - The suffix appended to the alias of the temporary flow created during a Safe Swap update.
      - The temporary flow exists only for the duration of the swap procedure and is renamed to
        the original alias once all bindings have been successfully transferred.
    type: str
    default: _tmp_for_swap
  force_temporary_swap_flow_deletion:
    description:
      - If C(true), any pre-existing temporary swap flow (identified by the original alias plus
        O(temporary_swap_flow_suffix)) is deleted before the Safe Swap procedure begins.
      - Set this to C(false) to cause the module to fail instead of silently removing a
        pre-existing temporary flow, for example to avoid accidental data loss after an
        interrupted run.
    default: true
    type: bool
extends_documentation_fragment:
  - community.general._keycloak
  - community.general._keycloak.actiongroup_keycloak
  - community.general._attributes

author:
  - Thomas Bargetz (@thomasbargetz)
"""

EXAMPLES = r"""
- name: Create or modify the 'My Login Flow'.
  community.general.keycloak_authentication_v2:
    auth_keycloak_url: http://localhost:8080/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: master
    alias: My Login Flow
    authenticationExecutions:
      - providerId: idp-review-profile
        requirement: REQUIRED
        authenticationConfig:
          alias: My Login Flow - review profile config
          config:
            update.profile.on.first.login: "missing"
      - subFlow: My Login Flow - User creation or linking
        requirement: REQUIRED
        authenticationExecutions:
          - providerId: idp-create-user-if-unique
            requirement: ALTERNATIVE
            authenticationConfig:
              alias: My Login Flow - create unique user config
              config:
                require.password.update.after.registration: "true"
          - providerId: auth-cookie
            requirement: REQUIRED
          - subFlow: My Login Flow - Handle Existing Account
            requirement: ALTERNATIVE
            authenticationExecutions:
              - providerId: idp-confirm-link
                requirement: REQUIRED
      - providerId: auth-cookie
        requirement: DISABLED
    state: present

- name: Remove an authentication flow.
  community.general.keycloak_authentication_v2:
    auth_keycloak_url: http://localhost:8080/auth
    auth_realm: master
    auth_username: admin
    auth_password: password
    realm: master
    alias: My Login Flow
    state: absent
"""

RETURN = r"""
end_state:
  description: Representation of the authentication flow after module execution.
  returned: on success
  type: dict
  sample:
    {
      "alias": "My Login Flow",
      "builtIn": false,
      "description": "Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account",
      "id": "bc228863-5887-4297-b898-4d988f8eaa5c",
      "providerId": "basic-flow",
      "topLevel": true,
      "authenticationExecutions": [
        {
          "alias": "review profile config",
          "authenticationConfig": {
            "alias": "review profile config",
            "config": {
              "update.profile.on.first.login": "missing"
            },
            "id": "6f09e4fb-aad4-496a-b873-7fa9779df6d7"
          },
          "configurable": true,
          "displayName": "Review Profile",
          "id": "8f77dab8-2008-416f-989e-88b09ccf0b4c",
          "index": 0,
          "level": 0,
          "providerId": "idp-review-profile",
          "requirement": "REQUIRED",
          "requirementChoices": [
            "REQUIRED",
            "ALTERNATIVE",
            "DISABLED"
          ]
        }
      ]
    }
"""

import copy
import traceback
import typing as t

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._keycloak import (
    KeycloakAPI,
    KeycloakError,
    get_token,
    keycloak_argument_spec,
)


def rename_auth_flow(kc: KeycloakAPI, realm: str, flow_id: str, new_alias: str) -> None:
    """Rename an existing authentication flow to a new alias.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which the flow resides.
    :param flow_id: the ID of the flow to rename.
    :param new_alias: the new alias to assign to the flow.
    """
    auth = kc.get_authentication_flow_by_id(flow_id, realm)
    if auth is not None:
        updated = copy.deepcopy(auth)
        updated["alias"] = new_alias
        # The authenticationExecutions key is not accepted by the update endpoint.
        updated.pop("authenticationExecutions", None)
        kc.update_authentication_flow(flow_id, config=updated, realm=realm)


def append_suffix_to_executions(executions: list, suffix: str) -> None:
    """Recursively append a suffix to all sub-flow and authentication config aliases.

    :param executions: a list of execution dicts to process.
    :param suffix: the suffix string to append.
    """
    for execution in executions:
        if execution.get("authenticationConfig") is not None:
            execution["authenticationConfig"]["alias"] += suffix
        if execution.get("subFlow") is not None:
            execution["subFlow"] += suffix
            if execution.get("authenticationExecutions") is not None:
                append_suffix_to_executions(execution["authenticationExecutions"], suffix)


def append_suffix_to_flow_names(desired_auth: dict, suffix: str) -> None:
    """Append a suffix to the top-level alias and all nested aliases in a flow definition.

    This is used during the Safe Swap procedure to give the temporary flow a distinct name.

    :param desired_auth: the desired authentication flow dict (mutated in place).
    :param suffix: the suffix string to append.
    """
    desired_auth["alias"] += suffix
    append_suffix_to_executions(desired_auth["authenticationExecutions"], suffix)


def remove_suffix_from_flow_names(kc: KeycloakAPI, realm: str, auth: dict, suffix: str) -> None:
    """Remove a previously-added suffix from the top-level flow alias, all sub-flow aliases,
    and all authentication config aliases.

    This is the final step of the Safe Swap procedure, which restores the original alias after
    the temporary flow has been bound and the old flow deleted.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which the flow resides.
    :param auth: the authentication flow dict (mutated in place to reflect the renamed alias).
    :param suffix: the suffix to remove.
    """
    new_alias = auth["alias"].removesuffix(suffix)
    rename_auth_flow(kc, realm, auth["id"], new_alias)
    auth["alias"] = new_alias

    executions = kc.get_executions_representation(config=auth, realm=realm)
    for execution in executions:
        if execution.get("authenticationFlow"):
            new_sub_flow_alias = execution["displayName"].removesuffix(suffix)
            rename_auth_flow(kc, realm, execution["flowId"], new_sub_flow_alias)
        if execution.get("configurable"):
            auth_config = execution.get("authenticationConfig")
            if auth_config is not None:
                auth_config["alias"] = auth_config["alias"].removesuffix(suffix)
                kc.update_authentication_config(
                    configId=auth_config["id"],
                    authenticationConfig=auth_config,
                    realm=realm,
                )


def update_execution_requirement_and_config(
    kc: KeycloakAPI,
    realm: str,
    top_level_auth: dict,
    execution: dict,
    parent_flow_alias: str,
) -> None:
    """Update a newly-created execution to set its requirement and, if present, its configuration.

    Keycloak ignores the requirement value on execution creation and defaults all new executions
    to DISABLED. A subsequent update is therefore required to apply the correct requirement.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which the flow resides.
    :param top_level_auth: the top-level authentication flow dict used to look up executions.
    :param execution: the desired execution dict containing 'requirement' and optionally
                      'authenticationConfig'.
    :param parent_flow_alias: the alias of the flow or sub-flow that owns this execution.
    """
    # The most recently added execution is always last in the list.
    created_exec = kc.get_executions_representation(top_level_auth, realm=realm)[-1]
    exec_update = {
        "id": created_exec["id"],
        "providerId": execution["providerId"],
        "requirement": execution["requirement"],
        "priority": created_exec["priority"],
    }
    kc.update_authentication_executions(
        flowAlias=parent_flow_alias,
        updatedExec=exec_update,
        realm=realm,
    )

    if execution.get("authenticationConfig") is not None:
        kc.add_authenticationConfig_to_execution(
            created_exec["id"],
            execution["authenticationConfig"],
            realm=realm,
        )


def create_executions(
    kc: KeycloakAPI,
    realm: str,
    top_level_auth: dict,
    executions: list,
    parent_flow_alias: str,
) -> None:
    """Recursively create all executions and sub-flows under the given parent flow.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which the flow resides.
    :param top_level_auth: the top-level authentication flow dict, used when querying the
                           current execution list after each creation.
    :param executions: a list of desired execution dicts to create.
    :param parent_flow_alias: the alias of the flow or sub-flow that will own the executions.
    """
    for desired_exec in executions:
        sub_flow = desired_exec["subFlow"]
        sub_flow_type = desired_exec["subFlowType"]
        sub_flow_execs = desired_exec.get("authenticationExecutions")

        # Build the minimal payload accepted by the execution creation endpoint.
        exec_payload = {
            "providerId": desired_exec.get("providerId"),
            "requirement": desired_exec["requirement"],
        }
        if desired_exec.get("authenticationConfig") is not None:
            exec_payload["authenticationConfig"] = desired_exec["authenticationConfig"]

        if sub_flow is not None:
            kc.create_subflow(sub_flow, parent_flow_alias, realm=realm, flowType=sub_flow_type)
            update_execution_requirement_and_config(kc, realm, top_level_auth, exec_payload, parent_flow_alias)
            if sub_flow_execs is not None:
                create_executions(kc, realm, top_level_auth, sub_flow_execs, sub_flow)
        else:
            kc.create_execution(exec_payload, flowAlias=parent_flow_alias, realm=realm)
            update_execution_requirement_and_config(kc, realm, top_level_auth, exec_payload, parent_flow_alias)


def create_empty_flow(kc: KeycloakAPI, realm: str, auth_flow_config: dict) -> dict:
    """Create an empty authentication flow from the given configuration dict.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which to create the flow.
    :param auth_flow_config: the flow configuration dict (must include at least 'alias').
    :returns: the newly-created flow dict as returned by the Keycloak API.
    :raises RuntimeError: if the created flow cannot be retrieved immediately after creation.
    """
    created_auth = kc.create_empty_auth_flow(config=auth_flow_config, realm=realm)
    if created_auth is None:
        raise RuntimeError(f"Could not retrieve the authentication flow that was just created: {auth_flow_config}")

    return created_auth


def desired_auth_to_diff_repr(desired_auth: dict) -> dict:
    """Convert a desired authentication flow dict into the normalized representation used for
    diff comparison.

    :param desired_auth: the desired flow dict as provided by the module parameters.
    :returns: a normalized dict suitable for comparison with 'existing_auth_to_diff_repr'.
    """
    desired_copy = copy.deepcopy(desired_auth)
    desired_copy["topLevel"] = True
    desired_copy["authenticationExecutions"] = desired_executions_to_diff_repr(desired_copy["authenticationExecutions"])
    return desired_copy


def desired_executions_to_diff_repr(desired_executions: list) -> list:
    return desired_executions_to_diff_repr_rec(executions=desired_executions, level=0)


def desired_executions_to_diff_repr_rec(executions: list, level: int) -> list:
    """Recursively flatten and normalize a nested execution list into the same flat structure
    that the Keycloak API returns, so that the two representations can be compared directly.

    :param executions: a list of desired execution dicts (possibly nested).
    :param level: the current nesting depth (0 for top-level executions).
    :returns: a flat list of normalized execution dicts.
    """
    converted: list = []
    for index, execution in enumerate(executions):
        converted.append(execution)
        execution["index"] = index
        execution["priority"] = index
        execution["level"] = level

        if execution.get("authenticationConfig") is None:
            execution.pop("authenticationConfig", None)

        if execution.get("subFlow") is not None:
            execution.pop("providerId", None)
            execution["authenticationFlow"] = True
            if execution.get("authenticationExecutions") is not None:
                converted += desired_executions_to_diff_repr_rec(execution["authenticationExecutions"], level + 1)

        execution.pop("subFlow", None)
        execution.pop("subFlowType", None)
        execution.pop("authenticationExecutions", None)

    return converted


def existing_auth_to_diff_repr(kc: KeycloakAPI, realm: str, existing_auth: dict) -> dict:
    """Build a normalized representation of an existing flow that can be compared with the
    output of 'desired_auth_to_diff_repr'.

    Server-side fields that have no equivalent in the desired state (such as 'id',
    'builtIn', 'requirementChoices', and 'configurable') are stripped so that the
    comparison is not skewed by fields the user cannot control.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm in which the flow resides.
    :param existing_auth: the existing flow dict as returned by the Keycloak API.
    :returns: a normalized dict.
    """
    existing_copy = copy.deepcopy(existing_auth)
    existing_copy.pop("id", None)
    existing_copy.pop("builtIn", None)

    executions = kc.get_executions_representation(config=existing_copy, realm=realm)
    for execution in executions:
        execution.pop("id", None)
        execution.pop("requirementChoices", None)
        execution.pop("configurable", None)
        execution.pop("displayName", None)
        execution.pop("description", None)
        execution.pop("flowId", None)

        if execution.get("authenticationConfig") is not None:
            execution["authenticationConfig"].pop("id", None)
            # The alias is already stored inside the authenticationConfig object; the
            # top-level alias field on the execution is redundant and is removed.
            execution.pop("alias", None)

    existing_copy["authenticationExecutions"] = executions
    # Normalize a missing description to None so that it compares equal to an unset desired value.
    existing_copy["description"] = existing_copy.get("description") or None
    return existing_copy


def is_auth_flow_in_use(kc: KeycloakAPI, realm: str, existing_auth: dict) -> bool:
    """Determine whether the given flow is currently bound to a realm binding, a client
    authentication flow override or as an identity-provider login-flow or post-flow.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm to inspect.
    :param existing_auth: the existing flow dict (must include 'id' and 'alias').
    :returns: True if the flow is bound anywhere, False otherwise.
    """
    flow_id = existing_auth["id"]
    flow_alias = existing_auth["alias"]
    realm_data = kc.get_realm_by_id(realm)
    if realm_data is None:
        raise RuntimeError(f"realm '{realm}' does not exist")

    realm_binding_keys = [
        "browserFlow",
        "registrationFlow",
        "directGrantFlow",
        "resetCredentialsFlow",
        "clientAuthenticationFlow",
        "dockerAuthenticationFlow",
        "firstBrokerLoginFlow",
    ]
    for binding_key in realm_binding_keys:
        if realm_data.get(binding_key) == flow_alias:
            return True

    for client in kc.get_clients(realm=realm):
        overrides = client.get("authenticationFlowBindingOverrides", {})
        if overrides.get("browser") == flow_id:
            return True
        if overrides.get("direct_grant") == flow_id:
            return True

    for identity_provider in kc.get_identity_providers(realm):
        first_broker_login_flow_alias = identity_provider.get("firstBrokerLoginFlowAlias")
        post_broker_login_flow_alias = identity_provider.get("postBrokerLoginFlowAlias")
        if first_broker_login_flow_alias == flow_alias or post_broker_login_flow_alias == flow_alias:
            return True

    return False


def rebind_auth_flow_bindings(
    kc: KeycloakAPI,
    realm: str,
    from_id: str,
    from_alias: str,
    to_id: str,
    to_alias: str,
) -> None:
    """Re-point all realm bindings, client flow overrides and identity-provider login-flows or post-flows
    that reference the source flow to the target flow.

    This is the critical step in the Safe Swap procedure that transfers live bindings from the
    old flow to the newly-created temporary flow without any gap in coverage.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm to update.
    :param from_id: the ID of the flow to rebind away from.
    :param from_alias: the alias of the flow to rebind away from.
    :param to_id: the ID of the flow to rebind to.
    :param to_alias: the alias of the flow to rebind to.
    """
    realm_data = kc.get_realm_by_id(realm)
    if realm_data is None:
        raise RuntimeError(f"realm '{realm}' does not exist")
    realm_changed = False

    realm_binding_keys = [
        "browserFlow",
        "registrationFlow",
        "directGrantFlow",
        "resetCredentialsFlow",
        "clientAuthenticationFlow",
        "dockerAuthenticationFlow",
        "firstBrokerLoginFlow",
    ]
    for binding_key in realm_binding_keys:
        if realm_data.get(binding_key) == from_alias:
            realm_data[binding_key] = to_alias
            realm_changed = True

    if realm_changed:
        kc.update_realm(realm_data, realm)

    for client in kc.get_clients(realm=realm):
        overrides = client.get("authenticationFlowBindingOverrides", {})
        client_changed = False

        if overrides.get("browser") == from_id:
            client["authenticationFlowBindingOverrides"]["browser"] = to_id
            client_changed = True
        if overrides.get("direct_grant") == from_id:
            client["authenticationFlowBindingOverrides"]["direct_grant"] = to_id
            client_changed = True

        if client_changed:
            kc.update_client(id=client["id"], clientrep=client, realm=realm)

    for identity_provider in kc.get_identity_providers(realm):
        first_broker_login_flow_alias = identity_provider.get("firstBrokerLoginFlowAlias")
        post_broker_login_flow_alias = identity_provider.get("postBrokerLoginFlowAlias")
        identity_provider_changed = False

        if first_broker_login_flow_alias == from_alias:
            identity_provider["firstBrokerLoginFlowAlias"] = to_alias
            identity_provider_changed = True

        if post_broker_login_flow_alias == from_alias:
            identity_provider["postBrokerLoginFlowAlias"] = to_alias
            identity_provider_changed = True

        if identity_provider_changed:
            kc.update_identity_provider(idprep=identity_provider, realm=realm)


def delete_tmp_swap_flow_if_exists(
    kc: KeycloakAPI,
    realm: str,
    tmp_swap_alias: str,
    fallback_id: str,
    fallback_alias: str,
) -> None:
    """Delete a pre-existing temporary swap flow, rebinding any of its bindings back to the
    fallback flow first to avoid orphaned bindings.

    :param kc: a KeycloakAPI instance.
    :param realm: the realm to inspect.
    :param tmp_swap_alias: the alias of the temporary swap flow to delete.
    :param fallback_id: the ID of the flow to rebind to before deleting the temporary flow.
    :param fallback_alias: the alias of the flow to rebind to before deleting the temporary flow.
    """
    existing_tmp = kc.get_authentication_flow_by_alias(tmp_swap_alias, realm)
    if existing_tmp is not None and len(existing_tmp) > 0:
        rebind_auth_flow_bindings(
            kc,
            realm,
            from_id=existing_tmp["id"],
            from_alias=existing_tmp["alias"],
            to_id=fallback_id,
            to_alias=fallback_alias,
        )
        kc.delete_authentication_flow_by_id(id=existing_tmp["id"], realm=realm)


def create_authentication_execution_spec_options(depth: int) -> dict[str, t.Any]:
    options: dict[str, t.Any] = dict(
        providerId=dict(type="str", required=depth == 0),
        requirement=dict(type="str", required=True, choices=["REQUIRED", "ALTERNATIVE", "DISABLED", "CONDITIONAL"]),
        authenticationConfig=dict(
            type="dict",
            options=dict(
                alias=dict(type="str", required=True),
                config=dict(type="dict", required=True),
            ),
        ),
    )
    if depth > 0:
        options.update(
            subFlow=dict(type="str"),
            subFlowType=dict(type="str", choices=["basic-flow", "form-flow"], default="basic-flow"),
            authenticationExecutions=dict(
                type="list",
                elements="dict",
                options=create_authentication_execution_spec_options(depth - 1),
            ),
        )
    return options


def validate_executions(kc: KeycloakAPI, realm: str, executions: dict) -> None:
    valid_providers = kc.get_authenticator_providers(realm)
    valid_provider_ids = {provider["id"] for provider in valid_providers}

    invalid_provider_ids = validate_executions_rec(valid_provider_ids, executions)
    if len(invalid_provider_ids) > 0:
        invalid_provider_ids_str = ", ".join(f"'{item}'" for item in invalid_provider_ids)
        raise ValueError(
            f"The following execution providerIds are unknown and therefore invalid: {invalid_provider_ids_str}"
        )


def validate_executions_rec(valid_provider_ids: set, executions: dict) -> list:
    invalid_provider_ids = []
    for execution in executions:
        provider_id = execution["providerId"]
        sub_flow = execution["subFlow"]
        if provider_id is not None:
            if provider_id not in valid_provider_ids:
                invalid_provider_ids.append(provider_id)

        if sub_flow is not None:
            invalid_provider_ids.extend(
                validate_executions_rec(valid_provider_ids, execution["authenticationExecutions"])
            )

    return invalid_provider_ids


def main() -> None:
    """Module entry point."""
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        realm=dict(type="str", required=True),
        alias=dict(type="str", required=True),
        providerId=dict(type="str", choices=["basic-flow", "client-flow"], default="basic-flow"),
        description=dict(type="str"),
        authenticationExecutions=dict(
            type="list",
            elements="dict",
            options=create_authentication_execution_spec_options(4),
        ),
        state=dict(choices=["absent", "present"], default="present"),
        force_temporary_swap_flow_deletion=dict(type="bool", default=True),
        temporary_swap_flow_suffix=dict(type="str", default="_tmp_for_swap"),
    )
    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"]]
        ),
        required_together=([["auth_username", "auth_password"]]),
        required_by={"refresh_token": "auth_realm"},
    )

    result = dict(changed=False, msg="", end_state={})

    # Obtain an access token and initialize the API client.
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    state = module.params.get("state")
    force_swap_deletion = module.params.get("force_temporary_swap_flow_deletion")
    tmp_swap_suffix = module.params.get("temporary_swap_flow_suffix")

    desired_auth = {
        "alias": module.params.get("alias"),
        "providerId": module.params.get("providerId"),
        "authenticationExecutions": module.params.get("authenticationExecutions") or [],
        "description": module.params.get("description") or None,
    }
    desired_auth_diff_repr = desired_auth_to_diff_repr(desired_auth)

    existing_auth = kc.get_authentication_flow_by_alias(alias=desired_auth["alias"], realm=realm)
    existing_auth_diff_repr = None
    if existing_auth:
        existing_auth_diff_repr = existing_auth_to_diff_repr(kc, realm, existing_auth)

    try:
        try:
            validate_executions(kc, realm, desired_auth["authenticationExecutions"])
        except ValueError as e:
            module.fail_json(
                msg=f"Validation of executions failed: {e}",
                exception=traceback.format_exc(),
            )

        if not existing_auth:
            if state == "absent":
                # The flow does not exist and is not required; nothing to do.
                result["diff"] = dict(before="", after="")
                result["changed"] = False
                result["end_state"] = {}
                result["msg"] = f"'{desired_auth['alias']}' is already absent"
                module.exit_json(**result)

            elif state == "present":
                # The flow does not yet exist; create it.
                if module.check_mode:
                    result["changed"] = True
                    result["diff"] = dict(before="", after=desired_auth_diff_repr)
                    module.exit_json(**result)

                created_auth = create_empty_flow(kc, realm, desired_auth)
                result["changed"] = True

                create_executions(
                    kc=kc,
                    realm=realm,
                    top_level_auth=created_auth,
                    executions=desired_auth["authenticationExecutions"],
                    parent_flow_alias=desired_auth["alias"],
                )

                exec_repr = kc.get_executions_representation(config=desired_auth, realm=realm)
                if exec_repr is not None:
                    created_auth["authenticationExecutions"] = exec_repr

                result["diff"] = dict(before="", after=created_auth)
                result["end_state"] = created_auth
                result["msg"] = f"Authentication flow '{created_auth['alias']}' with id: '{created_auth['id']}' created"

        else:
            is_flow_in_use = is_auth_flow_in_use(kc, realm, existing_auth)

            if state == "present":
                change_required = existing_auth_diff_repr != desired_auth_diff_repr
                if change_required:
                    result["diff"] = dict(before=existing_auth_diff_repr, after=desired_auth_diff_repr)

                if module.check_mode:
                    result["changed"] = change_required
                    module.exit_json(**result)

                if not change_required:
                    # The existing flow already matches the desired state; nothing to do.
                    result["end_state"] = existing_auth_diff_repr
                    module.exit_json(**result)

                # The flow needs to be updated. Rather than modifying the existing flow in place,
                # the Safe Swap procedure is used to guarantee that the flow is never left in an
                # unsafe intermediate state. See the module documentation for a full description.
                if is_flow_in_use:
                    tmp_swap_alias = desired_auth["alias"] + tmp_swap_suffix

                    if force_swap_deletion:
                        # Remove any leftover temporary flow from a previous interrupted run,
                        # rebinding its bindings back to the current flow first.
                        delete_tmp_swap_flow_if_exists(
                            kc=kc,
                            realm=realm,
                            tmp_swap_alias=tmp_swap_alias,
                            fallback_id=existing_auth["id"],
                            fallback_alias=existing_auth["alias"],
                        )

                    # Build the new flow under a temporary name so that both flows coexist
                    # during the swap.
                    append_suffix_to_flow_names(desired_auth, tmp_swap_suffix)
                else:
                    # The flow is not bound anywhere; it is safe to delete it immediately and
                    # recreate it under the original name.
                    kc.delete_authentication_flow_by_id(existing_auth["id"], realm=realm)

                created_auth = create_empty_flow(kc, realm, desired_auth)
                result["changed"] = True
                create_executions(
                    kc=kc,
                    realm=realm,
                    top_level_auth=created_auth,
                    executions=desired_auth["authenticationExecutions"],
                    parent_flow_alias=desired_auth["alias"],
                )

                if is_flow_in_use:
                    # Transfer all bindings from the old flow to the new temporary flow, then
                    # delete the old flow and strip the temporary suffix from all aliases.
                    rebind_auth_flow_bindings(
                        kc=kc,
                        realm=realm,
                        from_id=existing_auth["id"],
                        from_alias=existing_auth["alias"],
                        to_id=created_auth["id"],
                        to_alias=created_auth["alias"],
                    )
                    kc.delete_authentication_flow_by_id(existing_auth["id"], realm=realm)
                    remove_suffix_from_flow_names(kc, realm, created_auth, tmp_swap_suffix)

                created_auth_diff_repr = existing_auth_to_diff_repr(kc, realm, created_auth)
                result["diff"] = dict(before=existing_auth_diff_repr, after=created_auth_diff_repr)
                result["end_state"] = created_auth_diff_repr
                result["msg"] = f"Authentication flow: {created_auth['alias']} id: {created_auth['id']} updated"

            else:
                if is_flow_in_use:
                    module.fail_json(
                        msg=f"Flow {existing_auth['alias']} with id {existing_auth['id']} is in use and therefore cannot be deleted in realm {realm}"
                    )

                result["diff"] = dict(before=existing_auth_diff_repr, after="")
                if module.check_mode:
                    result["changed"] = True
                    module.exit_json(**result)

                kc.delete_authentication_flow_by_id(id=existing_auth["id"], realm=realm)
                result["changed"] = True
                result["msg"] = f"Authentication flow: {desired_auth['alias']} id: {existing_auth['id']} is deleted"
    except Exception as e:
        module.fail_json(
            msg=f"An unexpected error occurred: {e}",
            exception=traceback.format_exc(),
        )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
