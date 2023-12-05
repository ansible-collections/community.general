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
module: keycloak_component

short_description: Configure LDAP user storage component in Keycloak.

version_added: "8.2.0"

description:
    - This module creates, removes or update Keycloak component.
    - It can be use to create a LDAP and AD user federation to a realm in the Keycloak server
options:
    realm:
        description:
            - The name of the realm in which is the component.
        required: true
        type: str
    id:
        description:
            - ID of the component when it have already been created and it is known.
        required: false
        type: str
    name:
        description:
            - Name of the Component
        required: true
        type: str
    parent_id:
        description:
            - Parent ID of the component. Use the realm name for top level component.
        required: false
        type: str
    config:
        description:
            - Configuration of the component to create, update or delete.
        required: false
        type: dict
        suboptions:
            vendor:
                description:
                    - LDAP vendor/product
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ad
                    - tivoli
                    - edirectory
                    - rhds
                    - other
            usernameLDAPAttribute:
                description:
                    - Name of LDAP attribute, which is mapped as Keycloak username.
                    - It is usually uid, for Active Directory it is sAMAccountName.
                    - Value must be a list of one string item.
                type: list
            editMode:
                description:
                    - The Edit Mode configuration option defines the edit policy you have with your LDAP store.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - READ_ONLY
                    - WRITABLE
                    - UNSYNCED
                default:
                    - WRITABLE
            rdnLDAPAttribute:
                description:
                    - Name of LDAP attribute, which is used as RDN (top attribute) of typical user DN.
                    - Usually it's the same as Username LDAP attribute. For active Directory, it's usually cn.
                    - Value must be a list of one string item.
                type: list
            uuidLDAPAttribute:
                description:
                    - Name of LDAP attribute, which is used as unique object identifier.
                    - For many LDAP vendor it's entryUUI.
                    - For Active Directory it's objectGUID.
                    - For Red Hat Directory Server it's nsuniqueid
                    - Value must be a list of one string item.
                type: list
            userObjectClasses:
                description:
                    - All values of LDAP objectClasses attribute for users in LDAP.
                type: list
            connectionUrl:
                description:
                    - LDAP connection URL in the format [ldap|dlaps]://server.name:port
                    - Value must be a list of one string item.
                type: list
            usersDn:
                description:
                    - Full DN of LDAP tree where users are stored
                    - Value must be a list of one string item.
                type: list
            authType:
                description:
                    - LDAP authentication type.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - simple
                    - none
            bindDn:
                description:
                    - DN of LDAP admin used to authenticate to LDAP server
                    - Value must be a list of one string item.
                type: list
            bindCredential:
                description:
                    - Password for the LDAP admin
                    - Value must be a list of one string item.
                type: list
            changedSyncPeriod:
                description:
                    - Period for synchronization of changed or newly created LDAP users.
                    - To disable changed user synchronization, use -1
                    - Value must be a list of one string item.
                type: list
            fullSyncPeriod:
                description:
                    - Period for full synchronization of LDAP users.
                    - To disable full user synchronization, use -1
                    - Value must be a list of one string item.
                type: list
            pagination:
                description:
                    - Does the LDAP support pagination.
                    - Default value is false if this option is not defined
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            connectionPooling:
                description:
                    - Does the Keycloak should use connection pooling for accessing the LDAP server?
                    - Default value is true
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            cachePolicy:
                description:
                    - Cache policy for this user storage provider.
                    - Default value is ["DEFAULT"] if this option is not defined.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - DEFAULT
                    - EVICT_DAILY
                    - EVICT_WEEKLY
                    - MAX_LIFESPAN
                    - NO_CACHE
            useKerberosForPasswordAuthentication:
                description:
                    - User Kerberos module to authenticate users to Kerberos server instead
                    - of authenticate against LDAP server with Active Directory Service API.
                    - Default value is false if this option is not defined
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            allowKerberosAuthentication:
                description:
                    - Enable or disable HTTP authentication of users with SPNEGO/Kerberos tokens.
                    - Default value is false if option is not defined
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            importEnabled:
                description:
                    - If true, LDAP users are imported into the Keycloak database and synchronized.
                    - Default value is true if not defined.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            syncRegistrations:
                description:
                    - If true, user created in the Keycloak server will be synchronized to LDAP.
                    - Default value is true if not defined.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            searchScope:
                description:
                    - For one level, users will be searched in only the usersDn. If subtree,
                    - users will be searched recursively in the usersDn and his children.
                    - For one level, use 1 as value, for subtree, use 2.
                    - Default value is 2 if the option is not defined.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - 1
                    - 2
            priority:
                description:
                    - Order of priority for user search when multiple user storages are defined.
                    - Lowest first
                    - Default value is 0 when this option is not defined.
                    - Value must be a list of one string item.
                type: list
            validatePasswordPolicy:
                description:
                    - If true, users password will be checked against Keycloak password policy.
                    - Default value is true if not defined.
                    - Value must be a list of one string item.
                type: list
                choices:
                    - ['true']
                    - ['false']
            batchSizeForSync:
                description:
                    - Count of LDAP users to be imported in a single transaction.
                    - Value must be a list of one string item.
                type: list
    sub_components:
        description:
            - List of sub components to create inside the component.
            - It can be use to configure group-ldap-mapper for a User Federation.
        type: dict
        suboptions:
            "org.keycloak.storage.ldap.mappers.LDAPStorageMapper":
                description:
                    - LDAP storage mappers
                type: list
                suboptions:
                    name:
                        description:
                            - Name of the sub component
                        type: str
                    config:
                        description:
                            - Configuration for the sub component. Structure depends on the component's type.
                        type: dict
                        suboptions:
                            "ldap.attribute":
                                description:
                                    - This is for user-attribute-ldap-mapper type.
                                    - LDAP attrribute to map from.
                                    - Value must be a list of one string item.
                                type: list
                            is.mandatory.in.ldap:
                                description:
                                    - This is for user-attribute-ldap-mapper type.
                                    - If true, the attribute must be in the LDAP entry for the user.
                                    - Default value is true if the option is not defined.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - ['true']
                                    - ['false']
                            read.only:
                                description:
                                    - This is for user-attribute-ldap-mapper type.
                                    - If true, the attribute is read only.
                                    - Default value is false if the option is not defined.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - ['true']
                                    - ['false']
                            user.model.attribute:
                                description:
                                    - This is for user-attribute-ldap-mapper type.
                                    - Attribute of keycloak user model to map to..
                                    - Value must be a list of one string item.
                                type: list
                            always.read.value.from.ldap:
                                description:
                                    - This is for user-attribute-ldap-mapper type.
                                    - If true, the attribute from LDAP will always override Keycloak user model attribute.
                                    - Default value is true if the option is not defined.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - ['true']
                                    - ['false']
                            mode:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - LDAP/Keycloak groups synchronization mode.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - LDAP_ONLY
                                    - IMPORT
                                    - READ_ONLY
                            membership.attribute.type:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Membership attribute type, DN or UID.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - DN
                                    - UID
                            user.roles.retrieve.strategy:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Specify how to retrieve group members.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - LOAD_GROUPS_BY_MEMBER_ATTRIBUTE
                                    - GET_GROUPS_FROM_USER_MEMBEROF_ATTRIBUTE
                                    - LOAD_GROUPS_BY_MEMBER_ATTRIBUTE_RECURSIVELY
                            group.name.ldap.attribute:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Name of LDAP attribute which is used as the group name.
                                    - Value must be a list of one string item.
                                type: list
                            membership.ldap.attribute:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Name of LDAP attribute which is used for membership mapping.
                                    - Value must be a list of one string item.
                                type: list
                            membership.user.ldap.attribute:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Used only when membership attribute type is UID.
                                    - Name of LDAP attribute which is used for membership mapping.
                                    - Value must be a list of one string item.
                                type: list
                            memberof.ldap.attribute:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Used only when user.roles.retrieve.strategy is GET_GROUPS_FROM_USER_MEMBEROF_ATTRIBUTE.
                                    - Name of LDAP attribute on LDAP user which is used for membership mapping.
                                    - Value must be a list of one string item.
                                type: list
                            preserve.group.inheritance:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - If true, the LDAP group inheritance will be replicate on the Keycloak server.
                                    - Default value is true if the option is not defined.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - ['true']
                                    - ['false']
                            groups.dn:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - LDAP DN where groups are.
                                    - Value must be a list of one string item.
                                type: list
                            group.object.classes:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - Object class or classes for LDAP group objects.
                                    - Value must be a list of one string item.
                                type: list
                            drop.non.existing.groups.during.sync:
                                description:
                                    - This option is for group-ldap-mapper.
                                    - If true, the group on Keycloak server that does not exists in LDAP will be dropped.
                                    - Default value is false if the option is not defined.
                                    - Value must be a list of one string item.
                                type: list
                                choices:
                                    - ['true']
                                    - ['false']
    state:
        description:
            - Control if the component must exists or not
        choices: [ "present", "absent" ]
        default: present
        required: false
        type: str
    force:
        description:
            - If true, allows to remove component and recreate it.
        type: bool
        default: false
extends_documentation_fragment:
    - keycloak

author:
    - Philippe Gauthier (@elfelip)
'''

EXAMPLES = '''
    - name: Create a LDAP User Storage provider. A full sync of users and a fedToKeycloak sync for group mappers will be triggered.
      keycloak_component:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: ActiveDirectory
        config:
          vendor:
          - "ad"
          usernameLDAPAttribute:
          - "sAMAccountName"
          rdnLDAPAttribute:
          - "cn"
          uuidLDAPAttribute:
          - "objectGUID"
          userObjectClasses:
          - "person"
          - "organizationalPerson"
          - "user"
          connectionUrl:
          - "ldap://ldap.server.com:389"
          usersDn:
          - "OU=USERS,DC=server,DC=com"
          authType:
          - "simple"
          bindDn:
          - "CN=keycloak,OU=USERS,DC=server,DC=com"
          bindCredential:
          - "UnTresLongMotDePasseQuePersonneNeConnait"
          editMode:
          - "WRITABLE"
          changedSyncPeriod:
          - "86400"
          fullSyncPeriod:
          - "604800"
        sub_components:
          org.keycloak.storage.ldap.mappers.LDAPStorageMapper:
          - name: "groupMapper"
            provider_id: "group-ldap-mapper"
            config:
              mode:
                - "READ_ONLY"
              membership.attribute.type:
                - "DN"
              user.roles.retrieve.strategy:
                - "LOAD_GROUPS_BY_MEMBER_ATTRIBUTE"
              group.name.ldap.attribute:
                - "cn"
              membership.ldap.attribute:
                - "member"
              preserve.group.inheritance:
                - "true"
              membership.user.ldap.attribute:
                - "uid"
              group.object.classes:
                - "groupOfNames"
              groups.dn:
                - "cn=groups,OU=SEC,DC=SANTEPUBLIQUE,DC=RTSS,DC=QC,DC=CA"
              drop.non.existing.groups.during.sync:
                - "false"
        state: present

    - name: Re-create LDAP User Storage provider.
      keycloak_component:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: ActiveDirectory
        config:
          vendor:
          - "ad"
          usernameLDAPAttribute:
          - "sAMAccountName"
          rdnLDAPAttribute:
          - "cn"
          uuidLDAPAttribute:
          - "objectGUID"
          userObjectClasses:
          - "person"
          - "organizationalPerson"
          - "user"
          connectionUrl:
          - "ldap://ldap.server.com:389"
          usersDn:
          - "OU=USERS,DC=server,DC=com"
          authType:
          - "simple"
          bindDn:
          - "CN=keycloak,OU=USERS,DC=server,DC=com"
          bindCredential:
          - "UnTresLongMotDePasseQuePersonneNeConnait"
          editMode:
          - "WRITABLE"
          changedSyncPeriod:
          - "86400"
          fullSyncPeriod:
          - "604800"
        sub_components:
          org.keycloak.storage.ldap.mappers.LDAPStorageMapper:
          - name: "groupMapper"
            provider_id: "group-ldap-mapper"
            config:
              mode:
                - "READ_ONLY"
              membership.attribute.type:
                - "DN"
              user.roles.retrieve.strategy:
                - "LOAD_GROUPS_BY_MEMBER_ATTRIBUTE"
              group.name.ldap.attribute:
                - "cn"
              membership.ldap.attribute:
                - "member"
              preserve.group.inheritance:
                - "true"
              membership.user.ldap.attribute:
                - "uid"
              group.object.classes:
                - "groupOfNames"
              groups.dn:
                - "cn=groups,OU=SEC,DC=SANTEPUBLIQUE,DC=RTSS,DC=QC,DC=CA"
              drop.non.existing.groups.during.sync:
                - "false"
        state: present
        force: yes

    - name: Remove User Storage Provider.
      keycloak_component:
        auth_keycloak_url: http://localhost:8080/auth
        auth_sername: admin
        auth_password: password
        realm: master
        name: ActiveDirectory
        state: absent
'''

RETURN = '''
component:
  description: JSON representation for the component.
  returned: on success
  type: dict
sub_components:
  description: JSON representation of the sub components list.
  returned: on success
  type: list
msg:
  description: Error message if it is the case
  returned: on error
  type: str
changed:
  description: Return True if the operation changed the component on the keycloak server, false otherwise.
  returned: always
  type: bool
'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, \
    keycloak_argument_spec, get_token, KeycloakError, camel, is_struct_included
from ansible.module_utils.common.dict_transformations import dict_merge
# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote
import json
import copy

def main():
    argument_spec = keycloak_argument_spec()
    config_spec = dict(
        vendor=dict(type='list', choices=['ad', 'tivoli', 'edirectory', 'rhds', 'other']),
        usernameLDAPAttribute=dict(type='list'),
        editMode=dict(type='list', choices=['READ_ONLY', 'WRITABLE', 'UNSYNCED'], default=['WRITABLE']),
        rdnLDAPAttribute=dict(type='list'),
        uuidLDAPAttribute=dict(type='list'),
        userObjectClasses=dict(type='list'),
        connectionUrl=dict(type='list'),
        usersDn=dict(type='list'),
        authType=dict(type='list', choices=['simple', 'none']),
        bindDn=dict(type='list'),
        bindCredential=dict(type='list'),
        changedSyncPeriod=dict(type='list'),
        fullSyncPeriod=dict(type='list'),
        pagination=dict(type='list', choices=['true', 'false']),
        connectionPooling=dict(type='list', choices=['true', 'false']),
        cachePolicy=dict(type='list', choices=['DEFAULT', 'EVICT_DAILY', 'EVICT_WEEKLY', 'MAX_LIFESPAN', 'NO_CACHE']),
        useKerberosForPasswordAuthentication=dict(type='list', choices=['true', 'false']),
        allowKerberosAuthentication=dict(type='list', choices=[['true'], ['false']]),
        importEnabled=dict(type='list', choices=['true', 'false']),
        syncRegistrations=dict(type='list', choices=['true', 'false']),
        searchScope=dict(type='list', choices=['1', '2']),
        priority=dict(type='list'),
        validatePasswordPolicy=dict(type='list', choices=['true', 'false']),
        batchSizeForSync=dict(type='list')
    )
    ldapstoragemapper_spec = {
        "ldap.attribute": {'type': 'list'},
        "is.mandatory.in.ldap": {'type': 'list', 'choices': ['true', 'false']},
        "read.only": {'type': 'list', 'choices': ['true', 'false']},
        "user.model.attribute": {'type': 'list'},
        "always.read.value.from.ldap": {'type': 'list', 'choices': [['true'], ['false']]},
        'mode': {'type': 'list', 'choices': ['LDAP_ONLY', 'READ_ONLY', 'IMPORT']},
        "membership.attribute.type": {'type': 'list', 'choices': ['DN', 'UID']},
        "user.roles.retrieve.strategy": {'type': 'list', 'choices': [
            'LOAD_GROUPS_BY_MEMBER_ATTRIBUTE',
            'GET_GROUPS_FROM_USER_MEMBEROF_ATTRIBUTE',
            'LOAD_GROUPS_BY_MEMBER_ATTRIBUTE_RECURSIVELY'
        ]},
        'group.name.ldap.attribute': {'type': 'list'},
        'membership.ldap.attribute': {'type': 'list'},
        'membership.user.ldap.attribute': {'type': 'list'},
        'memberof.ldap.attribute': {'type': 'list'},
        'preserve.group.inheritance': {'type': 'list', 'choices': ['true', 'false']},
        'groups.dn': {'type': 'list'},
        'group.object.classes': {'type': 'list'},
        'drop.non.existing.groups.during.sync': {'type': 'list', 'choices': ['true', 'false']}
    }
    sub_components_config_spec = {
        "name": {"type": "str"},
        "provider_id": {"type": "str", "choices": ['user-attribute-ldap-mapper', 'group-ldap-mapper']},
        "config": {"type": "dict", "options": ldapstoragemapper_spec}
    }
    sub_components_spec = {
        "org.keycloak.storage.ldap.mappers.LDAPStorageMapper": {'type': 'list', 'options': sub_components_config_spec, 'required': True}
    }
    meta_args = dict(
        name=dict(type='str', required=True),
        realm=dict(type='str', required=True),
        config=dict(type='dict', options=config_spec),
        sub_components=dict(type='dict', options=sub_components_spec),
        state=dict(choices=["absent", "present"], default='present'),
        force=dict(type='bool', default=False),
    )
    argument_spec.update(meta_args)

    required_if = [
        ('state', 'present', ['config', 'sub_components'])
    ]

    module = AnsibleModule(argument_spec=argument_spec,
                           required_if=required_if,
                           supports_check_mode=True)

    result = dict(changed=False, msg='', component={}, sub_components=[])

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    force = module.params.get('force')

    # convert module parameters to realm representation parameters (if they belong in there)
    params_to_ignore = list(keycloak_argument_spec().keys()) + ['state','realm','force','sub_components']

    # Filter and map the parameters names that apply to the role
    component_params = [x for x in module.params
                    if x not in params_to_ignore and
                    module.params.get(x) is not None]
        
    objRealm = kc.get_realm_by_id(realm)
    if not objRealm:
        module.fail_json(msg="Failed to retrive realm '{realm}'".format(realm=realm))

    # Create a representation from module parameters
    changeset = {}
    for realm_param in component_params:
        new_param_value = module.params.get(realm_param)
        changeset[camel(realm_param)] = new_param_value

    changeset["providerId"] = "ldap"
    changeset["providerType"] = "org.keycloak.storage.UserStorageProvider"
    changeset["parentId"] = objRealm['id']

    storageMapper = module.params.get("sub_components") #["org.keycloak.storage.ldap.mappers.LDAPStorageMapper"]
    changeset_sub_components = {}
    
    if storageMapper:
        for componentType in storageMapper.keys():
            newComponents = []
            componentChangesets = storageMapper[componentType]
            for i in range(len(componentChangesets)):
                item = componentChangesets[i]
                subitem = {}
                for param in item:
                    new_param_value = item.get(param)
                    subitem[camel(param)] = new_param_value
                newComponents.append(subitem)
            changeset_sub_components[componentType] = newComponents

    changeset = remove_arguments_with_value_none(changeset)
    changeset_sub_components = remove_arguments_with_value_none(changeset_sub_components)
    changed = False

    filter = "name={name}&type={type}&parent={parent}".format(
                name=quote(changeset["name"], safe=''),
                type=changeset["providerType"],
                parent=quote(changeset["parentId"], safe='')
             )
    component = get_component(kc, filter=filter, realm=realm)

    if not component:  # If component does not exist
        if (state == 'present'):  # If desired stat is present
            # Create the component and it's sub-components
            kc.create_component(changeset, realm)
            component = get_component(kc, filter=filter, realm=realm)
            create_update_sub_components(kc, component['id'], [], changeset_sub_components, realm)

            result['component'] = component
            result['sub_components'] = get_sub_components(kc, component["id"], realm)
            result['changed'] = True
        elif state == 'absent':  # Id desired state is absent, return absent and do nothing.
            result['msg'] = changeset["name"] + ' absent'
            result['component'] = changeset

    else:  # If component already exist
        if (state == 'present'):  # if desired state is present

            desired_component = copy.deepcopy(component)
            merge(changeset, desired_component)
            result['changed'] = not is_struct_included(component, desired_component, ['bindCredential','lastSync'])        

            if force:  # If force option is true
                # Delete the existing component
                kc.delete_component(component["id"], realm)
                result['changed'] = True
                # Re-create the component.
                kc.create_component(changeset, realm)
            elif result['changed']:  # If force option is false
                # Copy existing id in new component
                changeset['id'] = component['id']
                kc.update_component(changeset, realm)

            component = get_component(kc, filter=filter, realm=realm)
            sub_components = get_sub_components(kc, component["id"], realm)
            # Update sub components
            if create_update_sub_components(kc, component['id'], sub_components, changeset_sub_components, realm):
                result['changed'] = True

            result['component'] = component
            result['sub_components'] = get_sub_components(kc, component["id"], realm)

        elif state == 'absent':  # if desired state is absent
            # Delete the component
            kc.delete_component(component['id'], realm)
            changed = True
            result['msg'] = changeset["name"] + ' deleted'
            result['changed'] = changed

    module.exit_json(**result)

def get_sub_components(kc, parent_id, realm):
    filter = "parent={parent}".format(
        parent=parent_id
    )
    return kc.get_components(filter=filter, realm=realm)

def merge(source, destination):
    """
    
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination

def create_update_sub_components(kc, parentid ,subcomponents, newSubComponents, realm):
    """
    Create or Update subcomponents for a component.
    :param component: Representation of the parent component
    :param newSubComponents: List of subcomponents to create for this parent
    :param realm: Realm
    :return: True if changed
    """
    retValue = False

    for componentType in newSubComponents.keys():
        oldcomponents = {}
        for component in subcomponents:
            if component["providerType"] == componentType:
                oldcomponents[component["name"]] = component
        components = newSubComponents[componentType]
        for newcomponent in components:
            name = newcomponent["name"]
            newcomponent["parentId"] = parentid
            newcomponent["providerType"] = componentType
            if name in oldcomponents:
                desired_component = copy.deepcopy(oldcomponents[name])
                merge(newcomponent, desired_component)
                if not is_struct_included(oldcomponents[name], desired_component):
                    newcomponent['id'] = oldcomponents[name]['id']
                    kc.update_component(newcomponent, realm)
                    retValue = True
                del oldcomponents[name]
            else:
                kc.create_component(newcomponent, realm)
                retValue = True

    return retValue

def get_component(kc, filter, realm):
    components = kc.get_components(filter=filter, realm=realm)
    if len(components) == 1:
        return components[0]
    return None

def remove_arguments_with_value_none(argument):
    """
    This function remove all NoneType elements from dict object.
    This is useful when argument_spec include optional keys which dos not need to be
    POST or PUT to Keycloak API.
    :param argument: Dict from which to remove NoneType elements
    :return: Dict without None values
    """

    if type(argument) is dict:
        newarg = {}
        for key in argument.keys():
            if type(argument[key]) is list:
                newarg[key] = []
                for element in argument[key]:
                    newelement = remove_arguments_with_value_none(element)
                    if newelement is not None:
                        newarg[key].append(newelement)
            elif type(argument[key]) is dict:
                newvalue = remove_arguments_with_value_none(argument[key])
                if newvalue is not None:
                    newarg[key] = newvalue
            elif argument[key] is not None:
                newarg[key] = argument[key]
        return newarg
    return argument

if __name__ == '__main__':
    main()
