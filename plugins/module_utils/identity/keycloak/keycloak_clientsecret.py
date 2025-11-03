#!/usr/bin/env python
# Copyright (c) 2022, John Cant <a.johncant@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import keycloak_argument_spec


def keycloak_clientsecret_module():
    """
    Returns an AnsibleModule definition for modules that interact with a client
    secret.

    :return: argument_spec dict
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        realm=dict(default="master"),
        id=dict(type="str"),
        client_id=dict(type="str", aliases=["clientId"]),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            [
                ["id", "client_id"],
                ["token", "auth_realm", "auth_username", "auth_password", "auth_client_id", "auth_client_secret"],
            ]
        ),
        required_together=([["auth_username", "auth_password"]]),
        mutually_exclusive=[["token", "auth_realm"], ["token", "auth_username"], ["token", "auth_password"]],
    )

    return module


def keycloak_clientsecret_module_resolve_params(module, kc):
    """
    Given an AnsibleModule definition for keycloak_clientsecret_*, and a
    KeycloakAPI client, resolve the params needed to interact with the Keycloak
    client secret, looking up the client by clientId if necessary via an API
    call.

    :return: tuple of id, realm
    """

    realm = module.params.get("realm")
    id = module.params.get("id")
    client_id = module.params.get("client_id")

    # only lookup the client_id if id isn't provided.
    # in the case that both are provided, prefer the ID, since it is one
    # less lookup.
    if id is None:
        # Due to the required_one_of spec, client_id is guaranteed to not be None
        client = kc.get_client_by_clientid(client_id, realm=realm)

        if client is None:
            module.fail_json(msg=f"Client does not exist {client_id}")

        id = client["id"]

    return id, realm
