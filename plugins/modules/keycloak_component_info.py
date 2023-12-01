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

version_added: "8.0.2"

description:
    - This module retrive information on component from Keycloak.
options:
    realm:
        description:
            - The name of the realm in which is the component.
        required: true
        type: str
    name:
        description:
            - Name of the Component
        required: true
        type: str
    providerType:
        description:
            - Provider type of component
        choices:
            - org.keycloak.storage.UserStorageProvider
            - org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy
            - org.keycloak.keys.KeyProvider
            - authenticatorConfig
            - requiredActions
        required: true
        type: str


extends_documentation_fragment:
    - keycloak

author:
    - Philippe Gauthier (@elfelip)
    - Andre Desrosiers (@desand01)
'''

EXAMPLES = '''
    - name: Retrive info for ldap component
      keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: ActiveDirectory
        providerType: org.keycloak.storage.UserStorageProvider

    - name: Retrive key info component
      keycloak_component_info:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: rsa-enc-generated
        providerType: org.keycloak.keys.KeyProvider


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
        name=dict(type='str', required=True),
        realm=dict(type='str', required=True),
        providerType=dict(
            choices=[
                "org.keycloak.storage.UserStorageProvider",
                "org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy",
                "org.keycloak.keys.KeyProvider",
                "authenticatorConfig",
                "requiredActions"],
            required=True),
    )
    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    result = dict(changed=False, component={}, subComponents={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')

    name = module.params.get('name')
    providerType = module.params.get('providerType')
    objRealm = kc.get_realm_by_id(realm)
    if not objRealm:
        module.fail_json(msg="Failed to retrive realm '{realm}'".format(realm=realm))

    filter = "name={name}&type={type}&parent={parent}".format(
                name=quote(name, safe=''),
                type=providerType,
                parent=quote(objRealm['id'], safe='')
             )
    
    components = kc.get_components(filter=filter, realm=realm)

    if len(components) == 1:
        component = components[0]
        filter = "parent={parent}".format(
                parent=component["id"]
             )
        subComponents = kc.get_components(filter=filter, realm=realm)
        result['component'] = component
        result['subComponents'] = subComponents

    module.exit_json(**result)


if __name__ == '__main__':
    main()
