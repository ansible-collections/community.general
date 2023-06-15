#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Adam Goossens <adam.goossens@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_group

short_description: Allows administration of Keycloak groups via Keycloak API

description:
    - This module allows you to add, remove or modify Keycloak groups via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/20.0.2/rest-api/index.html).

    - Attributes are multi-valued in the Keycloak API. All attributes are lists of individual values and will
      be returned that way by this module. You may pass single values for attributes when calling the module,
      and this will be translated into a list suitable for the API.

    - When updating a group, where possible provide the group ID to the module. This removes a lookup
      to the API to translate the name into the group ID.

attributes:
    check_mode:
        support: full
    diff_mode:
        support: full

options:
    state:
        description:
            - State of the group.
            - On V(present), the group will be created if it does not yet exist, or updated with the parameters you provide.
            - >-
              On V(absent), the group will be removed if it exists. Be aware that absenting
              a group with subgroups will automatically delete all its subgroups too.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    name:
        type: str
        description:
            - Name of the group.
            - This parameter is required only when creating or updating the group.

    realm:
        type: str
        description:
            - They Keycloak realm under which this group resides.
        default: 'master'

    id:
        type: str
        description:
            - The unique identifier for this group.
            - This parameter is not required for updating or deleting a group but
              providing it will reduce the number of API calls required.

    attributes:
        type: dict
        description:
            - A dict of key/value pairs to set as custom attributes for the group.
            - Values may be single values (e.g. a string) or a list of strings.

    parents:
        version_added: "6.4.0"
        type: list
        description:
            - List of parent groups for the group to handle sorted top to bottom.
            - >-
              Set this to create a group as a subgroup of another group or groups (parents) or
              when accessing an existing subgroup by name.
            - >-
              Not necessary to set when accessing an existing subgroup by its C(ID) because in
              that case the group can be directly queried without necessarily knowing its parent(s).
        elements: dict
        suboptions:
          id:
            type: str
            description:
              - Identify parent by ID.
              - Needs less API calls than using O(parents[].name).
              - A deep parent chain can be started at any point when first given parent is given as ID.
              - Note that in principle both ID and name can be specified at the same time
                but current implementation only always use just one of them, with ID
                being preferred.
          name:
            type: str
            description:
              - Identify parent by name.
              - Needs more internal API calls than using O(parents[].id) to map names to ID's under the hood.
              - When giving a parent chain with only names it must be complete up to the top.
              - Note that in principle both ID and name can be specified at the same time
                but current implementation only always use just one of them, with ID
                being preferred.

notes:
    - Presently, the RV(end_state.realmRoles), RV(end_state.clientRoles), and RV(end_state.access) attributes returned by the Keycloak API
      are read-only for groups. This limitation will be removed in a later version of this module.

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
    - Adam Goossens (@adamgoossens)
'''

EXAMPLES = '''
- name: Create a Keycloak group, authentication with credentials
  community.general.keycloak_group:
    name: my-new-kc-group
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  register: result_new_kcgrp
  delegate_to: localhost

- name: Create a Keycloak group, authentication with token
  community.general.keycloak_group:
    name: my-new-kc-group
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost

- name: Delete a keycloak group
  community.general.keycloak_group:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    state: absent
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Delete a Keycloak group based on name
  community.general.keycloak_group:
    name: my-group-for-deletion
    state: absent
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Update the name of a Keycloak group
  community.general.keycloak_group:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    name: an-updated-kc-group-name
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost

- name: Create a keycloak group with some custom attributes
  community.general.keycloak_group:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    name: my-new_group
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

- name: Create a Keycloak subgroup of a base group (using parent name)
  community.general.keycloak_group:
    name: my-new-kc-group-sub
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parents:
      - name: my-new-kc-group
  register: result_new_kcgrp_sub
  delegate_to: localhost

- name: Create a Keycloak subgroup of a base group (using parent id)
  community.general.keycloak_group:
    name: my-new-kc-group-sub2
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parents:
      - id: "{{ result_new_kcgrp.end_state.id }}"
  delegate_to: localhost

- name: Create a Keycloak subgroup of a subgroup (using parent names)
  community.general.keycloak_group:
    name: my-new-kc-group-sub-sub
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parents:
      - name: my-new-kc-group
      - name: my-new-kc-group-sub
  delegate_to: localhost

- name: Create a Keycloak subgroup of a subgroup (using direct parent id)
  community.general.keycloak_group:
    name: my-new-kc-group-sub-sub
    realm: MyCustomRealm
    state: present
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
    parents:
      - id: "{{ result_new_kcgrp_sub.end_state.id }}"
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
        attributes:
            description: Attributes applied to this group.
            type: dict
            returned: always
            sample:
                attr1: ["val1", "val2", "val3"]
        path:
            description: URI path to the group.
            type: str
            returned: always
            sample: /grp-test-123
        realmRoles:
            description: An array of the realm-level roles granted to this group.
            type: list
            returned: always
            sample: []
        subGroups:
            description: A list of groups that are children of this group. These groups will have the same parameters as
                         documented here.
            type: list
            returned: always
        clientRoles:
            description: A list of client-level roles granted to this group.
            type: list
            returned: always
            sample: []
        access:
            description: A dict describing the accesses you have to this group based on the credentials used.
            type: dict
            returned: always
            sample:
                manage: true
                manageMembership: true
                view: true
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
        attributes=dict(type='dict'),
        parents=dict(
            type='list', elements='dict',
            options=dict(
                id=dict(type='str'),
                name=dict(type='str')
            ),
        ),
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

    parents = module.params.get('parents')

    # attributes in Keycloak have their values returned as lists
    # via the API. attributes is a dict, so we'll transparently convert
    # the values to lists.
    if attributes is not None:
        for key, val in module.params['attributes'].items():
            module.params['attributes'][key] = [val] if not isinstance(val, list) else val

    # Filter and map the parameters names that apply to the group
    group_params = [x for x in module.params
                    if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'parents'] and
                    module.params.get(x) is not None]

    # See if it already exists in Keycloak
    if gid is None:
        before_group = kc.get_group_by_name(name, realm=realm, parents=parents)
    else:
        before_group = kc.get_group_by_groupid(gid, realm=realm)

    if before_group is None:
        before_group = {}

    # Build a proposed changeset from parameters given to this module
    changeset = {}

    for param in group_params:
        new_param_value = module.params.get(param)
        old_value = before_group[param] if param in before_group else None
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # Prepare the desired values using the existing values (non-existence results in a dict that is save to use as a basis)
    desired_group = before_group.copy()
    desired_group.update(changeset)

    # Cater for when it doesn't exist (an empty dict)
    if not before_group:
        if state == 'absent':
            # Do nothing and exit
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = {}
            result['msg'] = 'Group does not exist; doing nothing.'
            module.exit_json(**result)

        # Process a creation
        result['changed'] = True

        if name is None:
            module.fail_json(msg='name must be specified when creating a new group')

        if module._diff:
            result['diff'] = dict(before='', after=desired_group)

        if module.check_mode:
            module.exit_json(**result)

        # create it ...
        if parents:
            # ... as subgroup of another parent group
            kc.create_subgroup(parents, desired_group, realm=realm)
        else:
            # ... as toplvl base group
            kc.create_group(desired_group, realm=realm)

        after_group = kc.get_group_by_name(name, realm, parents=parents)

        result['end_state'] = after_group

        result['msg'] = 'Group {name} has been created with ID {id}'.format(name=after_group['name'],
                                                                            id=after_group['id'])
        module.exit_json(**result)

    else:
        if state == 'present':
            # Process an update

            # no changes
            if desired_group == before_group:
                result['changed'] = False
                result['end_state'] = desired_group
                result['msg'] = "No changes required to group {name}.".format(name=before_group['name'])
                module.exit_json(**result)

            # doing an update
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_group, after=desired_group)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            kc.update_group(desired_group, realm=realm)

            after_group = kc.get_group_by_groupid(desired_group['id'], realm=realm)

            result['end_state'] = after_group

            result['msg'] = "Group {id} has been updated".format(id=after_group['id'])
            module.exit_json(**result)

        else:
            # Process a deletion (because state was not 'present')
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_group, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete it
            gid = before_group['id']
            kc.delete_group(groupid=gid, realm=realm)

            result['end_state'] = {}

            result['msg'] = "Group {name} has been deleted".format(name=before_group['name'])

    module.exit_json(**result)


if __name__ == '__main__':
    main()
