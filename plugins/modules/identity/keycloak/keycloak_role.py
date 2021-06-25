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

    - When updating a role, where possible provide the role ID to the module. This removes a lookup
      to the API to translate the name into the role ID.


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
        description:
            - Name of the role.
            - This parameter is required only when creating or updating the role.

    realm:
        type: str
        description:
            - They Keycloak realm under which this role resides.
        default: 'master'

    id:
        type: str
        description:
            - The unique identifier for this role.
            - This parameter is not required for updating or deleting a role but
              providing it will reduce the number of API calls required.

    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the role.
            - Values may be single values (e.g. a string) or a list of strings.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Adam Goossens (@adamgoossens)
'''

EXAMPLES = '''
- name: Create a Keycloak role, authentication with credentials
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

- name: Create a Keycloak role, authentication with token
  community.general.keycloak_role:
    name: my-new-kc-role
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Delete a keycloak role
  community.general.keycloak_role:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    state: absent
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak role based on name
  community.general.keycloak_role:
    name: my-role-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Update the name of a Keycloak role
  community.general.keycloak_role:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    name: an-updated-kc-role-name
    state: present
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
    name: my-new_role
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
role:
  description: Role representation of the role after module execution (sample is truncated).
  returned: always
  type: complex
  contains:
    id:
      description: GUID that identifies the role
      type: str
      returned: always
      sample: 23f38145-3195-462c-97e7-97041ccea73e
    name:
      description: Name of the role
      type: str
      returned: always
      sample: role-test-123
    description:
      description: Description of the role
      type: str
      returned: always
      sample: test role 123
    attributes:
      description: Attributes applied to this group
      type: dict
      returned: always
      sample:
        attr1: ["val1", "val2", "val3"]
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
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        client_id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        attributes=dict(type='dict'),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, role='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    clientid = module.params.get('client_id')
    state = module.params.get('state')
    name = module.params.get('name')
    attributes = module.params.get('attributes')

    before_role = None         # current state of the role, for merging.

    # does the role already exist?
    before_role = kc.get_role_by_name(name, clientid=clientid, realm=realm)
    before_role = {} if before_role is None else before_role

    # attributes in Keycloak have their values returned as lists
    # via the API. attributes is a dict, so we'll transparently convert
    # the values to lists.
    if attributes is not None:
        for key, val in module.params['attributes'].items():
            module.params['attributes'][key] = [val] if not isinstance(val, list) else val

    role_params = [x for x in module.params
                    if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'client_id'] and
                    module.params.get(x) is not None]

    # build a changeset
    changeset = {}
    for param in role_params:
        new_param_value = module.params.get(param)
        old_value = before_role[param] if param in before_role else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # prepare the new role
    updated_role = before_role.copy()
    updated_role.update(changeset)

    # if before_role is none, the role doesn't exist.
    if before_role == {}:
        if state == 'absent':
            # nothing to do.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['msg'] = 'Role does not exist; doing nothing.'
            result['role'] = dict()
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
        kc.create_role(updated_role, clientid=clientid, realm=realm)
        after_role = kc.get_role_by_name(name, clientid=clientid, realm=realm)

        result['role'] = after_role
        result['msg'] = 'Role {name} has been created'.format(name=after_role['name'])

    else:
        if state == 'present':
            # no changes
            if updated_role == before_role:
                result['changed'] = False
                result['role'] = updated_role
                result['msg'] = "No changes required to role {name}.".format(name=before_role['name'])
                module.exit_json(**result)

            # update the existing role
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_role, after=updated_role)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            kc.update_role(updated_role, clientid=clientid, realm=realm)

            after_role = kc.get_role_by_name(updated_role['name'], realm=realm)

            result['role'] = after_role
            result['msg'] = "Role {name} has been updated".format(name=after_role['name'])

            module.exit_json(**result)

        elif state == 'absent':
            result['role'] = dict()

            if module._diff:
                result['diff'] = dict(before=before_role, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete for real
            kc.delete_role(name, clientid=clientid, realm=realm)

            result['changed'] = True
            result['msg'] = "Role {name} has been deleted".format(name=before_role['name'])

            module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
