#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_userprofile

short_description: Allows managing Keycloak User Profiles.

description:
  - This module allows you to create, update, or delete Keycloak User Profiles via Keycloak API. You can also customize the "Unmanaged Attributes" with it.

version_added: "9.3.0"

attributes:
    check_mode:
        support: full
    diff_mode:
        support: full

options:
    state:
        description:
            - State of the user profile provider.
            - On C(present), the user profile provider will be created if it does not yet exist, or updated with
              the parameters you provide.
            - On C(absent), the user profile provider will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent
    parent_id:
        description:
            - The parent_id of the realm userprofile. In practice, the ID (name) of the realm.
        type: str
        required: true
    provider_id:
        description:
            - The name of the "provider ID" for the userprofile.
        choices: ['declarative-user-profile']
        default: 'declarative-user-profile'
        type: str
    config:
        description:
            - The configuration of the User Profile Provider.
        type: dict
        required: false
        suboptions:
            "kc.user.profile.config":
                description:
                    - Define a declarative user profile. See EXAMPLES for more context.
                type: list
                elements: dict
                suboptions:
                    attributes:
                        description:
                            - A list of attributes to be included in the user profile.
                        type: list
                        elements: dict
                        suboptions:
                            name:
                                description:
                                    - The name of the attribute.
                                type: str
                                required: true
                            displayName:
                                description:
                                    - The display name of the attribute.
                                type: str
                                required: true
                            validations:
                                description:
                                    - The validations to be applied to the attribute.
                                type: dict
                                # suboptions:
                                #     length:
                                #         description:
                                #             - The length validation for the attribute.
                                #         type: dict
                                #         suboptions:
                                #             min:
                                #                 description:
                                #                     - The minimum length of the attribute.
                                #                 type: int
                                #             max:
                                #                 description:
                                #                     - The maximum length of the attribute.
                                #                 type: int
                                #                 required: true
                                #     email:
                                #         description:
                                #             - The email validation for the attribute.
                                #         type: dict
                                #     username-prohibited-characters:
                                #         description:
                                #             - The prohibited characters validation for the username attribute.
                                #         type: dict
                                #     up-username-not-idn-homograph:
                                #         description:
                                #             - The validation to prevent IDN homograph attacks in usernames.
                                #         type: dict
                                #     person-name-prohibited-characters:
                                #         description:
                                #             - The prohibited characters validation for person name attributes.
                                #         type: dict
                                #     uri:
                                #         description:
                                #             - The URI validation for the attribute.
                                #         type: dict
                                #     pattern:
                                #         description:
                                #             - The pattern validation for the attribute using regular expressions.
                                #         type: dict
                                #     options:
                                #         description:
                                #             - Validation to ensure the attribute matches one of the provided options.
                                #         type: dict
                            annotations:
                                description:
                                    - Annotations for the attribute.
                                type: dict
                            group:
                                description:
                                    - Specifies the user profile group where this attribute will be added.
                                type: str
                            permissions:
                                description:
                                    - The permissions for viewing and editing the attribute.
                                type: dict
                                suboptions:
                                    view:
                                        description:
                                            - The roles that can view the attribute.
                                        type: list
                                        elements: str
                                        default:
                                          - admin
                                          - user
                                    edit:
                                        description:
                                            - The roles that can edit the attribute.
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
                                        type: list
                                        elements: str
                                        default:
                                          - user
                    groups:
                        description:
                            - A list of attribute groups to be included in the user profile.
                        type: list
                        elements: dict
                        suboptions:
                            name:
                                description:
                                    - The name of the group.
                                type: str
                                required: true
                            displayHeader:
                                description:
                                    - The display header for the group.
                                type: str
                                required: true
                            displayDescription:
                                description:
                                    - The display description for the group.
                                type: str
                                required: false
                            annotations:
                                description:
                                    - The annotations included in the group.
                                type: dict
                                required: false
                    unmanagedAttributePolicy:
                        description:
                            - Policy for unmanaged attributes.
                        type: str
                        choices:
                            - ENABLED
                            - ADMIN_EDIT
                            - ADMIN_VIEW

notes:
    - Currently only the provider_id of declarative-user-profile is tested.
    - Currently only a single declarative-user-profile entry can exist. This entry can have multiple attributes, though.

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
  - Eike Waldt (@yeoldegrove)
'''

EXAMPLES = '''
- name: Create a Declarative User Profile with default settings
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    provider_id: declarative-user-profile
    config:
      kc.user.profile.config:
        - attributes:
            - name: username
              displayName: ${username}
              validations:
                length:
                  min: 3
                  max: 255
                username-prohibited-characters: {}
                up-username-not-idn-homograph: {}
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
                person-name-prohibited-characters: {}
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
                person-name-prohibited-characters: {}
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
    provider_id: declarative-user-profile

# Unmanaged attributes are user attributes not explicitly defined in the user profile configuration. By default, unmanaged attributes are `Disabled`
# and are not available from any context such as registration, account, and the administration console. By setting `Enabled`, unmanaged attributes are fully
# recognized by the server and accessible through all contexts, useful if you are starting migrating an existing realm to the declarative user profile
# and you don't have yet all user attributes defined in the user profile configuration.
- name: Enable Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    provider_id: declarative-user-profile
    config:
      kc.user.profile.config:
        - unmanagedAttributePolicy: ENABLED

# By setting `Only administrators can write`, unmanaged attributes can be managed only through the administration console and API, useful if you have already
# defined any custom attribute that can be managed by users but you are unsure about adding other attributes that should only be managed by administrators.
- name: Enable ADMIN_EDIT on Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    provider_id: declarative-user-profile
    config:
      kc.user.profile.config:
        - unmanagedAttributePolicy: ADMIN_EDIT

# By setting `Only administrators can view`, unmanaged attributes are read-only and only available through the administration console and API.
- name: Enable ADMIN_VIEW on Unmanaged Attributes
  community.general.keycloak_userprofile:
    state: present
    parent_id: master
    provider_id: declarative-user-profile
    config:
      kc.user.profile.config:
        - unmanagedAttributePolicy: ADMIN_VIEW
'''

RETURN = '''
msg:
  description: The output message generated by the module.
  returned: always
  type: str
  sample: UserProfileProvider created successfully
data:
  description: The data returned by the Keycloak API.
  returned: when state is present
  type: dict
  sample: {...}
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from copy import deepcopy
import json


def main():
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        parent_id=dict(type='str', required=True),
        provider_id=dict(type='str', default='declarative-user-profile', choices=['declarative-user-profile']),
        config=dict(
            type='dict',
            required=False,
            options={
                "kc.user.profile.config": dict(
                    type='list',
                    elements='dict',
                    options={
                        'attributes': dict(
                            type='list',
                            elements='dict',
                            required=False,
                            options={
                                'name': dict(type='str', required=True),
                                'displayName': dict(type='str', required=True),
                                'validations': dict(
                                    type='dict',
                                    # TODO: template this too but without passing null on unrequired empty key/value pairs
                                    # options={
                                    #     'length': dict(
                                    #         type='dict',
                                    #         options={
                                    #             'min': dict(type='int', required=False),
                                    #             'max': dict(type='int', required=True)
                                    #         }
                                    #     ),
                                    #     'email': dict(type='dict', required=False),
                                    #     'username-prohibited-characters': dict(type='dict', required=False),
                                    #     'up-username-not-idn-homograph': dict(type='dict', required=False),
                                    #     'person-name-prohibited-characters': dict(type='dict', required=False),
                                    #     'uri': dict(type='dict', required=False),
                                    #     'pattern': dict(type='dict', required=False),
                                    #     'options': dict(type='dict', required=False)
                                    # }
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
                                'displayHeader': dict(type='str', required=True),
                                'displayDescription': dict(type='str', required=False),
                                'annotations': dict(type='dict', required=False)
                            }
                        ),
                        'unmanagedAttributePolicy': dict(type='str', choices=['ENABLED', 'ADMIN_EDIT', 'ADMIN_VIEW'], required=False)
                    }
                )
            }
        )
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

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
    component_params = [x for x in module.params
                        if x not in params_to_ignore and
                        module.params.get(x) is not None]

    # We only support one component provider type in this module
    provider_type = 'org.keycloak.userprofile.UserProfileProvider'

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    # Build the changeset with proper JSON serialization for kc.user.profile.config
    config = module.params['config']
    changeset['config'] = {}

    # Generate a JSON payload for Keycloak Admin API from the module
    # parameters.  Parameters that do not belong to the JSON payload (e.g.
    # "state" or "auth_keycloal_url") have been filtered away earlier (see
    # above).
    #
    # This loop converts Ansible module parameters (snake-case) into
    # Keycloak-compatible format (camel-case). For example private_key
    # becomes privateKey.
    for component_param in component_params:
        if component_param == 'config':
            for config_param in module.params.get('config'):
                changeset['config'][camel(config_param)] = []
                raw_value = module.params.get('config')[config_param]
                if isinstance(raw_value, bool):
                    value = str(raw_value).lower()
                else:
                    value = raw_value  # Directly use the raw value
                # special case for kc.user.profile.config
                if config_param == 'kc.user.profile.config':
                    kc_user_profile_config = config['kc.user.profile.config']
                    if len(kc_user_profile_config) > 0:
                        value = json.dumps(kc_user_profile_config[0])
                changeset['config'][camel(config_param)].append(value)
        else:
            # No need for camelcase in here as these are one-word parameters
            new_param_value = module.params.get(component_param)
            changeset[camel(component_param)] = new_param_value

    # As provider_type is not a module parameter we have to add it to the
    # changeset explicitly.
    changeset['providerType'] = provider_type

    # Make a deep copy of the changeset. This is use when determining
    # changes to the current state.
    changeset_copy = deepcopy(changeset)

    # Make it easier to refer to current module parameters
    state = module.params.get('state')
    enabled = module.params.get('enabled')
    provider_id = module.params.get('provider_id')
    parent_id = module.params.get('parent_id')

    # Get a list of all Keycloak components that are of userprofile provider type.
    realm_userprofiles = kc.get_components(urlencode(dict(type=provider_type, parent=parent_id)), parent_id)

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
