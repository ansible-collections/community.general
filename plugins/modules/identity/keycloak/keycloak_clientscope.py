#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_clientscope

short_description: Allows administration of Keycloak client_scopes via Keycloak API

description:
    - This module allows you to add, remove or modify Keycloak client_scopes via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/8.0/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When updating a group, where possible provide the group ID to the module. This removes a lookup
      to the API to translate the name into the group ID.


options:
    state:
        description:
            - State of the client_scope.
            - On C(present), the group will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the group will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    name:
        type: str
        description:
            - Name of the client_scope.
            - This parameter is required only when creating or updating the client_scope.

    realm:
        type: str
        description:
            - They Keycloak realm under which this group resides.
        default: 'master'

    id:
        type: str
        description:
            - The unique identifier for this client_scope.
            - This parameter is not required for updating or deleting a client_scope but
              providing it will reduce the number of API calls required.
    
    description:
        type: str
        description:
            - Description for this client_scope.
            - This parameter is not required for updating or deleting a client_scope.
    
    protocol:
        type: str
        description:
            - Protocol for this client_scope.
            - When you are creating the client scope, you must choose the Protocol.
              Only the clients which use same protocol can then be linked with this client scope.

    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the client_scope.
            - Values may be single values (e.g. a string) or a list of strings.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Gaëtan Daubresse (@Gaetan2907)
'''

EXAMPLES = '''
- name: Create a Keycloak client_scopes, authentication with credentials
  community.general.keycloak_clientscope:
    name: my-new-kc-clientscope
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak client_scopes, authentication with token
  community.general.keycloak_clientscope:
    name: my-new-kc-clientscope
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Delete a keycloak client_scopes
  community.general.keycloak_clientscope:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    state: absent
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak client_scope based on name
  community.general.keycloak_clientscope:
    name: my-clientscope-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Update the name of a Keycloak client_scope
  community.general.keycloak_clientscope:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    name: an-updated-kc-clientscope-name
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a Keycloak client_scope with some custom attributes
  community.general.keycloak_clientscope:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    name: my-new_clientscope
    description: description-of-clientscope
    protocol: openid-connect
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
  sample: "Client_scope testclientscope has been updated"

proposed:
    description: client_scope representation of proposed changes to client_scope
    returned: always
    type: dict
    sample: {
      clientId: "test"
    }
existing:
    description: client_scope representation of existing client_scope (sample is truncated)
    returned: always
    type: dict
    sample: {
        "adminUrl": "http://www.example.com/admin_url",
        "attributes": {
            "request.object.signature.alg": "RS256",
        }
    }
end_state:
    description: client_scope representation of client_scope after module execution (sample is truncated)
    returned: always
    type: dict
    sample: {
        "adminUrl": "http://www.example.com/admin_url",
        "attributes": {
            "request.object.signature.alg": "RS256",
        }
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
        state=dict(default='present', choices=['present', 'absent']),
        realm=dict(default='master'),
        id=dict(type='str'),
        name=dict(type='str'),
        description=dict(type='str'),
        protocol=dict(type='str'),
        attributes=dict(type='dict'),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, group='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    gid = module.params.get('id')
    name = module.params.get('name')
    attributes = module.params.get('attributes')

    before_clientscope = None         # current state of the group, for merging.

    # does the group already exist?
    if gid is None:
        before_clientscope = kc.get_clientscope_by_name(name, realm=realm)
    else:
        before_clientscope = kc.get_clientscope_by_clientscopeid(gid, realm=realm)

    before_clientscope = {} if before_clientscope is None else before_clientscope

    # attributes in Keycloak have their values returned as lists
    # via the API. attributes is a dict, so we'll transparently convert
    # the values to lists.
    if attributes is not None:
        for key, val in module.params['attributes'].items():
            module.params['attributes'][key] = [val] if not isinstance(val, list) else val

    clientscope_params = [x for x in module.params
                          if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm'] and
                          module.params.get(x) is not None]

    # build a changeset
    changeset = {}
    for param in clientscope_params:
        new_param_value = module.params.get(param)
        old_value = before_clientscope[param] if param in before_clientscope else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # prepare the new group
    updated_clientscope = before_clientscope.copy()
    updated_clientscope.update(changeset)

    # if before_clientscope is none, the group doesn't exist.
    if before_clientscope == {}:
        if state == 'absent':
            # nothing to do.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['msg'] = 'Clientscope does not exist; doing nothing.'
            result['group'] = dict()
            module.exit_json(**result)

        # for 'present', create a new group.
        result['changed'] = True
        if name is None:
            module.fail_json(msg='name must be specified when creating a new group')

        if module._diff:
            result['diff'] = dict(before='', after=updated_clientscope)

        if module.check_mode:
            module.exit_json(**result)

        # do it for real!
        kc.create_clientscope(updated_clientscope, realm=realm)
        after_clientscope = kc.get_clientscope_by_name(name, realm)

        result['group'] = after_clientscope
        result['msg'] = 'Clientscope {name} has been created with ID {id}'.format(name=after_clientscope['name'],
                                                                                  id=after_clientscope['id'])

    else:
        if state == 'present':
            # no changes
            if updated_clientscope == before_clientscope:
                result['changed'] = False
                result['group'] = updated_clientscope
                result['msg'] = "No changes required to clientscope {name}.".format(name=before_clientscope['name'])
                module.exit_json(**result)

            # update the existing group
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_clientscope, after=updated_clientscope)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            kc.update_clientscope(updated_clientscope, realm=realm)

            after_clientscope = kc.get_clientscope_by_clientscopeid(updated_clientscope['id'], realm=realm)

            result['group'] = after_clientscope
            result['msg'] = "Group {id} has been updated".format(id=after_clientscope['id'])

            module.exit_json(**result)

        elif state == 'absent':
            result['group'] = dict()

            if module._diff:
                result['diff'] = dict(before=before_clientscope, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete for real
            cid = before_clientscope['id']
            kc.delete_clientscope(cid=cid, realm=realm)

            result['changed'] = True
            result['msg'] = "Clientscope {name} has been deleted".format(name=before_clientscope['name'])

            module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
