#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: keycloak_scope_mappings

short_description: Allows administration of Keycloak client scope mappings via Keycloak API


description:
    - This module allows the administration of Keycloak client scope mappings vie the KeyCloak API

options:
    TODO
"""

EXAMPLES = """
    TODO
"""

RETURN = """
TODO
msg:

proposed:

existing:

end_state:

"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    camel,
    keycloak_argument_spec,
    get_token,
    KeycloakError,
)
from ansible.module_utils.basic import AnsibleModule
from copy import deepcopy

    
def get_all_mappings(kc, cid, existing_clients, realm):
    all_mappings = {}
    for existing_client in existing_clients:
        existing_mappings = kc.get_client_scope_mappings(cid, target_client=existing_client["id"], realm=realm)
        if existing_mappings:
            scope_mappings = [sm.get("name") for sm in existing_mappings]
            all_mappings.update({existing_client["clientId"]: list(sorted(scope_mappings))})
    # Also get realm mappings.
    existing_realm_mappings = kc.get_realm_scope_mappings(cid, realm=realm)
    if existing_realm_mappings:
        scope_mappings = [sm.get("name") for sm in existing_realm_mappings]
        all_mappings.update({"realm": scope_mappings})

    return all_mappings
    
def update_mappings(kc, cid, before_mappings, desired_mappings, ids, realm):
    # Update scope mappings
    mappings_update_dict = before_mappings | desired_mappings
    available_mappings = kc.get_available_realm_scope_mappings(cid, realm=realm)
    realm_mappings = kc.get_realm_scope_mappings(cid, realm=realm)
    name_to_id = dict((sm["name"], sm["id"]) for sm in available_mappings + realm_mappings)
    for client_id, roles in mappings_update_dict.items():
        existing_sm = before_mappings.get(client_id)
        target_id = ids[client_id] if client_id != "realm" else None
        if roles:
            for role in roles:
                if not existing_sm or role not in existing_sm:
                    if client_id != "realm":
                        repr = [{"name":role, "description":"", "composite": False, "clientRole": True}]
                        kc.add_client_scope_mapping(cid, target_id, repr, realm=realm)
                    else:
                        repr = [{"id": name_to_id[role]}]
                        kc.add_realm_scope_mapping(cid, repr, realm=realm)
        if existing_sm:
            for role in existing_sm:
                if not roles or role not in roles:
                    if client_id != "realm":
                        repr = [{"name": role, "description": "", "composite": False, "clientRole": True}]
                        kc.delete_client_scope_mapping(cid, target_id, repr, realm=realm)
                    else:
                        repr = [{"id": name_to_id[role]}]
                        kc.delete_realm_scope_mapping(cid, repr, realm=realm)
def delete_proposed_mappings(kc, cid, before_mappings, mappings_to_delete):
    
    new_mappings = deepcopy(before_mappings)
    for client_id, roles in mappings_to_delete.items():
        for role in roles:
            if client_id in new_mappings.keys() and role in new_mappings.get(client_id):
                new_mappings[client_id].remove(role)
    for client_id in before_mappings.keys():
        if not new_mappings.get(client_id):
            new_mappings.pop(client_id)
    return new_mappings
        
def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(default="present", choices=["present", "absent"]),
        realm=dict(type="str", default="master"),
        id=dict(type="str"),
        client_id=dict(type="str", aliases=["clientId"]),
        scope_mappings=dict(
            type="dict", aliases=["scopeMappings"]
        ),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [
                ["id", "client_id"],
                ["token", "auth_realm", "auth_username", "auth_password"],
            ]
        ),
        required_together=([["auth_realm", "auth_username", "auth_password"]]),
    )

    result = dict(
        changed=False, msg="", diff={}, proposed={}, existing={}, end_state={}
    )

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    cid = module.params.get("id")
    state = module.params.get("state")
        
    # Get all existing scope mappings
    existing_clients = kc.get_clients(realm=realm)
    ids = dict((c["clientId"], c["id"]) for c in existing_clients)
    if not cid:
        cid = ids[module.params.get("client_id")]
    before_mappings = get_all_mappings(kc, cid, existing_clients, realm=realm)

    # Build a proposed changeset from parameters given to this module. We sort te roles to avoid a diff that is only a re-ordering
    changeset = module.params.get("scope_mappings")
    if changeset:
        for target_client, roles in changeset.items():
            changeset.update({target_client: list(sorted(roles))})
 
    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_mappings = before_mappings.copy()
    desired_mappings.update(changeset)

    result["proposed"] = desired_mappings
    result["existing"] = before_mappings

    if state == "present":
        # Process an update
        result["changed"] = True

        if module.check_mode:
            # We can only compare the current client with the proposed updates we have
            if module._diff:
                result["diff"] = dict(
                    before=before_mappings, after=dict((k, v) for k, v in desired_mappings.items() if v is not None)
                )
            result["changed"] = before_mappings != desired_mappings

            module.exit_json(**result)
        
        existing_clients = kc.get_clients(realm=realm)
        update_mappings(kc, cid, before_mappings, desired_mappings, ids, realm=realm)
        after_mappings = get_all_mappings(kc, cid, existing_clients, realm=realm)
        
        result["changed"] = before_mappings != after_mappings
        if module._diff:
            result["diff"] = dict(
                before=before_mappings, after=after_mappings
            )
        
        result["end_state"] = after_mappings

        result["msg"] = "Mappings for client %s have been updated." % module.params.get("client_id")
        module.exit_json(**result)
    
    elif state == "absent":
        result['changed'] = True
        proposed_mappings = delete_proposed_mappings(kc, cid, before_mappings, changeset)
        if module._diff:
            result['diff'] = dict(before=before_mappings, after=proposed_mappings)
        if module.check_mode:
            module.exit_json(**result)
        
        for client, roles in changeset.items():
            if client != "realm":
                for role in roles:
                    kc.delete_client_scope_mapping(cid, ids[client], [{"name" : role}], realm=realm)
            else:
                for role in roles:
                    kc.delete_realm_scope_mapping(cid, [{"name" : role}], realm=realm)
        result['msg'] = 'Scope mappings %s removed from client %s.' % (changeset, module.params.get("client_id"))
        
        result["proposed"] = {}

        result["end_state"] = {}
        existing_clients = kc.get_clients(realm=realm)
        mappings_after = get_all_mappings(kc, cid, existing_clients, realm=realm)
        for target_client, roles in mappings_after.items():
            mappings_after.update({target_client: list(sorted(roles))})
        result['end_state'] = mappings_after
        module.exit_json(**result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
