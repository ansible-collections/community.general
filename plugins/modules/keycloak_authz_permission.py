#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# Copyright (c) 2021, Christophe Gilles <christophe.gilles54@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_authz_permission

version_added: 7.2.0

short_description: Allows administration of Keycloak client authorization permissions via Keycloak API

description:
    - This module allows the administration of Keycloak client authorization permissions via the Keycloak REST
      API. Authorization permissions are only available if a client has Authorization enabled.

    - There are some peculiarities in JSON paths and payloads for authorization permissions. In particular
      POST and PUT operations are targeted at permission endpoints, whereas GET requests go to policies
      endpoint. To make matters more interesting the JSON responses from GET requests return data in a
      different format than what is expected for POST and PUT. The end result is that it is not possible to
      detect changes to things like policies, scopes or resources - at least not without a large number of
      additional API calls. Therefore this module always updates authorization permissions instead of
      attempting to determine if changes are truly needed.

    - This module requires access to the REST API via OpenID Connect; the user connecting and the realm
      being used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate realm definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase options used by Keycloak.
      The Authorization Services paths and payloads have not officially been documented by the Keycloak project.
      U(https://www.puppeteers.net/blog/keycloak-authorization-services-rest-api-paths-and-payload/)

attributes:
    check_mode:
        support: full
    diff_mode:
        support: none

options:
    state:
        description:
            - State of the authorization permission.
            - On V(present), the authorization permission will be created (or updated if it exists already).
            - On V(absent), the authorization permission will be removed if it exists.
        choices: ['present', 'absent']
        default: 'present'
        type: str
    name:
        description:
            - Name of the authorization permission to create.
        type: str
        required: true
    description:
        description:
            - The description of the authorization permission.
        type: str
        required: false
    permission_type:
        description:
            - The type of authorization permission.
            - On V(scope) create a scope-based permission.
            - On V(resource) create a resource-based permission.
        type: str
        required: true
        choices:
            - resource
            - scope
    decision_strategy:
        description:
            - The decision strategy to use with this permission.
        type: str
        default: UNANIMOUS
        required: false
        choices:
            - UNANIMOUS
            - AFFIRMATIVE
            - CONSENSUS
    resources:
        description:
            - Resource names to attach to this permission.
            - Scope-based permissions can only include one resource.
            - Resource-based permissions can include multiple resources.
        type: list
        elements: str
        default: []
        required: false
    scopes:
        description:
            - Scope names to attach to this permission.
            - Resource-based permissions cannot have scopes attached to them.
        type: list
        elements: str
        default: []
        required: false
    policies:
        description:
            - Policy names to attach to this permission.
        type: list
        elements: str
        default: []
        required: false
    client_id:
        description:
            - The clientId of the keycloak client that should have the authorization scope.
            - This is usually a human-readable name of the Keycloak client.
        type: str
        required: true
    realm:
        description:
            - The name of the Keycloak realm the Keycloak client is in.
        type: str
        required: true

extends_documentation_fragment:
    - community.general.keycloak
    - community.general.attributes

author:
    - Samuli Seppänen (@mattock)
'''

EXAMPLES = '''
- name: Manage scope-based Keycloak authorization permission
  community.general.keycloak_authz_permission:
    name: ScopePermission
    state: present
    description: Scope permission
    permission_type: scope
    scopes:
      - file:delete
    policies:
      - Default Policy
    client_id: myclient
    realm: myrealm
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master

- name: Manage resource-based Keycloak authorization permission
  community.general.keycloak_authz_permission:
    name: ResourcePermission
    state: present
    description: Resource permission
    permission_type: resource
    resources:
      - Default Resource
    policies:
      - Default Policy
    client_id: myclient
    realm: myrealm
    auth_keycloak_url: http://localhost:8080/auth
    auth_username: keycloak
    auth_password: keycloak
    auth_realm: master
'''

RETURN = '''
msg:
    description: Message as to what action was taken.
    returned: always
    type: str

end_state:
    description: Representation of the authorization permission after module execution.
    returned: on success
    type: complex
    contains:
        id:
            description: ID of the authorization permission.
            type: str
            returned: when O(state=present)
            sample: 9da05cd2-b273-4354-bbd8-0c133918a454
        name:
            description: Name of the authorization permission.
            type: str
            returned: when O(state=present)
            sample: ResourcePermission
        description:
            description: Description of the authorization permission.
            type: str
            returned: when O(state=present)
            sample: Resource Permission
        type:
            description: Type of the authorization permission.
            type: str
            returned: when O(state=present)
            sample: resource
        decisionStrategy:
            description: The decision strategy to use.
            type: str
            returned: when O(state=present)
            sample: UNANIMOUS
        logic:
            description: The logic used for the permission (part of the payload, but has a fixed value).
            type: str
            returned: when O(state=present)
            sample: POSITIVE
        resources:
            description: IDs of resources attached to this permission.
            type: list
            returned: when O(state=present)
            sample:
                - 49e052ff-100d-4b79-a9dd-52669ed3c11d
        scopes:
            description: IDs of scopes attached to this permission.
            type: list
            returned: when O(state=present)
            sample:
                - 9da05cd2-b273-4354-bbd8-0c133918a454
        policies:
            description: IDs of policies attached to this permission.
            type: list
            returned: when O(state=present)
            sample:
                - 9da05cd2-b273-4354-bbd8-0c133918a454
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        state=dict(type='str', default='present',
                   choices=['present', 'absent']),
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
        permission_type=dict(type='str', choices=['scope', 'resource'], required=True),
        decision_strategy=dict(type='str', default='UNANIMOUS',
                               choices=['UNANIMOUS', 'AFFIRMATIVE', 'CONSENSUS']),
        resources=dict(type='list', elements='str', default=[], required=False),
        scopes=dict(type='list', elements='str', default=[], required=False),
        policies=dict(type='list', elements='str', default=[], required=False),
        client_id=dict(type='str', required=True),
        realm=dict(type='str', required=True)
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=(
                               [['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    # Convenience variables
    state = module.params.get('state')
    name = module.params.get('name')
    description = module.params.get('description')
    permission_type = module.params.get('permission_type')
    decision_strategy = module.params.get('decision_strategy')
    realm = module.params.get('realm')
    client_id = module.params.get('client_id')
    realm = module.params.get('realm')
    resources = module.params.get('resources')
    scopes = module.params.get('scopes')
    policies = module.params.get('policies')

    if permission_type == 'scope' and state == 'present':
        if scopes == []:
            module.fail_json(msg='Scopes need to defined when permission type is set to scope!')
        if len(resources) > 1:
            module.fail_json(msg='Only one resource can be defined for a scope permission!')

    if permission_type == 'resource' and state == 'present':
        if resources == []:
            module.fail_json(msg='A resource need to defined when permission type is set to resource!')
        if scopes != []:
            module.fail_json(msg='Scopes cannot be defined when permission type is set to resource!')

    result = dict(changed=False, msg='', end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    # Get id of the client based on client_id
    cid = kc.get_client_id(client_id, realm=realm)
    if not cid:
        module.fail_json(msg='Invalid client %s for realm %s' %
                         (client_id, realm))

    # Get current state of the permission using its name as the search
    # filter. This returns False if it is not found.
    permission = kc.get_authz_permission_by_name(
        name=name, client_id=cid, realm=realm)

    # Generate a JSON payload for Keycloak Admin API. This is needed for
    # "create" and "update" operations.
    payload = {}
    payload['name'] = name
    payload['description'] = description
    payload['type'] = permission_type
    payload['decisionStrategy'] = decision_strategy
    payload['logic'] = 'POSITIVE'
    payload['scopes'] = []
    payload['resources'] = []
    payload['policies'] = []

    if permission_type == 'scope':
        # Add the resource id, if any, to the payload. While the data type is a
        # list, it is only possible to have one entry in it based on what Keycloak
        # Admin Console does.
        r = False
        resource_scopes = []

        if resources:
            r = kc.get_authz_resource_by_name(resources[0], cid, realm)
            if not r:
                module.fail_json(msg='Unable to find authorization resource with name %s for client %s in realm %s' % (resources[0], cid, realm))
            else:
                payload['resources'].append(r['_id'])

            for rs in r['scopes']:
                resource_scopes.append(rs['id'])

        # Generate a list of scope ids based on scope names. Fail if the
        # defined resource does not include all those scopes.
        for scope in scopes:
            s = kc.get_authz_authorization_scope_by_name(scope, cid, realm)
            if r and not s['id'] in resource_scopes:
                module.fail_json(msg='Resource %s does not include scope %s for client %s in realm %s' % (resources[0], scope, client_id, realm))
            else:
                payload['scopes'].append(s['id'])

    elif permission_type == 'resource':
        if resources:
            for resource in resources:
                r = kc.get_authz_resource_by_name(resource, cid, realm)
                if not r:
                    module.fail_json(msg='Unable to find authorization resource with name %s for client %s in realm %s' % (resource, cid, realm))
                else:
                    payload['resources'].append(r['_id'])

    # Add policy ids, if any, to the payload.
    if policies:
        for policy in policies:
            p = kc.get_authz_policy_by_name(policy, cid, realm)

            if p:
                payload['policies'].append(p['id'])
            else:
                module.fail_json(msg='Unable to find authorization policy with name %s for client %s in realm %s' % (policy, client_id, realm))

    # Add "id" to payload for update operations
    if permission:
        payload['id'] = permission['id']

        # Handle the special case where the user attempts to change an already
        # existing permission's type - something that can't be done without a
        # full delete -> (re)create cycle.
        if permission['type'] != payload['type']:
            module.fail_json(msg='Modifying the type of permission (scope/resource) is not supported: \
                                  permission %s of client %s in realm %s unchanged' % (permission['id'], cid, realm))

    # Updating an authorization  permission is tricky for several reasons.
    # Firstly, the current permission is retrieved using a _policy_ endpoint,
    # not from a permission endpoint. Also, the data that is returned is in a
    # different format than what is expected by the payload. So, comparing the
    # current state attribute by attribute to the payload is not possible.  For
    # example the data contains a JSON object "config" which may contain the
    # authorization type, but which is no required in the payload.  Moreover,
    # information about resources, scopes and policies is _not_ present in the
    # data. So, there is no way to determine if any of those fields have
    # changed. Therefore the best options we have are
    #
    # a) Always apply the payload without checking the current state
    # b) Refuse to make any changes to any settings (only support create and delete)
    #
    # The approach taken here is a).
    #
    if permission and state == 'present':
        if module.check_mode:
            result['msg'] = 'Notice: unable to check current resources, scopes and policies for permission. \
                            Would apply desired state without checking the current state.'
        else:
            kc.update_authz_permission(payload=payload, permission_type=permission_type, id=permission['id'], client_id=cid, realm=realm)
            result['msg'] = 'Notice: unable to check current resources, scopes and policies for permission. \
                            Applying desired state without checking the current state.'

        # Assume that something changed, although we don't know if that is the case.
        result['changed'] = True
        result['end_state'] = payload
    elif not permission and state == 'present':
        if module.check_mode:
            result['msg'] = 'Would create permission'
        else:
            kc.create_authz_permission(payload=payload, permission_type=permission_type, client_id=cid, realm=realm)
            result['msg'] = 'Permission created'

        result['changed'] = True
        result['end_state'] = payload
    elif permission and state == 'absent':
        if module.check_mode:
            result['msg'] = 'Would remove permission'
        else:
            kc.remove_authz_permission(id=permission['id'], client_id=cid, realm=realm)
            result['msg'] = 'Permission removed'

        result['changed'] = True

    elif not permission and state == 'absent':
        result['changed'] = False
    else:
        module.fail_json(msg='Unable to determine what to do with permission %s of client %s in realm %s' % (
            name, client_id, realm))

    module.exit_json(**result)


if __name__ == '__main__':
    main()
