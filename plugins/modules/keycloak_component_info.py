#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, INSPQ <philippe.gauthier@inspq.qc.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: keycloak_component_info

short_description: Retrive component info in Keycloak.

description:
    - This module retrive information on component from Keycloak.
options:
    realm:
        description:
            - The name of the realm.
        required: true
        type: str
    name:
        description:
            - Name of the Component
        type: str
    provider_type:
        description:
            - Provider type of components
        choices:
            - org.keycloak.storage.UserStorageProvider
            - org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy
            - org.keycloak.keys.KeyProvider
            - authenticatorConfig
            - requiredActions
        type: str
    parent_id:
        description:
            - Container Id of the components
        type: str
    sub_provider_type:
        description:
            - Type of sub components
            - Only effective when O(parent_id) is provided
        type: str


extends_documentation_fragment:
    - keycloak

author:
    - Andre Desrosiers (@desand01)
'''

EXAMPLES = '''
    - name: Retrive info for ldap component
      community.general.keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: ActiveDirectory
        provider_type: org.keycloak.storage.UserStorageProvider

    - name: Retrive key info component
      community.general.keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: rsa-enc-generated
        provider_type: org.keycloak.keys.KeyProvider

    - name: Retrive all component from realm master
      community.general.keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master

    - name: Retrive all sub components of parent component filter by type
      community.general.keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        parent_id: "075ef2fa-19fc-4a6d-bf4c-249f57365fd2"
        sub_provider_type: "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
        

'''

RETURN = '''
component:
  description: JSON representation for the component.
  returned: on success
  type: dict
subComponents:
  description: JSON representation of the sub components list.
  returned: on success
  type: list
changed:
  description: Always return False.
  returned: always
  type: bool
'''

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
        provider_type=dict(
            choices=[
                "org.keycloak.storage.UserStorageProvider",
                "org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy",
                "org.keycloak.keys.KeyProvider",
                "authenticatorConfig",
                "requiredActions"]
        ),
        sub_provider_type=dict(type='str'),
    )

    argument_spec.update(meta_args)

    mutually_exclusive = [["parent_id","provider_type"],["provider_type","sub_provider_type"]]
    module = AnsibleModule(argument_spec=argument_spec,
                           mutually_exclusive=mutually_exclusive,
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
    subProviderType = module.params.get('sub_provider_type')

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
        filters.append("type=%s" % (providerType))
    if subProviderType:
        if parentId:
            filters.append("type=%s" % (subProviderType))
        else:
            module.warn('The parameter sub_provider_type is ignored when parent_id is omitted.')
    
    result['components'] = kc.get_components(filter="&".join(filters), realm=realm)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
