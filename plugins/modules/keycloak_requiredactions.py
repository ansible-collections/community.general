#!/usr/bin/python

# Copyright: (c) 2023, Claire Lefrancq
from __future__ import absolute_import, division, print_function
import json
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    keycloak_argument_spec,
    get_token,
    KeycloakError,
)
from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

DOCUMENTATION = r"""
---
module: keycloak_requiredactions

short_description: Configure required actions in Keycloak

description: This module can create, update and delete a required action.

options:
    realm:
        description:
            - The name of the realm in which the required action is
        required: true
        type: str
    alias:
        description:
            - Alias for the required action
        required: true
        type: str
    config:
        description:
            - Configuration of the required action
        type: dict
    default_action:
        description:
            - Set the required action as a default action
        type: boolean
    enabled:
        description:
            - Enable the required action
        type: boolean
    name:
        description:
            - Name of the required action
        type: str
    priority:
        description:
            - Priority of the required action
        type: int
    provider_id:
        description:
            - providerId for the new required action
        type: str
    state:
        description:
            - Control if the required action must exists or not.
        choices: [ "present", "absent" ]
        default: present
        type: str
extends_documentation_fragment:
- community.general.keycloak


author:
    - Claire Lefrancq (@clefrancq)
"""

EXAMPLES = r"""
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
"""


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = {
        "state": {"type": "str", "default": "present",
                  "choices": ["present", "absent"]},
        "id": {"type": "str"},
        "realm": {"type": "str"},
        "alias": {"type": "str"},
        "config": {"type": "dict"},
        "default_action": {"type": "bool", "aliases": ["defaultAction"]},
        "enabled": {"type": "bool"},
        "name": {"type": "str"},
        "priority": {"type": "int"},
        "provider_id": {"type": "str", "aliases": ["providerId"]},
    }
    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [
                ["id", "realm", "enabled"],
                ["token", "auth_realm", "auth_username", "auth_password"],
            ]
        ),
        required_together=([["auth_realm", "auth_username", "auth_password"]]),
    )

    result = {"changed": False, "msg": "", "diff": {}, "action": {}}

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get("realm")
    state = module.params.get("state")

    new_req_action_repr = {
        "alias": module.params.get("alias"),
        "config": module.params.get("config"),
        "defaultAction": module.params.get("default_action"),
        "enabled": module.params.get("enabled"),
        "name": module.params.get("name"),
        "priority": module.params.get("priority"),
        "providerId": module.params.get("provider_id"),
    }

    if not new_req_action_repr['enabled']:
        msg_details = " (not enabled)"
    else:
        msg_details = " (enabled and "
        if not new_req_action_repr['defaultAction']:
            msg_details = msg_details + "not "
        msg_details = msg_details + "default action)"

    req_action_repr = kc.get_required_action_by_alias(
        alias=new_req_action_repr["alias"], realm=realm
    )
    if req_action_repr == {}:  # Required action does not exist
        if state == "present":  # if desired state is present
            result["changed"] = True
            if module._diff:  # if module is in diff mode
                result["diff"] = {"before": "", "after": new_req_action_repr}
            if module.check_mode:  # if module is in check mode
                module.exit_json(**result)
            kc.register_new_required_action(new_req_action_repr, realm)
            result["action"] = new_req_action_repr
            result["msg"] = ("New required action " +
                             new_req_action_repr["alias"] +
                             " registered" +
                             msg_details)
        elif state == "absent":  # if desired state is absent
            if module._diff:
                result["diff"] = {"before": "", "after": ""}
            result["msg"] = ("Required action " +
                             new_req_action_repr["alias"] +
                             " already absent.")
    else:  # The required action already exists
        if state == "present":  # if desired state is present
            # check if new required action is different
            # from existing required action
            changed = False
            after = {}
            desired_action = req_action_repr.copy() | dict((k,v) for k,v in new_req_action_repr.items() if v is not None)
            changed = (desired_action != req_action_repr)
            result["changed"] = changed
            if not changed:
                if module._diff:
                    result["diff"] = {"before": "", "after": ""}
                result["action"] = req_action_repr
                result["msg"] = ("Required action " +
                                 new_req_action_repr["alias"] +
                                 msg_details +
                                 " not modified.")
                module.exit_json(**result)
            else:
                if module._diff:
                    result["diff"] = {
                        "before": req_action_repr,
                        "after": desired_action,
                    }
                if module.check_mode:  # if check mode, exit
                    module.exit_json(**result)
                # Update required action
                action = kc.update_required_action(desired_action, realm=realm)
                if module._diff:
                    result["diff"] = {
                        "before": req_action_repr,
                        "after": action,
                    }
                if action is not None:
                    req_action_repr = action
                result["action"] = req_action_repr
                result["msg"] = ("Required action " +
                                 new_req_action_repr["alias"] +
                                 msg_details +
                                 " modified.")
        elif state == "absent":  # if desired state is absent
            result["changed"] = True
            result["msg"] = ("Required action " +
                             new_req_action_repr["alias"] +
                             " deleted.")
            if module._diff:
                result["diff"] = {"before": req_action_repr, "after": ""}
            if module.check_mode:
                module.exit_json(**result)
            kc.delete_required_action(req_action_repr["alias"],
                                      realm=realm)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
