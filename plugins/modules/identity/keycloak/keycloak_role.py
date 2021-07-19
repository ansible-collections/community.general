#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Adam Goossens <adam.goossens@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_role

short_description: Allows administration of Keycloak roles via Keycloak API

version_added: 3.4.0

description:
    - This module allows you to add, remove or modify Keycloak roles via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.


options:
    state:
        description:
            - State of the role.
            - On C(present), the role will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the role will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    name:
        type: str
        required: true
        description:
            - Name of the role.
            - This parameter is required.

    description:
        type: str
        description:
            - The role description.

    realm:
        type: str
        description:
            - The Keycloak realm under which this role resides.
        default: 'master'

    client_id:
        type: str
        description:
            - If the role is a client role, the client id under which it resides.
            - If this parameter is absent, the role is considered a realm role.

    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the role.
            - Values may be single values (e.g. a string) or a list of strings.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Laurent Paumier (@laurpaum)
'''

EXAMPLES = '''
- name: Create a Keycloak realm role, authentication with credentials
  community.general.keycloak_role:
    name: my-new-kc-role
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak realm role, authentication with token
  community.general.keycloak_role:
    name: my-new-kc-role
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Create a Keycloak client role
  community.general.keycloak_role:
    name: my-new-kc-role
    realm: MyCustomRealm
    client_id: MyClient
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak role
  community.general.keycloak_role:
    name: my-role-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a keycloak role with some custom attributes
  community.general.keycloak_role:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    name: my-new-role
    attributes:
        attrib1: value1
        attrib2: value2
        attrib3:
            - with
            - numerous
            - individual
            - list
            - items
  delegate_to: localhost
'''

RETURN = '''
msg:
  description: Message as to what action was taken
  returned: always
  type: str
  sample: "Role myrole has been updated"

proposed:
    description: Role representation of proposed changes to role
    returned: always
    type: dict
    sample: {
        "description": "My updated test description"
    }
existing:
    description: Role representation of existing role
    returned: always
    type: dict
    sample: {
        "attributes": {},
        "clientRole": true,
        "composite": false,
        "containerId": "9f03eb61-a826-4771-a9fd-930e06d2d36a",
        "description": "My client test role",
        "id": "561703dd-0f38-45ff-9a5a-0c978f794547",
        "name": "myrole"
    }
end_state:
    description: Role representation of role after module execution (sample is truncated)
    returned: always
    type: dict
    sample: {
        "attributes": {},
        "clientRole": true,
        "composite": false,
        "containerId": "9f03eb61-a826-4771-a9fd-930e06d2d36a",
        "description": "My updated client test role",
        "id": "561703dd-0f38-45ff-9a5a-0c978f794547",
        "name": "myrole"
    }
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
        description=dict(type='str'),
        realm=dict(type='str', default='master'),
        client_id=dict(type='str'),
        attributes=dict(type='dict'),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    clientid = module.params.get('client_id')
    name = module.params.get('name')
    state = module.params.get('state')

    # attributes in Keycloak have their values returned as lists
    # via the API. attributes is a dict, so we'll transparently convert
    # the values to lists.
    if module.params.get('attributes') is not None:
        for key, val in module.params['attributes'].items():
            module.params['attributes'][key] = [val] if not isinstance(val, list) else val

    # convert module parameters to client representation parameters (if they belong in there)
    role_params = [x for x in module.params
                   if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'client_id', 'composites'] and
                   module.params.get(x) is not None]

    # does the role already exist?
    if clientid is None:
        before_role = kc.get_realm_role(name, realm)
    else:
        before_role = kc.get_client_role(name, clientid, realm)

    if before_role is None:
        before_role = dict()

    # build a changeset
    changeset = dict()

    for param in role_params:
        new_param_value = module.params.get(param)
        old_value = before_role[param] if param in before_role else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # prepare the new role
    updated_role = before_role.copy()
    updated_role.update(changeset)

    result['proposed'] = changeset
    result['existing'] = before_role

    # if before_role is none, the role doesn't exist.
    if before_role == dict():
        if state == 'absent':
            # nothing to do.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = dict()
            result['msg'] = 'Role does not exist; doing nothing.'
            module.exit_json(**result)

        # for 'present', create a new role.
        result['changed'] = True

        if name is None:
            module.fail_json(msg='name must be specified when creating a new role')

        if module._diff:
            result['diff'] = dict(before='', after=updated_role)

        if module.check_mode:
            module.exit_json(**result)

        # do it for real!
        if clientid is None:
            kc.create_realm_role(updated_role, realm)
            after_role = kc.get_realm_role(name, realm)
        else:
            kc.create_client_role(updated_role, clientid, realm)
            after_role = kc.get_client_role(name, clientid, realm)

        result['end_state'] = after_role

        result['msg'] = 'Role {name} has been created'.format(name=name)
        module.exit_json(**result)

    else:
        if state == 'present':
            # no changes
            if updated_role == before_role:
                result['changed'] = False
                result['end_state'] = updated_role
                result['msg'] = "No changes required to role {name}.".format(name=name)
                module.exit_json(**result)

            # update the existing role
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_role, after=updated_role)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            if clientid is None:
                kc.update_realm_role(updated_role, realm)
                after_role = kc.get_realm_role(name, realm)
            else:
                kc.update_client_role(updated_role, clientid, realm)
                after_role = kc.get_client_role(name, clientid, realm)

            result['end_state'] = after_role

            result['msg'] = "Role {name} has been updated".format(name=name)
            module.exit_json(**result)

        elif state == 'absent':
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_role, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete for real
            if clientid is None:
                kc.delete_realm_role(name, realm)
            else:
                kc.delete_client_role(name, clientid, realm)

            result['end_state'] = dict()

            result['msg'] = "Role {name} has been deleted".format(name=name)
            module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
