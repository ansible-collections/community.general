#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_userprofile

short_description: Allows managing Keycloak User Profiles

description:
  - This module allows you to create, update, or delete Keycloak User Profiles using the Keycloak API. You can also customize
    the "Unmanaged Attributes" with it.
  - The names of module options are snake_cased versions of the camelCase ones found in the Keycloak API and its documentation
    at U(https://www.keycloak.org/docs-api/24.0.5/rest-api/index.html). For compatibility reasons, the module also accepts
    the camelCase versions of the options.
version_added: "9.4.0"

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
      - State of the User Profile provider.
      - On V(present), the User Profile provider will be created if it does not yet exist, or updated with the parameters
        you provide.
      - On V(absent), the User Profile provider will be removed if it exists.
    default: 'present'
    type: str
    choices:
      - present
      - absent

  parent_id:
    description:
      - The parent ID of the realm key. In practice the ID (name) of the realm.
    aliases:
      - parentId
      - realm
    type: str
    required: true

  provider_id:
    description:
      - The name of the provider ID for the key (supported value is V(declarative-user-profile)).
    aliases:
      - providerId
    choices: ['declarative-user-profile']
    default: 'declarative-user-profile'
    type: str

  provider_type:
    description:
      - Component type for User Profile (only supported value is V(org.keycloak.userprofile.UserProfileProvider)).
    aliases:
      - providerType
    choices: ['org.keycloak.userprofile.UserProfileProvider']
    default: org.keycloak.userprofile.UserProfileProvider
    type: str

  config:
    description:
      - The configuration of the User Profile Provider.
    type: dict
    required: false
    suboptions:
      kc_user_profile_config:
        description:
          - Define a declarative User Profile. See EXAMPLES for more context.
        aliases:
          - kcUserProfileConfig
        type: list
        elements: dict
        suboptions:
          attributes:
            description:
              - A list of attributes to be included in the User Profile.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - The name of the attribute.
                type: str
                required: true

              display_name:
                description:
                  - The display name of the attribute.
                aliases:
                  - displayName
                type: str
                required: true

              validations:
                description:
                  - The validations to be applied to the attribute.
                type: dict
                suboptions:
                  length:
                    description:
                      - The length validation for the attribute.
                    type: dict
                    suboptions:
                      min:
                        description:
                          - The minimum length of the attribute.
                        type: int
                      max:
                        description:
                          - The maximum length of the attribute.
                        type: int
                        required: true

                  email:
                    description:
                      - The email validation for the attribute.
                    type: dict

                  username_prohibited_characters:
                    description:
                      - The prohibited characters validation for the username attribute.
                    type: dict
                    aliases:
                      - usernameProhibitedCharacters

                  up_username_not_idn_homograph:
                    description:
                      - The validation to prevent IDN homograph attacks in usernames.
                    type: dict
                    aliases:
                      - upUsernameNotIdnHomograph

                  person_name_prohibited_characters:
                    description:
                      - The prohibited characters validation for person name attributes.
                    type: dict
                    aliases:
                      - personNameProhibitedCharacters

                  uri:
                    description:
                      - The URI validation for the attribute.
                    type: dict

                  pattern:
                    description:
                      - The pattern validation for the attribute using regular expressions.
                    type: dict

                  options:
                    description:
                      - Validation to ensure the attribute matches one of the provided options.
                    type: dict

              annotations:
                description:
                  - Annotations for the attribute.
                type: dict

              group:
                description:
                  - Specifies the User Profile group where this attribute will be added.
                type: str

              permissions:
                description:
                  - The permissions for viewing and editing the attribute.
                type: dict
                suboptions:
                  view:
                    description:
                      - The roles that can view the attribute.
                      - Supported values are V(admin) and V(user).
                    type: list
                    elements: str
                    default:
                      - admin
                      - user

                  edit:
                    description:
                      - The roles that can edit the attribute.
                      - Supported values are V(admin) and V(user).
                    type: list
                    elements: str
                    default:
                      - admin
                      - user

              multivalued:
                description:
                  - Whether the attribute can have multiple values.
                type: bool
                default: false

              required:
                description:
                  - The roles that require this attribute.
                type: dict
                suboptions:
                  roles:
                    description:
                      - The roles for which this attribute is required.
                      - Supported values are V(admin) and V(user).
                    type: list
                    elements: str
                    default:
                      - user

          groups:
            description:
              - A list of attribute groups to be included in the User Profile.
            type: list
            elements: dict
            suboptions:
              name:
                description:
                  - The name of the group.
                type: str
                required: true

              display_header:
                description:
                  - The display header for the group.
                aliases:
                  - displayHeader
                type: str
                required: true

              display_description:
                description:
                  - The display description for the group.
                aliases:
                  - displayDescription
                type: str
                required: false

              annotations:
                description:
                  - The annotations included in the group.
                type: dict
                required: false

          unmanaged_attribute_policy:
            description:
              - Policy for unmanaged attributes.
            aliases:
              - unmanagedAttributePolicy
            type: str
            choices:
              - ENABLED
              - ADMIN_EDIT
              - ADMIN_VIEW

notes:
  - Currently, only a single V(declarative-user-profile) entry is supported for O(provider_id) (design of the Keyckoak API).
    However, there can be multiple O(config.kc_user_profile_config[].attributes[]) entries.
extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes

author:
  - Eike Waldt (@yeoldegrove)
"""

EXAMPLES = r"""
- name: Create a Declarative User Profile with default settings
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    config:
      kc_user_profile_config:
        - attributes:
            - name: username
              displayName: ${username}
              validations:
                length:
                  min: 3
                  max: 255
                username_prohibited_characters: {}
                up_username_not_idn_homograph: {}
              annotations: {}
              permissions:
                view:
                  - admin
                  - user
                edit: []
              multivalued: false
            - name: email
              displayName: ${email}
              validations:
                email: {}
                length:
                  max: 255
              annotations: {}
              required:
                roles:
                  - user
              permissions:
                view:
                  - admin
                  - user
                edit: []
              multivalued: false
            - name: firstName
              displayName: ${firstName}
              validations:
                length:
                  max: 255
                person_name_prohibited_characters: {}
              annotations: {}
              required:
                roles:
                  - user
              permissions:
                view:
                  - admin
                  - user
                edit: []
              multivalued: false
            - name: lastName
              displayName: ${lastName}
              validations:
                length:
                  max: 255
                person_name_prohibited_characters: {}
              annotations: {}
              required:
                roles:
                  - user
              permissions:
                view:
                  - admin
                  - user
                edit: []
              multivalued: false
          groups:
            - name: user-metadata
              displayHeader: User metadata
              displayDescription: Attributes, which refer to user metadata
              annotations: {}

- name: Delete a Keycloak User Profile Provider
  keycloak_userprofile:
    state: absent
    parent_id: master

# Unmanaged attributes are user attributes not explicitly defined in the User Profile
# configuration. By default, unmanaged attributes are "Disabled" and are not
# available from any context such as registration, account, and the
# administration console. By setting "Enabled", unmanaged attributes are fully
# recognized by the server and accessible through all contexts, useful if you are
# starting migrating an existing realm to the declarative User Profile
# and you don't have yet all user attributes defined in the User Profile configuration.
- name: Enable Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    config:
      kc_user_profile_config:
        - unmanagedAttributePolicy: ENABLED

# By setting "Only administrators can write", unmanaged attributes can be managed
# only through the administration console and API, useful if you have already
# defined any custom attribute that can be managed by users but you are unsure
# about adding other attributes that should only be managed by administrators.
- name: Enable ADMIN_EDIT on Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    config:
      kc_user_profile_config:
        - unmanagedAttributePolicy: ADMIN_EDIT

# By setting `Only administrators can view`, unmanaged attributes are read-only
# and only available through the administration console and API.
- name: Enable ADMIN_VIEW on Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    config:
      kc_user_profile_config:
        - unmanagedAttributePolicy: ADMIN_VIEW
"""

RETURN = r"""
msg:
  description: The output message generated by the module.
  returned: always
  type: str
  sample: UserProfileProvider created successfully
data:
  description: The data returned by the Keycloak API.
  returned: when state is present
  type: dict
  sample: {'...': '...'}
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from copy import deepcopy
import json


def remove_null_values(data):
    if isinstance(data, dict):
        # Recursively remove null values from dictionaries
        return {k: remove_null_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        # Recursively remove null values from lists
        return [remove_null_values(item) for item in data if item is not None]
    else:
        # Return the data if it is neither a dictionary nor a list
        return data


def camel_recursive(data):
    if isinstance(data, dict):
        # Convert keys to camelCase and apply recursively
        return {camel(k): camel_recursive(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Apply camelCase conversion to each item in the list
        return [camel_recursive(item) for item in data]
    else:
        # Return the data as-is if it is not a dict or list
        return data


def main():
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        parent_id=dict(type='str', aliases=['parentId', 'realm'], required=True),
        provider_id=dict(type='str', aliases=['providerId'], default='declarative-user-profile', choices=['declarative-user-profile']),
        provider_type=dict(
            type='str',
            aliases=['providerType'],
            default='org.keycloak.userprofile.UserProfileProvider',
            choices=['org.keycloak.userprofile.UserProfileProvider']
        ),
        config=dict(
            type='dict',
            required=False,
            options={
                'kc_user_profile_config': dict(
                    type='list',
                    aliases=['kcUserProfileConfig'],
                    elements='dict',
                    options={
                        'attributes': dict(
                            type='list',
                            elements='dict',
                            required=False,
                            options={
                                'name': dict(type='str', required=True),
                                'display_name': dict(type='str', aliases=['displayName'], required=True),
                                'validations': dict(
                                    type='dict',
                                    options={
                                        'length': dict(
                                            type='dict',
                                            options={
                                                'min': dict(type='int', required=False),
                                                'max': dict(type='int', required=True)
                                            }
                                        ),
                                        'email': dict(type='dict', required=False),
                                        'username_prohibited_characters': dict(type='dict', aliases=['usernameProhibitedCharacters'], required=False),
                                        'up_username_not_idn_homograph': dict(type='dict', aliases=['upUsernameNotIdnHomograph'], required=False),
                                        'person_name_prohibited_characters': dict(type='dict', aliases=['personNameProhibitedCharacters'], required=False),
                                        'uri': dict(type='dict', required=False),
                                        'pattern': dict(type='dict', required=False),
                                        'options': dict(type='dict', required=False)
                                    }
                                ),
                                'annotations': dict(type='dict'),
                                'group': dict(type='str'),
                                'permissions': dict(
                                    type='dict',
                                    options={
                                        'view': dict(type='list', elements='str', default=['admin', 'user']),
                                        'edit': dict(type='list', elements='str', default=['admin', 'user'])
                                    }
                                ),
                                'multivalued': dict(type='bool', default=False),
                                'required': dict(
                                    type='dict',
                                    options={
                                        'roles': dict(type='list', elements='str', default=['user'])
                                    }
                                )
                            }
                        ),
                        'groups': dict(
                            type='list',
                            elements='dict',
                            options={
                                'name': dict(type='str', required=True),
                                'display_header': dict(type='str', aliases=['displayHeader'], required=True),
                                'display_description': dict(type='str', aliases=['displayDescription'], required=False),
                                'annotations': dict(type='dict', required=False)
                            }
                        ),
                        'unmanaged_attribute_policy': dict(
                            type='str',
                            aliases=['unmanagedAttributePolicy'],
                            choices=['ENABLED', 'ADMIN_EDIT', 'ADMIN_VIEW'],
                            required=False
                        )
                    }
                )
            }
        )
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]),
                           required_by={'refresh_token': 'auth_realm'},
                           )

    # Initialize the result object. Only "changed" seems to have special
    # meaning for Ansible.
    result = dict(changed=False, msg='', end_state={}, diff=dict(before={}, after={}))

    # This will include the current state of the realm userprofile if it is already
    # present. This is only used for diff-mode.
    before_realm_userprofile = {}
    before_realm_userprofile['config'] = {}

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    params_to_ignore = list(keycloak_argument_spec().keys()) + ["state"]

    # Filter and map the parameters names that apply to the role
    component_params = [
        x
        for x in module.params
        if x not in params_to_ignore and module.params.get(x) is not None
    ]

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    # Build the changeset with proper JSON serialization for kc_user_profile_config
    config = module.params.get('config')
    changeset['config'] = {}

    # Generate a JSON payload for Keycloak Admin API from the module
    # parameters.  Parameters that do not belong to the JSON payload (e.g.
    # "state" or "auth_keycloal_url") have been filtered away earlier (see
    # above).
    #
    # This loop converts Ansible module parameters (snake-case) into
    # Keycloak-compatible format (camel-case). For example proider_id
    # becomes providerId. It also handles some special cases, e.g. aliases.
    for component_param in component_params:
        # realm/parent_id parameter
        if component_param == 'realm' or component_param == 'parent_id':
            changeset['parent_id'] = module.params.get(component_param)
            changeset.pop(component_param, None)
        # complex parameters in config suboptions
        elif component_param == 'config':
            for config_param in config:
                # special parameter kc_user_profile_config
                if config_param in ('kcUserProfileConfig', 'kc_user_profile_config'):
                    config_param_org = config_param
                    # rename parameter to be accepted by Keycloak API
                    config_param = 'kc.user.profile.config'
                    # make sure no null values are passed to Keycloak API
                    kc_user_profile_config = remove_null_values(config[config_param_org])
                    changeset[camel(component_param)][config_param] = []
                    if len(kc_user_profile_config) > 0:
                        # convert aliases to camelCase
                        kc_user_profile_config = camel_recursive(kc_user_profile_config)
                        # rename validations to be accepted by Keycloak API
                        if 'attributes' in kc_user_profile_config[0]:
                            for attribute in kc_user_profile_config[0]['attributes']:
                                if 'validations' in attribute:
                                    if 'usernameProhibitedCharacters' in attribute['validations']:
                                        attribute['validations']['username-prohibited-characters'] = (
                                            attribute['validations'].pop('usernameProhibitedCharacters')
                                        )
                                    if 'upUsernameNotIdnHomograph' in attribute['validations']:
                                        attribute['validations']['up-username-not-idn-homograph'] = (
                                            attribute['validations'].pop('upUsernameNotIdnHomograph')
                                        )
                                    if 'personNameProhibitedCharacters' in attribute['validations']:
                                        attribute['validations']['person-name-prohibited-characters'] = (
                                            attribute['validations'].pop('personNameProhibitedCharacters')
                                        )
                        changeset[camel(component_param)][config_param].append(kc_user_profile_config[0])
                # usual camelCase parameters
                else:
                    changeset[camel(component_param)][camel(config_param)] = []
                    raw_value = module.params.get(component_param)[config_param]
                    if isinstance(raw_value, bool):
                        value = str(raw_value).lower()
                    else:
                        value = raw_value  # Directly use the raw value
                    changeset[camel(component_param)][camel(config_param)].append(value)
        # usual parameters
        else:
            new_param_value = module.params.get(component_param)
            changeset[camel(component_param)] = new_param_value

    # Make it easier to refer to current module parameters
    state = module.params.get('state')
    enabled = module.params.get('enabled')
    parent_id = module.params.get('parent_id')
    provider_type = module.params.get('provider_type')
    provider_id = module.params.get('provider_id')

    # Make a deep copy of the changeset. This is use when determining
    # changes to the current state.
    changeset_copy = deepcopy(changeset)

    # Get a list of all Keycloak components that are of userprofile provider type.
    realm_userprofiles = kc.get_components(urlencode(dict(type=provider_type)), parent_id)

    # If this component is present get its userprofile ID. Confusingly the userprofile ID is
    # also known as the Provider ID.
    userprofile_id = None

    # Track individual parameter changes
    changes = ""

    # This tells Ansible whether the userprofile was changed (added, removed, modified)
    result['changed'] = False

    # Loop through the list of components. If we encounter a component whose
    # name matches the value of the name parameter then assume the userprofile is
    # already present.
    for userprofile in realm_userprofiles:
        if provider_id == "declarative-user-profile":
            userprofile_id = userprofile['id']
            changeset['id'] = userprofile_id
            changeset_copy['id'] = userprofile_id

            # keycloak returns kc.user.profile.config as a single JSON formatted string, so we have to deserialize it
            if 'config' in userprofile and 'kc.user.profile.config' in userprofile['config']:
                userprofile['config']['kc.user.profile.config'][0] = json.loads(userprofile['config']['kc.user.profile.config'][0])

            # Compare top-level parameters
            for param, value in changeset.items():
                before_realm_userprofile[param] = userprofile[param]

                if changeset_copy[param] != userprofile[param] and param != 'config':
                    changes += "%s: %s -> %s, " % (param, userprofile[param], changeset_copy[param])
                    result['changed'] = True

            # Compare parameters under the "config" userprofile
            for p, v in changeset_copy['config'].items():
                before_realm_userprofile['config'][p] = userprofile['config'][p]
                if changeset_copy['config'][p] != userprofile['config'][p]:
                    changes += "config.%s: %s -> %s, " % (p, userprofile['config'][p], changeset_copy['config'][p])
                    result['changed'] = True

    # Check all the possible states of the resource and do what is needed to
    # converge current state with desired state (create, update or delete
    # the userprofile).

    # keycloak expects kc.user.profile.config as a single JSON formatted string, so we have to serialize it
    if 'config' in changeset and 'kc.user.profile.config' in changeset['config']:
        changeset['config']['kc.user.profile.config'][0] = json.dumps(changeset['config']['kc.user.profile.config'][0])
    if userprofile_id and state == 'present':
        if result['changed']:
            if module._diff:
                result['diff'] = dict(before=before_realm_userprofile, after=changeset_copy)

            if module.check_mode:
                result['msg'] = "Userprofile %s would be changed: %s" % (provider_id, changes.strip(", "))
            else:
                kc.update_component(changeset, parent_id)
                result['msg'] = "Userprofile %s changed: %s" % (provider_id, changes.strip(", "))
        else:
            result['msg'] = "Userprofile %s was in sync" % (provider_id)

        result['end_state'] = changeset_copy
    elif userprofile_id and state == 'absent':
        if module._diff:
            result['diff'] = dict(before=before_realm_userprofile, after={})

        if module.check_mode:
            result['changed'] = True
            result['msg'] = "Userprofile %s would be deleted" % (provider_id)
        else:
            kc.delete_component(userprofile_id, parent_id)
            result['changed'] = True
            result['msg'] = "Userprofile %s deleted" % (provider_id)

        result['end_state'] = {}
    elif not userprofile_id and state == 'present':
        if module._diff:
            result['diff'] = dict(before={}, after=changeset_copy)

        if module.check_mode:
            result['changed'] = True
            result['msg'] = "Userprofile %s would be created" % (provider_id)
        else:
            kc.create_component(changeset, parent_id)
            result['changed'] = True
            result['msg'] = "Userprofile %s created" % (provider_id)

        result['end_state'] = changeset_copy
    elif not userprofile_id and state == 'absent':
        result['changed'] = False
        result['msg'] = "Userprofile %s not present" % (provider_id)
        result['end_state'] = {}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
