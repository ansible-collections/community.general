#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Adam Goossens <adam.goossens@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_subgroup

short_description: Allows set or create subgroup via Keycloak API

description:
    - This module allows you to set or create subgroup under Keycloak groups via the Keycloak REST API.
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
    realm:
        type: str
        description:
            - They Keycloak realm under which this group resides.
        default: 'master'
    parent_id:
        type: str
        description:
            - The unique identifier for parent group.
            - This parameter is not required for set or create child of a group but
              providing it will reduce the number of API calls required.
    parent_name:
        type: str
        description:
            - Name of the parent group.
    id:
        type: str
        description:
            - The unique identifier for the subgroup.
            - This parameter is not required for setting a subgroup but
              providing it will reduce the number of API calls required.
    name:
        type: str
        description:
            - Name of the subgroup.

extends_documentation_fragment:
- community.general.keycloak


author:
    - Fynn Chen (@fynncfchen)
'''

EXAMPLES = '''
- name: Set a Keycloak subgroup to parent, authentication with credentials
  community.general.keycloak_subgroup:
    parent_name: my-new-kc-group
    id: deafb7ef-5d3d-4ee2-8fa2-4f5169c0936a
    name: my-subgroup
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost
- name: Create a Keycloak subgroup, authentication with token
  community.general.keycloak_subgroup:
    parent_name: my-new-kc-group
    name: my-subgroup
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Representation of the group after module execution (sample is truncated).
    returned: on success
    type: complex
    contains:
        id:
            description: GUID that identifies the group.
            type: str
            returned: always
            sample: 23f38145-3195-462c-97e7-97041ccea73e
        name:
            description: Name of the group.
            type: str
            returned: always
            sample: grp-test-123
        path:
            description: URI path to the group.
            type: str
            returned: always
            sample: /parent/grp-test-123
        attributes:
            description: Attributes applied to this group.
            type: dict
            returned: always
            sample:
                attr1: ["val1", "val2", "val3"]
        realmRoles:
            description: An array of the realm-level roles granted to this group.
            type: list
            returned: always
            sample: []
        clientRoles:
            description: A list of client-level roles granted to this group.
            type: list
            returned: always
            sample: []
        subGroups:
            description: A list of groups that are children of this group. These groups will have the same parameters as
                         documented here.
            type: list
            returned: always

subgroup:
    description:
        - Representation of the group after module execution.
        - Deprecated return value, it will be removed in community.general 6.0.0. Please use the return value I(end_state) instead.
    returned: always
    type: complex
    contains:
        id:
            description: GUID that identifies the group.
            type: str
            returned: always
            sample: 23f38145-3195-462c-97e7-97041ccea73e
        name:
            description: Name of the group.
            type: str
            returned: always
            sample: grp-test-123
        path:
            description: URI path to the group.
            type: str
            returned: always
            sample: /parent/grp-test-123
        attributes:
            description: Attributes applied to this group.
            type: dict
            returned: always
            sample:
                attr1: ["val1", "val2", "val3"]
        realmRoles:
            description: An array of the realm-level roles granted to this group.
            type: list
            returned: always
            sample: []
        clientRoles:
            description: A list of client-level roles granted to this group.
            type: list
            returned: always
            sample: []
        subGroups:
            description: A list of groups that are children of this group. These groups will have the same parameters as
                          documented here.
            type: list
            returned: always

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
        realm=dict(default='master'),
        parent_id=dict(type='str'),
        parent_name=dict(type='str'),
        id=dict(type='str'),
        name=dict(type='str', required=True),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['parent_id', 'parent_name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, subgroup='')

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    parent_id = module.params.get('parent_id')
    parent_name = module.params.get('parent_name')
    id = module.params.get('id')
    name = module.params.get('name')

    # Filter and map the parameters names that apply to the subgroup
    subgroup_params = [x for x in module.params
                    if x not in list(keycloak_argument_spec().keys()) + ['realm', 'parent_id', 'parent_name'] and
                    module.params.get(x) is not None]

    # See if parent exists in Keycloak
    if parent_id is None:
        parent_group = kc.get_group_by_name(parent_name, realm=realm)

        if parent_group is None:
            module.fail_json(msg='Parent group not found {parent_name}'.format(parent_name=parent_name))

        parent_id = parent_group['id']

    # See if it already exists in Keycloak
    if id is None:
        before_subgroup = kc.get_group_by_name(name, realm=realm)
    else:
        before_subgroup = kc.get_group_by_groupid(id, realm=realm)

    desired_subgroup = {}

    if before_subgroup is None:
        for param in subgroup_params:
            desired_subgroup[camel(param)] = module.params.get(param)
    else:
        desired_subgroup.update(before_subgroup)

    if before_subgroup:
        # set to parent
        kc.create_subgroup(parent_id=parent_id, grouprep=desired_subgroup, realm=realm)
        after_subgroup = kc.get_group_by_groupid(before_subgroup['id'], realm=realm)

        result['end_state'] = after_subgroup
        result['subgroup'] = result['end_state']
        result['msg'] = 'Subgroup {name} has been set to path {path}'.format(name=after_subgroup['name'],
                                                                             path=after_subgroup['path'])
        module.exit_json(**result)
    else:
        # create it
        kc.create_subgroup(parent_id=parent_id, grouprep=desired_subgroup, realm=realm)
        after_subgroup = kc.get_group_by_name(desired_subgroup['name'], realm=realm)

        result['end_state'] = after_subgroup
        result['subgroup'] = result['end_state']
        result['msg'] = 'Subgroup {name} has been created with path {path}'.format(name=after_subgroup['name'],
                                                                                   path=after_subgroup['path'])
        module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
