#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_component_info

short_description: Retrieve component info in Keycloak

version_added: 8.2.0

description:
  - This module retrieve information on component from Keycloak.
attributes:
  action_group:
    version_added: 10.2.0

options:
  realm:
    description:
      - The name of the realm.
    required: true
    type: str
  name:
    description:
      - Name of the Component.
    type: str
  provider_type:
    description:
      - Provider type of components.
      - 'Examples: V(org.keycloak.storage.UserStorageProvider), V(org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy),
        V(org.keycloak.keys.KeyProvider), V(org.keycloak.userprofile.UserProfileProvider), V(org.keycloak.storage.ldap.mappers.LDAPStorageMapper).'
    type: str
  parent_id:
    description:
      - Container ID of the components.
    type: str


extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes
  - community.general.attributes.info_module

author:
  - Andre Desrosiers (@desand01)
"""

EXAMPLES = r"""
- name: Retrive info of a UserStorageProvider named myldap
  community.general.keycloak_component_info:
    auth_keycloak_url: http://localhost:8080/auth
    auth_sername: admin
    auth_password: password
    auth_realm: master
    realm: myrealm
    name: myldap
    provider_type: org.keycloak.storage.UserStorageProvider

- name: Retrive key info component
  community.general.keycloak_component_info:
    auth_keycloak_url: http://localhost:8080/auth
    auth_sername: admin
    auth_password: password
    auth_realm: master
    realm: myrealm
    name: rsa-enc-generated
    provider_type: org.keycloak.keys.KeyProvider

- name: Retrive all component from realm master
  community.general.keycloak_component_info:
    auth_keycloak_url: http://localhost:8080/auth
    auth_sername: admin
    auth_password: password
    auth_realm: master
    realm: myrealm

- name: Retrive all sub components of parent component filter by type
  community.general.keycloak_component_info:
    auth_keycloak_url: http://localhost:8080/auth
    auth_sername: admin
    auth_password: password
    auth_realm: master
    realm: myrealm
    parent_id: "075ef2fa-19fc-4a6d-bf4c-249f57365fd2"
    provider_type: "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
"""

RETURN = r"""
components:
  description: JSON representation of components.
  returned: always
  type: list
  elements: dict
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    meta_args = dict(
        name=dict(type='str'),
        realm=dict(type='str', required=True),
        parent_id=dict(type='str'),
        provider_type=dict(type='str'),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = dict(changed=False, components=[])

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    parentId = module.params.get('parent_id')
    name = module.params.get('name')
    providerType = module.params.get('provider_type')

    objRealm = kc.get_realm_by_id(realm)
    if not objRealm:
        module.fail_json(msg="Failed to retrive realm '{realm}'".format(realm=realm))

    filters = []

    if parentId:
        filters.append("parent=%s" % (quote(parentId, safe='')))
    else:
        filters.append("parent=%s" % (quote(objRealm['id'], safe='')))

    if name:
        filters.append("name=%s" % (quote(name, safe='')))
    if providerType:
        filters.append("type=%s" % (quote(providerType, safe='')))

    result['components'] = kc.get_components(filter="&".join(filters), realm=realm)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
