#!/usr/bin/python

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_realm_key

short_description: Allows administration of Keycloak realm keys using Keycloak API

version_added: 7.5.0

description:
  - This module allows the administration of Keycloak realm keys using the Keycloak REST API. It requires access to the REST
    API using OpenID Connect; the user connecting and the realm being used must have the requisite access rights. In a default
    Keycloak installation, admin-cli and an admin user would work, as would a separate realm definition with the scope tailored
    to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html). Aliases are provided so camelCased versions can be used
    as well.
  - This module is unable to detect changes to the actual cryptographic key after importing it. However, if some other property
    is changed alongside the cryptographic key, then the key also changes as a side-effect, as the JSON payload needs to include
    the private key. This can be considered either a bug or a feature, as the alternative would be to always update the realm
    key whether it has changed or not.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the keycloak realm key.
      - On V(present), the realm key is created (or updated if it exists already).
      - On V(absent), the realm key is removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  name:
    description:
      - Name of the realm key to create.
    type: str
    required: true
  force:
    description:
      - Enforce the state of the private key and certificate. This is not automatically the case as this module is unable
        to determine the current state of the private key and thus cannot trigger an update based on an actual divergence.
        That said, a private key update may happen even if force is false as a side-effect of other changes.
    default: false
    type: bool
  parent_id:
    description:
      - The parent_id of the realm key. In practice the name of the realm.
    type: str
    required: true
  provider_id:
    description:
      - The name of the "provider ID" for the key.
      - The value V(rsa-enc) has been added in community.general 8.2.0.
    choices: ['rsa', 'rsa-enc']
    default: 'rsa'
    type: str
  config:
    description:
      - Dict specifying the key and its properties.
    type: dict
    suboptions:
      active:
        description:
          - Whether they key is active or inactive. Not to be confused with the state of the Ansible resource managed by the
            O(state) parameter.
        default: true
        type: bool
      enabled:
        description:
          - Whether the key is enabled or disabled. Not to be confused with the state of the Ansible resource managed by the
            O(state) parameter.
        default: true
        type: bool
      priority:
        description:
          - The priority of the key.
        type: int
        required: true
      algorithm:
        description:
          - Key algorithm.
          - The values V(RS384), V(RS512), V(PS256), V(PS384), V(PS512), V(RSA1_5), V(RSA-OAEP), V(RSA-OAEP-256) have been
            added in community.general 8.2.0.
        default: RS256
        choices: ['RS256', 'RS384', 'RS512', 'PS256', 'PS384', 'PS512', 'RSA1_5', 'RSA-OAEP', 'RSA-OAEP-256']
        type: str
      private_key:
        description:
          - The private key as an ASCII string. Contents of the key must match O(config.algorithm) and O(provider_id).
          - Please note that the module cannot detect whether the private key specified differs from the current state's private
            key. Use O(force=true) to force the module to update the private key if you expect it to be updated.
        required: true
        type: str
      certificate:
        description:
          - A certificate signed with the private key as an ASCII string. Contents of the key must match O(config.algorithm)
            and O(provider_id).
          - If you want Keycloak to automatically generate a certificate using your private key then set this to an empty
            string.
        required: true
        type: str
notes:
  - Current value of the private key cannot be fetched from Keycloak. Therefore comparing its desired state to the current
    state is not possible.
  - If O(config.certificate) is not explicitly provided it is dynamically created by Keycloak. Therefore comparing the current
    state of the certificate to the desired state (which may be empty) is not possible.
  - Due to the private key and certificate options the module is B(not fully idempotent). You can use O(force=true) to force
    the module to ensure updating if you know that the private key might have changed.
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Samuli Seppänen (@mattock)
"""

EXAMPLES = r"""
- name: Manage Keycloak realm key (certificate autogenerated by Keycloak)
  community.general.keycloak_realm_key:
    name: custom
    state: present
    parent_id: master
    provider_id: rsa
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      private_key: "{{ private_key }}"
      certificate: ""
      enabled: true
      active: true
      priority: 120
      algorithm: RS256
- name: Manage Keycloak realm key and certificate
  community.general.keycloak_realm_key:
    name: custom
    state: present
    parent_id: master
    provider_id: rsa
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    config:
      private_key: "{{ private_key }}"
      certificate: "{{ certificate }}"
      enabled: true
      active: true
      priority: 120
      algorithm: RS256
"""

RETURN = r"""
msg:
  description: Message as to what action was taken.
  returned: always
  type: str

end_state:
  description: Representation of the keycloak_realm_key after module execution.
  returned: on success
  type: dict
  contains:
    id:
      description: ID of the realm key.
      type: str
      returned: when O(state=present)
      sample: 5b7ec13f-99da-46ad-8326-ab4c73cf4ce4
    name:
      description: Name of the realm key.
      type: str
      returned: when O(state=present)
      sample: mykey
    parentId:
      description: ID of the realm this key belongs to.
      type: str
      returned: when O(state=present)
      sample: myrealm
    providerId:
      description: The ID of the key provider.
      type: str
      returned: when O(state=present)
      sample: rsa
    providerType:
      description: The type of provider.
      type: str
      returned: when O(state=present)
    config:
      description: Realm key configuration.
      type: dict
      returned: when O(state=present)
      sample:
        {
          "active": [
            "true"
          ],
          "algorithm": [
            "RS256"
          ],
          "enabled": [
            "true"
          ],
          "priority": [
            "140"
          ]
        }
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI,
    camel,
    keycloak_argument_spec,
    get_token,
    KeycloakError,
)
from ansible.module_utils.basic import AnsibleModule
from urllib.parse import urlencode
from copy import deepcopy


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        name=dict(type="str", required=True),
        force=dict(type="bool", default=False),
        parent_id=dict(type="str", required=True),
        provider_id=dict(type="str", default="rsa", choices=["rsa", "rsa-enc"]),
        config=dict(
            type="dict",
            options=dict(
                active=dict(type="bool", default=True),
                enabled=dict(type="bool", default=True),
                priority=dict(type="int", required=True),
                algorithm=dict(
                    type="str",
                    default="RS256",
                    choices=[
                        "RS256",
                        "RS384",
                        "RS512",
                        "PS256",
                        "PS384",
                        "PS512",
                        "RSA1_5",
                        "RSA-OAEP",
                        "RSA-OAEP-256",
                    ],
                ),
                private_key=dict(type="str", required=True, no_log=True),
                certificate=dict(type="str", required=True),
            ),
        ),
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

    # Initialize the result object. Only "changed" seems to have special
    # meaning for Ansible.
    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # This will include the current state of the realm key if it is already
    # present. This is only used for diff-mode.
    before_realm_key = {}
    before_realm_key["config"] = {}

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    params_to_ignore = list(keycloak_argument_spec().keys()) + ["state", "force", "parent_id"]

    # Filter and map the parameters names that apply to the role
    component_params = [x for x in module.params if x not in params_to_ignore and module.params.get(x) is not None]

    # We only support one component provider type in this module
    provider_type = "org.keycloak.keys.KeyProvider"

    # Build a proposed changeset from parameters given to this module
    changeset = {}
    changeset["config"] = {}

    # Generate a JSON payload for Keycloak Admin API from the module
    # parameters.  Parameters that do not belong to the JSON payload (e.g.
    # "state" or "auth_keycloal_url") have been filtered away earlier (see
    # above).
    #
    # This loop converts Ansible module parameters (snake-case) into
    # Keycloak-compatible format (camel-case). For example private_key
    # becomes privateKey.
    #
    # It also converts bool, str and int parameters into lists with a single
    # entry of 'str' type. Bool values are also lowercased. This is required
    # by Keycloak.
    #
    for component_param in component_params:
        if component_param == "config":
            for config_param in module.params.get("config"):
                changeset["config"][camel(config_param)] = []
                raw_value = module.params.get("config")[config_param]
                if isinstance(raw_value, bool):
                    value = str(raw_value).lower()
                else:
                    value = str(raw_value)

                changeset["config"][camel(config_param)].append(value)
        else:
            # No need for camelcase in here as these are one word parameters
            new_param_value = module.params.get(component_param)
            changeset[camel(component_param)] = new_param_value

    # As provider_type is not a module parameter we have to add it to the
    # changeset explicitly.
    changeset["providerType"] = provider_type

    # Make a deep copy of the changeset. This is use when determining
    # changes to the current state.
    changeset_copy = deepcopy(changeset)

    # It is not possible to compare current keys to desired keys, because the
    # certificate parameter is a base64-encoded binary blob created on the fly
    # when a key is added. Moreover, the Keycloak Admin API does not seem to
    # return the value of the private key for comparison.  So, in effect, it we
    # just have to ignore changes to the keys.  However, as the privateKey
    # parameter needs be present in the JSON payload, any changes done to any
    # other parameters (e.g.  config.priority) will trigger update of the keys
    # as a side-effect.
    del changeset_copy["config"]["privateKey"]
    del changeset_copy["config"]["certificate"]

    # Make it easier to refer to current module parameters
    name = module.params.get("name")
    force = module.params.get("force")
    state = module.params.get("state")
    parent_id = module.params.get("parent_id")

    # Get a list of all Keycloak components that are of keyprovider type.
    realm_keys = kc.get_components(urlencode(dict(type=provider_type)), parent_id)

    # If this component is present get its key ID. Confusingly the key ID is
    # also known as the Provider ID.
    key_id = None

    # Track individual parameter changes
    changes = ""

    # This tells Ansible whether the key was changed (added, removed, modified)
    result["changed"] = False

    # Loop through the list of components. If we encounter a component whose
    # name matches the value of the name parameter then assume the key is
    # already present.
    for key in realm_keys:
        if key["name"] == name:
            key_id = key["id"]
            changeset["id"] = key_id
            changeset_copy["id"] = key_id

            # Compare top-level parameters
            for param, value in changeset.items():
                before_realm_key[param] = key[param]

                if changeset_copy[param] != key[param] and param != "config":
                    changes += f"{param}: {key[param]} -> {changeset_copy[param]}, "
                    result["changed"] = True

            # Compare parameters under the "config" key
            for p, v in changeset_copy["config"].items():
                before_realm_key["config"][p] = key["config"][p]
                if changeset_copy["config"][p] != key["config"][p]:
                    changes += f"config.{p}: {key['config'][p]} -> {changeset_copy['config'][p]}, "
                    result["changed"] = True

    # Sanitize linefeeds for the privateKey. Without this the JSON payload
    # will be invalid.
    changeset["config"]["privateKey"][0] = changeset["config"]["privateKey"][0].replace("\\n", "\n")
    changeset["config"]["certificate"][0] = changeset["config"]["certificate"][0].replace("\\n", "\n")

    # Check all the possible states of the resource and do what is needed to
    # converge current state with desired state (create, update or delete
    # the key).
    if key_id and state == "present":
        if result["changed"]:
            if module._diff:
                del before_realm_key["config"]["privateKey"]
                del before_realm_key["config"]["certificate"]
                result["diff"] = dict(before=before_realm_key, after=changeset_copy)

            if module.check_mode:
                result["msg"] = f"Realm key {name} would be changed: {changes.strip(', ')}"
            else:
                kc.update_component(changeset, parent_id)
                result["msg"] = f"Realm key {name} changed: {changes.strip(', ')}"
        elif not result["changed"] and force:
            kc.update_component(changeset, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} was forcibly updated"
        else:
            result["msg"] = f"Realm key {name} was in sync"

        result["end_state"] = changeset_copy
    elif key_id and state == "absent":
        if module._diff:
            del before_realm_key["config"]["privateKey"]
            del before_realm_key["config"]["certificate"]
            result["diff"] = dict(before=before_realm_key, after={})

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Realm key {name} would be deleted"
        else:
            kc.delete_component(key_id, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} deleted"

        result["end_state"] = {}
    elif not key_id and state == "present":
        if module._diff:
            result["diff"] = dict(before={}, after=changeset_copy)

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Realm key {name} would be created"
        else:
            kc.create_component(changeset, parent_id)
            result["changed"] = True
            result["msg"] = f"Realm key {name} created"

        result["end_state"] = changeset_copy
    elif not key_id and state == "absent":
        result["changed"] = False
        result["msg"] = f"Realm key {name} not present"
        result["end_state"] = {}

    module.exit_json(**result)


if __name__ == "__main__":
    main()
