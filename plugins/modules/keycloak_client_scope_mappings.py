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


    
def get_all_mappings(kc, cid, existing_clients, realm):
    all_mappings = {}
    for existing_client in existing_clients:
        existing_mappings = kc.get_client_scope_mappings(cid, target_client=existing_client["id"], realm=realm)
        if existing_mappings:
            scope_mappings = [sm.get("name") for sm in existing_mappings]
            all_mappings.update({existing_client["clientId"]: list(sorted(scope_mappings))})
    return all_mappings
    
def update_mappings(kc, cid, before_mappings, desired_mappings, existing_clients, realm):
    # Update scope mappings
    mappings_update_dict = before_mappings | desired_mappings # Forces all keys not in desired_mappings to None
    for client_id, roles in mappings_update_dict.items():
        existing_sm = before_mappings.get(client_id)
        target_id = [c["id"] for c in existing_clients if c["clientId"] == client_id][0]
        if roles:
            for role in roles:
                if not existing_sm or role not in existing_sm:
                    repr = [{"name":role, "description":"", "composite": False, "clientRole": True}]
                    kc.add_client_scope_mapping(cid, target_id, repr, realm=realm)
            for role in existing_sm:
                if role not in roles:
                    repr = [{"name":role, "description":"", "composite": False, "clientRole": True}]
                    kc.delete_client_scope_mapping(cid, target_id, repr, realm=realm)
        else:
            if existing_sm:
                for role in existing_sm:
                    repr = [{"name":role, "description":"", "composite": False, "clientRole": True}]
                    kc.delete_client_scope_mapping(cid, target_id, repr, realm=realm)

def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(default="present", choices=["present"]),
        realm=dict(type="str", default="master"),
        id=dict(type="str"),
        client_id=dict(type="str", aliases=["clientId"]),
        scope_mappings=dict(
            type="list", elements="dict", aliases=["scopeMappings"]
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

    # See if it already exists in Keycloak
    if cid is None:
        before_mappings = kc.get_client_by_clientid(
            module.params.get("client_id"), realm=realm
        )
        if before_mappings is not None:
            cid = before_mappings["id"]
    else:
        before_mappings = kc.get_client_by_id(cid, realm=realm)

    if before_mappings is None:
        before_mappings = {}
        
    # Get all existing scope mappings
    existing_clients = kc.get_clients(realm=realm)
    before_mappings = get_all_mappings(kc, cid, existing_clients, realm=realm)

    # Build a proposed changeset from parameters given to this module
    changeset = dict((k, None) for k in before_mappings)
    
    if module.params.get("scope_mappings"):
        for target_client in module.params.get("scope_mappings"):
            target_id = [client["id"] for client in existing_clients if client["clientId"] == target_client["target_client_id"]][0]
            roles = [r.get("name") for r in target_client["roles"]]
            changeset.update({target_client["target_client_id"]: list(sorted(roles))})
 
    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_mappings = before_mappings.copy()
    desired_mappings.update(changeset)

    result["proposed"] = changeset
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
        update_mappings(kc, cid, before_mappings, desired_mappings, existing_clients, realm=realm)
        after_mappings = get_all_mappings(kc, cid, existing_clients, realm=realm)
        
        
        if before_mappings == after_mappings:
            result["changed"] = False
        if module._diff:
            result["diff"] = dict(
                before=before_mappings, after=after_mappings
            )
        
        result["end_state"] = after_mappings

        result["msg"] = "Mappings for client %s have been updated." % module.params.get("client_id")
        module.exit_json(**result)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
