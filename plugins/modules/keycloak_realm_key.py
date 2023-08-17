#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six.moves.urllib.parse import urlencode
from copy import deepcopy
import json

DOCUMENTATION = '''
---
module: keycloak_realm_key

short_description: Allows administration of Keycloak realm keys via Keycloak API

description:
    - This module allows the administration of Keycloak realm via the Keycloak REST API. It
      requires access to the REST API via OpenID Connect; the user connecting and the realm being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate realm definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).
      Aliases are provided so camelCased versions can be used as well.

    - This module is unable to detect changes to the actual cryptographic key after importing it.
      However, if some other property is changed alongside the cryptographic key, then the key
      will also get changed as a side-effect, as the JSON payload needs to include the private key.
      This can be considered either a bug or a feature, as the alternative would be to always
      update the realm key whether it has changed or not.

options:
    state:
        description:
            - State of the keycloak realm key.
            - On C(present), the realm key will be created (or updated if it exists already).
            - On C(absent), the realm key will be removed if it exists.
        choices: ['present', 'absent']
        default: 'present'
        type: str
    name:
        description:
            - Name of the realm key to create.
        type: str
    parent_id:
        description:
            - The parent_id of the realm key. In practice the ID (name) of the realm.
        type: str
    provider_id:
        description:
            - The name of the "provider ID" for the key..
        choices: ['rsa']
        default: 'rsa'
        type: str
    config:
        description:
            - Dict specifying the key and its properties
        type: dict
        suboptions:
            active:
                description:
                    - Whether they key is active or inactive. Not to be confused with the state
                      of the Ansible resource managed by the "state" parameter.
                default: true
                type: bool
            enabled:
                description:
                    - Whether the key is enabled or disabled. Not to be confused with the state
                      of the Ansible resource managed by the "state" parameter.
                default: true
                type: bool
            priority:
                description:
                    - The priority of the key
                default: 100
                type: int
            algorithm:
                description:
                    - Key algorithm
                default: 'RSA256'
                choices: ['RSA256']
            private_key:
                description:
                    - The private key as an ASCII string. Contents of the key Must match algorithm
                      and provider_id
                    - Linefeeds should be converted into literal \n

extends_documentation_fragment:
    - community.general.keycloak

    author:
            - Samuli Seppänen (@mattock)
'''

EXAMPLES = '''
- name: Manage Keycloak realm key
    keycloak_realm_key:
      name: custom
      state: present
      parent_id: master
      provider_id: "rsa"
      auth_keycloak_url: "http://localhost:8080/auth"
      auth_username: keycloak
      auth_password: keycloak
      auth_realm: master
      config:
        private_key: "{{ private_key }}"
        enabled: true
        active: true
        priority: 120
        algorithm: "RS256"
'''

RETURN = '''
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule

def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type='str', default='present', choices=['present', 'absent']),
        name=dict(type='str', required=True),
        parent_id=dict(type='str', required=True),
        provider_id=dict(type='str', default='rsa', choices=['rsa']),
        config=dict(type='dict',
            options=dict(
                active=dict(type='bool', default=True),
                enabled=dict(type='bool', default=True),
                priority=dict(type='int', default=100),
                algorithm=dict(type='str', default='RS256', choices=['RS256']),
                private_key=dict(type='str', required=True, no_log=True)
            )
        )
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    # Initialize the result object. Only "changed" seems to have special
    # meaning for Ansible.
    result = dict(changed=False, msg='', end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    params_to_ignore = list(keycloak_argument_spec().keys()) + ["state"]

    # Filter and map the parameters names that apply to the role
    component_params = [x for x in module.params
                    if x not in params_to_ignore and
                    module.params.get(x) is not None]

    # We only support one component provider type in this module
    provider_type='org.keycloak.keys.KeyProvider'

    # Build a proposed changeset from parameters given to this module FIXME:
    # rename to "payload" or something as that reflects the variable's
    # purpose better.
    changeset = {}
    changeset['config'] = {}

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
        if component_param == 'config':
            for config_param in module.params.get('config'):
                changeset['config'][camel(config_param)] = []
                raw_value = module.params.get('config')[config_param]
                if isinstance(raw_value, bool):
                    value = str(raw_value).lower()
                else:
                    value = str(raw_value)

                changeset['config'][camel(config_param)].append(value)
        else:
          # No need for camelcase in here as these are one word parameters
          new_param_value = module.params.get(component_param)
          changeset[camel(component_param)] = new_param_value

    # As provider_type is not a module parameter we have to add it to the
    # changeset explicitly.
    changeset['providerType'] = provider_type

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
    del changeset_copy['config']['privateKey']

    # Make it easier to refer to current module parameters
    name = module.params.get('name')
    state = module.params.get('state')
    enabled = module.params.get('enabled')
    provider_id = module.params.get('provider_id')
    parent_id = module.params.get('parent_id')

    # Get a list of all Keycloak components that are of keyprovider type.
    realm_keys = kc.get_components(urlencode(dict(type=provider_type, parent=parent_id)), parent_id)

    # If this component is present get its key ID. Confusingly the key ID is
    # also known as the Provider ID.
    key_id = None

    # Track individual parameter changes
    changes=""

    # This tells Ansible whether the key was changed (added, removed, modified)
    result['changed'] = False

    # Loop through the list of components. If we encounter a component whose
    # name matches the value of the name parameter then assume the key is
    # already present.
    for key in realm_keys:
        if key['name'] == name:
            key_id = key['id']
            changeset['id'] = key_id
            changeset_copy['id'] = key_id

            # Compare top-level parameters
            for param, value in changeset.items():
                if changeset_copy[param] != key[param] and param != 'config':
                    changes += "%s: %s -> %s, " % (param, key[param], changeset_copy[param])
                    result['changed'] = True

            # Compare parameters under the "config" key
            for p, v in changeset_copy['config'].items():
                if changeset_copy['config'][p] != key['config'][p]:
                    changes += "config.%s: %s -> %s, " % (p, key['config'][p], changeset_copy['config'][p])
                    result['changed'] = True

    # Sanitize linefeeds for the privateKey. Without this the JSON payload
    # will be invalid.
    changeset['config']['privateKey'][0] = changeset['config']['privateKey'][0].replace('\\n', '\n')

    # Check all the possible states of the resource and do what is needed to
    # converge current state with desired state (create, update or delete
    # the key).
    if key_id and state == 'present':
        if result['changed']:
            kc.update_component(changeset, parent_id)
            result['msg'] = "Realm key %s changed: %s" % (name, changes.strip(", "))
        else:
            result['msg'] = "Realm key %s was in sync" % (name)
        result['end_state'] = changeset_copy
    elif key_id and state == 'absent':
        kc.delete_component(key_id, parent_id)
        result['changed'] = True
        result['msg'] = "Realm key %s deleted" % (name)
    elif not key_id and state == 'present':
        kc.create_component(changeset, parent_id)
        result['changed'] = True
        result['end_state'] = changeset_copy
        result['msg'] = "Realm key %s created" % (name)
    elif not key_id and state == 'absent':
        result['changed'] = False
        result['end_state'] = { state: state, name: name, parent_id: parent_id, enabled: enabled }
        result['msg'] = "Realm key %s not present" % (name)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
