#!/usr/bin/python

# Copyright (c) 2024, Björn Bösel <bjoernboesel@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
module: keycloak_component

short_description: Allows administration of Keycloak components using Keycloak API

version_added: 10.0.0

description:
  - This module allows the administration of Keycloak components using the Keycloak REST API. It requires access to the REST
    API using OpenID Connect; the user connecting and the realm being used must have the requisite access rights. In a default
    Keycloak installation, C(admin-cli) and an C(admin) user would work, as would a separate realm definition with the scope
    tailored to your needs and a user having the expected roles.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/latest/rest-api/index.html). Aliases are provided so camelCased versions can be
    used as well.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 10.2.0

options:
  state:
    description:
      - State of the Keycloak component.
      - On V(present), the component is created (or updated if it exists already).
      - On V(absent), the component is removed if it exists.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  name:
    description:
      - Name of the component to create.
    type: str
    required: true
  parent_id:
    description:
      - The parent_id of the component. In practice the ID (name) of the realm.
    type: str
    required: true
  provider_id:
    description:
      - The name of the "provider ID" for the key.
    type: str
    required: true
  provider_type:
    description:
      - The name of the "provider type" for the key. That is, V(org.keycloak.storage.UserStorageProvider), V(org.keycloak.userprofile.UserProfileProvider),
        ...
      - See U(https://www.keycloak.org/docs/latest/server_development/index.html#_providers).
    type: str
    required: true
  config:
    description:
      - Configuration properties for the provider.
      - Contents vary depending on the provider type.
    type: dict

extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Björn Bösel (@fivetide)
"""

EXAMPLES = r"""
- name: Manage Keycloak User Storage Provider
  community.general.keycloak_component:
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
    name: my storage provider
    state: present
    parent_id: some_realm
    provider_id: my storage
    provider_type: "org.keycloak.storage.UserStorageProvider"
    config:
      myCustomKey: "my_custom_key"
      cachePolicy: "NO_CACHE"
      enabled: true
"""

RETURN = r"""
end_state:
  description: Representation of the keycloak_component after module execution.
  returned: on success
  type: dict
  contains:
    id:
      description: ID of the component.
      type: str
      returned: when O(state=present)
      sample: 5b7ec13f-99da-46ad-8326-ab4c73cf4ce4
    name:
      description: Name of the component.
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
      description: Component configuration.
      type: dict
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
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type="str", default="present", choices=["present", "absent"]),
        name=dict(type="str", required=True),
        parent_id=dict(type="str", required=True),
        provider_id=dict(type="str", required=True),
        provider_type=dict(type="str", required=True),
        config=dict(
            type="dict",
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

    result = dict(changed=False, msg="", end_state={}, diff=dict(before={}, after={}))

    # This will include the current state of the component if it is already
    # present. This is only used for diff-mode.
    before_component = {}
    before_component["config"] = {}

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    params_to_ignore = list(keycloak_argument_spec().keys()) + ["state", "parent_id"]

    # Filter and map the parameters names that apply to the role
    component_params = [x for x in module.params if x not in params_to_ignore and module.params.get(x) is not None]

    provider_type = module.params.get("provider_type")

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

    # Make a deep copy of the changeset. This is use when determining
    # changes to the current state.
    changeset_copy = deepcopy(changeset)

    # Make it easier to refer to current module parameters
    name = module.params.get("name")
    state = module.params.get("state")
    provider_type = module.params.get("provider_type")
    parent_id = module.params.get("parent_id")

    # Get a list of all Keycloak components that are of keyprovider type.
    current_components = kc.get_components(urlencode(dict(type=provider_type)), parent_id)

    # If this component is present get its key ID. Confusingly the key ID is
    # also known as the Provider ID.
    component_id = None

    # Track individual parameter changes
    changes = ""

    # This tells Ansible whether the key was changed (added, removed, modified)
    result["changed"] = False

    # Loop through the list of components. If we encounter a component whose
    # name matches the value of the name parameter then assume the key is
    # already present.
    for component in current_components:
        if component["name"] == name:
            component_id = component["id"]
            changeset["id"] = component_id
            changeset_copy["id"] = component_id

            # Compare top-level parameters
            for param, value in changeset.items():
                before_component[param] = component[param]

                if changeset_copy[param] != component[param] and param != "config":
                    changes += f"{param}: {component[param]} -> {changeset_copy[param]}, "
                    result["changed"] = True
            # Compare parameters under the "config" key
            for p, v in changeset_copy["config"].items():
                try:
                    before_component["config"][p] = component["config"][p] or []
                except KeyError:
                    before_component["config"][p] = []
                if changeset_copy["config"][p] != component["config"][p]:
                    changes += f"config.{p}: {component['config'][p]} -> {changeset_copy['config'][p]}, "
                    result["changed"] = True

    # Check all the possible states of the resource and do what is needed to
    # converge current state with desired state (create, update or delete
    # the key).
    if component_id and state == "present":
        if result["changed"]:
            if module._diff:
                result["diff"] = dict(before=before_component, after=changeset_copy)

            if module.check_mode:
                result["msg"] = f"Component {name} would be changed: {changes.strip(', ')}"
            else:
                kc.update_component(changeset, parent_id)
                result["msg"] = f"Component {name} changed: {changes.strip(', ')}"
        else:
            result["msg"] = f"Component {name} was in sync"

        result["end_state"] = changeset_copy
    elif component_id and state == "absent":
        if module._diff:
            result["diff"] = dict(before=before_component, after={})

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Component {name} would be deleted"
        else:
            kc.delete_component(component_id, parent_id)
            result["changed"] = True
            result["msg"] = f"Component {name} deleted"

        result["end_state"] = {}
    elif not component_id and state == "present":
        if module._diff:
            result["diff"] = dict(before={}, after=changeset_copy)

        if module.check_mode:
            result["changed"] = True
            result["msg"] = f"Component {name} would be created"
        else:
            kc.create_component(changeset, parent_id)
            result["changed"] = True
            result["msg"] = f"Component {name} created"

        result["end_state"] = changeset_copy
    elif not component_id and state == "absent":
        result["changed"] = False
        result["msg"] = f"Component {name} not present"
        result["end_state"] = {}

    module.exit_json(**result)


if __name__ == "__main__":
    main()
