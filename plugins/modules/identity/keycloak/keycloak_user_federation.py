#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: keycloak_user_federation

short_description: Allows administration of Keycloak user federations via Keycloak API

description:
    - This module allows you to add, remove or modify Keycloak user federations via the Keycloak REST API.
      It requires access to the REST API via OpenID Connect; the user connecting and the client being
      used must have the requisite access rights. In a default Keycloak installation, admin-cli
      and an admin user would work, as would a separate client definition with the scope tailored
      to your needs and a user having the expected roles.

    - The names of module options are snake_cased versions of the camelCase ones found in the
      Keycloak API and its documentation at U(https://www.keycloak.org/docs-api/15.0/rest-api/index.html).


options:
    state:
        description:
            - State of the user federation.
            - On C(present), the user federation will be created if it does not yet exist, or updated with the parameters you provide.
            - On C(absent), the user federation will be removed if it exists.
        default: 'present'
        type: str
        choices:
            - present
            - absent

    realm:
        description:
            - The Keycloak realm under which this user federation resides.
        default: 'master'
        type: str

    id:
        description:
            - The id uniquely identifies a user federation.
        required: true
        type: str

    name:
        description:
            - Display name of provider when linked in admin console.
        type: str

    config:
        description:
            - Dict specifying the configuration options for the provider; the contents differ depending on the value of I(providerId).
              Examples are given below for C(oidc) and C(saml). It is easiest to obtain valid config values by dumping an already-existing
              user federation configuration through check-mode in the I(existing) field.
        type: dict
        suboptions:
            enabled:
                description:
                    - Enable/disable this user federation.
                type: bool

            priority:
                description:
                    - Priority of provider when doing a user lookup. Lowest first.
                type: int

            import_enabled:
                description:
                    - If true, LDAP users will be imported into Keycloak DB and synced by the configured sync policies.
                aliases:
                    - importEnabled
                type: bool

            edit_mode:
                description:
                    - READ_ONLY is a read-only LDAP store. WRITABLE means data will be synced back to LDAP on demand. UNSYNCED
                    means user data will be imported, but not synced back to LDAP.
                aliases:
                    - editMode
                type: str
                choices:
                    - READ_ONLY
                    - WRITABLE
                    - UNSYNCED

            sync_registrations:
                description:
                    - Should newly created users be created within LDAP store? Priority effects which provider is chosen to sync the new user.
                aliases:
                    - syncRegistrations
                type: bool

            vendor:
                description:
                    - LDAP vendor (provider).
                type: str

            username_ldap_attribute:
                description:
                    - Name of LDAP attribute, which is mapped as Keycloak username. For many LDAP server vendors it can be 'uid'. For Active
                    directory it can be 'sAMAccountName' or 'cn'. The attribute should be filled for all LDAP user records you want to import
                    from LDAP to Keycloak.
                aliases:
                    - usernameLDAPAttribute
                type: str

            rdn_ldap_attribute:
                description:
                    - Name of LDAP attribute, which is used as RDN (top attribute) of typical user DN. Usually it's the same as Username LDAP
                    attribute, however it is not required. For example for Active directory, it is common to use 'cn' as RDN attribute when
                    username attribute might be 'sAMAccountName'.
                aliases:
                    - rdnLDAPAttribute
                type: str

            uuid_ldap_attribute:
                description:
                    - Name of LDAP attribute, which is used as unique object identifier (UUID) for objects in LDAP. For many LDAP server vendors,
                    it is 'entryUUID'; however some are different. For example for Active directory it should be 'objectGUID'. If your LDAP server
                    does not support the notion of UUID, you can use any other attribute that is supposed to be unique among LDAP users in tree.
                aliases:
                    - uuidLDAPAttribute
                type: str

            user_object_classes:
                description:
                    - All values of LDAP objectClass attribute for users in LDAP divided by comma. For example: 'inetOrgPerson, organizationalPerson'.
                    Newly created Keycloak users will be written to LDAP with all those object classes and existing LDAP user records are found just
                    if they contain all those object classes.
                aliases:
                    - userObjectClasses
                type: str

            connection_url:
                description:
                    - Connection URL to your LDAP server.
                aliases:
                    - connectionUrl
                type: str

            users_dn:
                description:
                    - Full DN of LDAP tree where your users are. This DN is the parent of LDAP users.
                aliases:
                    - usersDn
                type: str

            customUser_search_filter:
                description:
                    - Additional LDAP Filter for filtering searched users. Leave this empty if you don't need additional filter.
                aliases:
                    - customUserSearchFilter
                type: str

            search_scope:
                description:
                    - For one level, the search applies only for users in the DNs specified by User DNs. For subtree, the search applies to the
                    whole subtree. See LDAP documentation for more details
                aliases:
                    - searchScope
                type: str

            auth_type:
                description:
                    - Type of the Authentication method used during LDAP Bind operation. It is used in most of the requests sent to the LDAP server.
                    Currently only 'none' (anonymous LDAP authentication) or 'simple' (Bind credential + Bind password authentication) mechanisms are available.
                aliases:
                    - authType
                type: str

            bind_dn:
                description:
                    - DN of LDAP user which will be used by Keycloak to access LDAP server.
                aliases:
                    - bindDn
                type: str

            bind_credential:
                description:
                    - Password of LDAP admin. This field is able to obtain its value from vault, use ${vault.ID} format.
                aliases:
                    - bindCredential
                type: str

            start_tls:
                description:
                    - Encrypts the connection to LDAP using STARTTLS, which will disable connection pooling.
                aliases:
                    - startTls
                type: bool

            use_password_modify_extended_op:
                description:
                    - Use the LDAPv3 Password Modify Extended Operation (RFC-3062). The password modify extended operation usually requires
                    that LDAP user already has password in the LDAP server. So when this is used with 'Sync Registrations', it can be good to
                    add also 'Hardcoded LDAP attribute mapper' with randomly generated initial password.
                aliases:
                    - usePasswordModifyExtendedOp
                type: bool

            validate_password_policy:
                description:
                    - Determines if Keycloak should validate the password with the realm password policy before updating it.
                aliases:
                    - validatePasswordPolicy
                type: bool

            trust_email:
                description:
                    - If enabled, email provided by this provider is not verified even if verification is enabled for the realm.
                aliases:
                    - trustEmail
                type: bool

            use_truststore_spi:
                description:
                    - Specifies whether LDAP connection will use the truststore SPI with the truststore configured in standalone.xml/domain.xml.
                    'Always' means that it will always use it. 'Never' means that it will not use it. 'Only for ldaps' means that it will use if
                    your connection URL use ldaps. Note even if standalone.xml/domain.xml is not configured, the default Java cacerts or certificate
                    specified by 'javax.net.ssl.trustStore' property will be used.
                aliases:
                    - useTruststoreSpi
                type: str

            connection_timeout:
                description:
                    - LDAP Connection Timeout in milliseconds.
                aliases:
                    - connectionTimeout
                type: int

            read_timeout:
                description:
                    - LDAP Read Timeout in milliseconds. This timeout applies for LDAP read operations.
                aliases:
                    - readTimeout
                type: int

            pagination:
                description:
                    - Does the LDAP server support pagination.
                type: bool

            connection_pooling:
                description:
                    - Determines if Keycloak should use connection pooling for accessing LDAP server.
                aliases:
                    - connectionPooling
                type: bool

            connection_pooling_authentication:
                description:
                    - A list of space-separated authentication types of connections that may be pooled. Valid types are "none", "simple", and "DIGEST-MD5".
                aliases:
                    - connectionPoolingAuthentication
                type: str

            connection_pooling_debug:
                description:
                    - A string that indicates the level of debug output to produce. Valid values are "fine" (trace connection creation and removal) and "all" (all debugging information).
                aliases:
                    - connectionPoolingDebug
                type: str

            connection_pooling_init_size:
                description:
                    - The string representation of an integer that represents the number of connections per connection identity to create when initially creating a connection for the identity.
                aliases:
                    - connectionPoolingInitSize
                type: str

            connection_pooling_max_size:
                description:
                    - The string representation of an integer that represents the maximum number of connections per connection identity that can be maintained concurrently.
                aliases:
                    - connectionPoolingMaxSize
                type: str

            connection_pooling_pref_size:
                description:
                    - The string representation of an integer that represents the preferred number of connections per connection identity that should be maintained concurrently.
                aliases:
                    - connectionPoolingPrefSize
                type: str

            connection_pooling_protocol:
                description:
                    - A list of space-separated protocol types of connections that may be pooled. Valid types are "plain" and "ssl".
                aliases:
                    - connectionPoolingProtocol
                type: str

            connection_pooling_timeout:
                description:
                    - The string representation of an integer that represents the number of milliseconds that an idle connection may remain in the pool without being closed and removed from the pool.
                aliases:
                    - connectionPoolingTimeout
                type: str

            allow_kerberos_authentication:
                description:
                    - Enable/disable HTTP authentication of users with SPNEGO/Kerberos tokens. The data about authenticated users will be provisioned from this LDAP server.
                aliases:
                    - allowKerberosAuthentication
                type: bool

            kerberos_realm:
                description:
                    - Name of kerberos realm.
                aliases:
                    - kerberosRealm
                type: str

            server_principal:
                description:
                    - Full name of server principal for HTTP service including server and domain name. For example 'HTTP/host.foo.org@FOO.ORG'. Use '*' to accept any service principal in the KeyTab file.
                aliases:
                    - serverPrincipal
                type: str

            key_tab:
                description:
                    - Location of Kerberos KeyTab file containing the credentials of server principal. For example /etc/krb5.keytab.
                aliases:
                    - keyTab
                type: str

            debug:
                description:
                    - Enable/disable debug logging to standard output for Krb5LoginModule.
                type: bool

            use_kerberos_for_password_authentication:
                description:
                    - Use Kerberos login module for authenticate username/password against Kerberos server instead of authenticating against LDAP server with Directory Service API.
                aliases:
                    - useKerberosForPasswordAuthentication
                type: str

            allow_password_authentication:
                description:
                    - Enable/disable possibility of username/password authentication against Kerberos database.
                aliases:
                    - allowPasswordAuthentication
                type: bool

            batch_size_for_sync:
                description:
                    - Count of LDAP users to be imported from LDAP to Keycloak within a single transaction.
                aliases:
                    - batchSizeForSync
                type: int

            full_sync_period:
                description:
                    - Period for full synchronization in seconds.
                aliases:
                    - fullSyncPeriod
                type: int

            changed_sync_period:
                description:
                    - Period for synchronization of changed or newly created LDAP users in seconds.
                aliases:
                    - changedSyncPeriod
                type: int

            update_profile_first_login:
                description:
                    - Update profile on first login.
                aliases:
                    - updateProfileFirstLogin
                type: bool

            cache_policy:
                description:
                    - Cache Policy for this storage provider.
                      'DEFAULT' is whatever the default settings are for the global cache.
                      'EVICT_DAILY' is a time of day every day that the cache will be invalidated.
                      'EVICT_WEEKLY' is a day of the week and time the cache will be invalidated.
                      'MAX-LIFESPAN' is the time in milliseconds that will be the lifespan of a cache entry.
                aliases:
                    - cachePolicy
                type: str

            eviction_day:
                description:
                    - Day of the week the entry will become invalid on.
                aliases:
                    - evictionDay
                type: str

            eviction_hour:
                description:
                    - Hour of day the entry will become invalid on.
                aliases:
                    - evictionHour
                type: str

            eviction_minute:
                description:
                    - Minute of day the entry will become invalid on.
                aliases:
                    - evictionMinute
                type: str

            max_lifespan:
                description:
                    - Max lifespan of cache entry in milliseconds.
                aliases:
                    - maxLifespan
                type: str

    mappers:
        description:
            - A list of dicts defining mappers associated with this Identity Provider.
        type: list
        elements: dict
        suboptions:
            id:
                description:
                    - Unique ID of this mapper.
                type: str

            name:
                description:
                    - Name of the mapper.
                type: str

            identityProviderAlias:
                description:
                    - Alias of the user federation for this mapper.
                type: str

            identityProviderMapper:
                description:
                    - Type of mapper.
                type: str

            config:
                description:
                    - Dict specifying the configuration options for the mapper; the contents differ depending on the value of I(identityProviderMapper).
                type: dict

extends_documentation_fragment:
- community.general.keycloak

author:
    - Laurent Paumier (@laurpaum)
'''

EXAMPLES = '''
  - name: Create LDAP user federation
    community.general.keycloak_user_federation:
      auth_keycloak_url: https://keycloak.example.com/auth
      auth_realm: master
      auth_username: admin
      auth_password: password
      realm: my-realm
      name: my-ldap
      state: present
      provider_id: ldap
      provider_type: org.keycloak.storage.UserStorageProvider
      config:
        priority: 0
        enabled: true
        cachePolicy: DEFAULT
        batchSizeForSync: 1000
        editMode: READ_ONLY
        importEnabled: true
        syncRegistrations: false
        vendor: other
        usernameLDAPAttribute: uid
        rdnLDAPAttribute: uid
        uuidLDAPAttribute: entryUUID
        userObjectClasses: inetOrgPerson, organizationalPerson
        connectionUrl: ldaps://ldap.example.com:636
        usersDn: ou=Users,dc=example,dc=com
        authType: simple
        bindDn: cn=directory reader
        bindCredential: password
        searchScope: 1
        validatePasswordPolicy: false
        trustEmail: false
        useTruststoreSpi: ldapsOnly
        connectionPooling: true
        pagination: true
        allowKerberosAuthentication: false
        debug: false
        useKerberosForPasswordAuthentication: false
      mappers:
        - name: "full name"
          providerId: "full-name-ldap-mapper"
          providerType: "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
          config:
            ldap.full.name.attribute: cn
            read.only: true
            write.only: false

  - name: Create Kerberos user federation
    community.general.keycloak_user_federation:
      auth_keycloak_url: https://keycloak.example.com/auth
      auth_realm: master
      auth_username: admin
      auth_password: password
      realm: my-realm
      name: my-kerberos
      state: present
      provider_id: kerberos
      provider_type: org.keycloak.storage.UserStorageProvider
      config:
        priority: 0
        enabled: true
        cachePolicy: DEFAULT
        kerberosRealm: EXAMPLE.COM
        serverPrincipal: HTTP/host.example.com@EXAMPLE.COM
        keyTab: keytab
        allowPasswordAuthentication: false
        updateProfileFirstLogin: false

  - name: Delete user federation
    community.general.keycloak_user_federation:
      auth_keycloak_url: https://keycloak.example.com/auth
      auth_realm: master
      auth_username: admin
      auth_password: password
      realm: my-realm
      name: my-federation
      state: absent

'''

RETURN = '''
msg:
  description: Message as to what action was taken
  returned: always
  type: str
  sample: "No changes required to user federation 164bb483-c613-482e-80fe-7f1431308799."

proposed:
    description: Representation of proposed changes to user federation
    returned: always
    type: dict
    sample: {
        "config": {
            "allowKerberosAuthentication": "false",
            "authType": "simple",
            "batchSizeForSync": "1000",
            "bindCredential": "**********",
            "bindDn": "cn=directory reader",
            "cachePolicy": "DEFAULT",
            "connectionPooling": "true",
            "connectionUrl": "ldaps://ldap.example.com:636",
            "debug": "false",
            "editMode": "READ_ONLY",
            "enabled": "true",
            "importEnabled": "true",
            "pagination": "true",
            "priority": "0",
            "rdnLDAPAttribute": "uid",
            "searchScope": "1",
            "syncRegistrations": "false",
            "trustEmail": "false",
            "useKerberosForPasswordAuthentication": "false",
            "useTruststoreSpi": "ldapsOnly",
            "userObjectClasses": "inetOrgPerson, organizationalPerson",
            "usernameLDAPAttribute": "uid",
            "usersDn": "ou=Users,dc=example,dc=com",
            "uuidLDAPAttribute": "entryUUID",
            "validatePasswordPolicy": "false",
            "vendor": "other"
        },
        "name": "ldap",
        "providerId": "ldap",
        "providerType": "org.keycloak.storage.UserStorageProvider"
    }

existing:
    description: Representation of existing user federation
    returned: always
    type: dict
    sample: {
        "config": {
            "allowKerberosAuthentication": "false",
            "authType": "simple",
            "batchSizeForSync": "1000",
            "bindCredential": "**********",
            "bindDn": "cn=directory reader",
            "cachePolicy": "DEFAULT",
            "changedSyncPeriod": "-1",
            "connectionPooling": "true",
            "connectionUrl": "ldaps://ldap.example.com:636",
            "debug": "false",
            "editMode": "READ_ONLY",
            "enabled": "true",
            "fullSyncPeriod": "-1",
            "importEnabled": "true",
            "pagination": "true",
            "priority": "0",
            "rdnLDAPAttribute": "uid",
            "searchScope": "1",
            "syncRegistrations": "false",
            "trustEmail": "false",
            "useKerberosForPasswordAuthentication": "false",
            "useTruststoreSpi": "ldapsOnly",
            "userObjectClasses": "inetOrgPerson, organizationalPerson",
            "usernameLDAPAttribute": "uid",
            "usersDn": "ou=Users,dc=example,dc=com",
            "uuidLDAPAttribute": "entryUUID",
            "validatePasswordPolicy": "false",
            "vendor": "other"
        },
        "id": "01122837-9047-4ae4-8ca0-6e2e891a765f",
        "mappers": [
            {
                "config": {
                    "always.read.value.from.ldap": "false",
                    "is.mandatory.in.ldap": "false",
                    "ldap.attribute": "mail",
                    "read.only": "true",
                    "user.model.attribute": "email"
                },
                "id": "17d60ce2-2d44-4c2c-8b1f-1fba601b9a9f",
                "name": "email",
                "parentId": "01122837-9047-4ae4-8ca0-6e2e891a765f",
                "providerId": "user-attribute-ldap-mapper",
                "providerType": "org.keycloak.storage.ldap.mappers.LDAPStorageMapper"
            }
        ],
        "name": "myfed",
        "parentId": "myrealm",
        "providerId": "ldap",
        "providerType": "org.keycloak.storage.UserStorageProvider"
    }

end_state:
    description: Representation of user federation after module execution
    returned: always
    type: dict
    sample: {
        "config": {
            "allowPasswordAuthentication": "false",
            "cachePolicy": "DEFAULT",
            "enabled": "true",
            "kerberosRealm": "EXAMPLE.COM",
            "keyTab": "/etc/krb5.keytab",
            "priority": "0",
            "serverPrincipal": "HTTP/host.example.com@EXAMPLE.COM",
            "updateProfileFirstLogin": "false"
        },
        "id": "cf52ae4f-4471-4435-a0cf-bb620cadc122",
        "mappers": [],
        "name": "kerberos",
        "parentId": "myrealm",
        "providerId": "kerberos",
        "providerType": "org.keycloak.storage.UserStorageProvider"
    }

'''

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import KeycloakAPI, camel, \
    keycloak_argument_spec, get_token, KeycloakError
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from copy import deepcopy


def sanitize(comp):
    result = deepcopy(comp)
    if 'config' in result:
        result['config'] = dict((k, v[0]) for k, v in result['config'].items())
        if 'bindCredential' in result['config']:
            result['config']['bindCredential'] = '**********'
    if 'mappers' in result:
        for mapper in result['mappers']:
            if 'config' in mapper:
                mapper['config'] = dict((k, v[0]) for k, v in mapper['config'].items())
    return result


def main():
    """
    Module execution

    :return:
    """
    argument_spec = keycloak_argument_spec()

    config_spec = dict(
        allowKerberosAuthentication=dict(type='bool'),
        allowPasswordAuthentication=dict(type='bool'),
        authType=dict(type='str'),
        batchSizeForSync=dict(type='int'),
        bindCredential=dict(type='str'),
        bindDn=dict(type='str'),
        cachePolicy=dict(type='str'),
        changedSyncPeriod=dict(type='int'),
        connectionPooling=dict(type='bool'),
        connectionPoolingAuthentication=dict(type='str'),
        connectionPoolingDebug=dict(type='str'),
        connectionPoolingInitSize=dict(type='int'),
        connectionPoolingMaxSize=dict(type='int'),
        connectionPoolingPrefSize=dict(type='int'),
        connectionPoolingProtocol=dict(type='str'),
        connectionPoolingTimeout=dict(type='int'),
        connectionTimeout=dict(type='int'),
        connectionUrl=dict(type='str'),
        customUserSearchFilter=dict(type='str'),
        debug=dict(type='bool'),
        editMode=dict(type='str'),
        enabled=dict(type='bool'),
        evictionDay=dict(type='str'),
        evictionHour=dict(type='str'),
        evictionMinute=dict(type='str'),
        fullSyncPeriod=dict(type='int'),
        importEnabled=dict(type='bool'),
        kerberosRealm=dict(type='str'),
        keyTab=dict(type='str'),
        maxLifespan=dict(type='int'),
        pagination=dict(type='bool'),
        priority=dict(type='int'),
        rdnLDAPAttribute=dict(type='str'),
        readTimeout=dict(type='int'),
        searchScope=dict(type='str'),
        serverPrincipal=dict(type='str'),
        startTls=dict(type='bool'),
        syncRegistrations=dict(type='bool'),
        trustEmail=dict(type='bool'),
        updateProfileFirstLogin=dict(type='bool'),
        useKerberosForPasswordAuthentication=dict(type='bool'),
        usePasswordModifyExtendedOp=dict(type='str'),
        useTruststoreSpi=dict(type='str'),
        userObjectClasses=dict(type='str'),
        usernameLDAPAttribute=dict(type='str'),
        usersDn=dict(type='str'),
        uuidLDAPAttribute=dict(type='str'),
        validatePasswordPolicy=dict(type='bool'),
        vendor=dict(type='str'),
    )

    mapper_spec = dict(
        id=dict(type='str'),
        name=dict(type='str'),
        parentId=dict(type='str'),
        providerId=dict(type='str'),
        providerType=dict(type='str'),
        config=dict(type='dict'),
    )

    meta_args = dict(
        state=dict(type='str', default='present', choices=['present', 'absent']),
        realm=dict(type='str', default='master'),
        id=dict(type='str'),
        name=dict(type='str'),
        provider_id=dict(type='str', aliases=['providerId']),
        provider_type=dict(type='str', aliases=['providerType'], default='org.keycloak.storage.UserStorageProvider'),
        parent_id=dict(type='str', aliases=['parentId']),
        config=dict(type='dict', options=config_spec),
        mappers=dict(type='list', elements='dict', options=mapper_spec),
    )

    argument_spec.update(meta_args)

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           required_one_of=([['id', 'name'],
                                             ['token', 'auth_realm', 'auth_username', 'auth_password']]),
                           required_together=([['auth_realm', 'auth_username', 'auth_password']]))

    result = dict(changed=False, msg='', diff={}, proposed={}, existing={}, end_state={})

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    realm = module.params.get('realm')
    state = module.params.get('state')
    config = module.params.get('config')
    mappers = module.params.get('mappers')
    cid = module.params.get('id')
    name = module.params.get('name')

    # Keycloak API expects config parameters to be arrays containing a single string element
    if config is not None:
        module.params['config'] = dict((k, [str(v).lower() if not isinstance(v, str) else v])
                                       for k, v in config.items() if config[k] is not None)

    if mappers is not None:
        for mapper in mappers:
            if mapper.get('config') is not None:
                mapper['config'] = dict((k, [str(v).lower() if not isinstance(v, str) else v])
                                        for k, v in mapper['config'].items() if mapper['config'][k] is not None)

    # convert module parameters to client representation parameters (if they belong in there)
    comp_params = [x for x in module.params
                   if x not in list(keycloak_argument_spec().keys()) + ['state', 'realm', 'mappers'] and
                   module.params.get(x) is not None]

    # does the user federation already exist?
    if cid is None:
        found = kc.get_components('type=org.keycloak.storage.UserStorageProvider&parent={id}&name={name}'.format(id=realm, name=name), realm)
        if len(found) > 1:
            module.fail_json(msg='No ID given and found multiple user federations with name `{name}`. Cannot continue.'.format(name=name))
        before_comp = next(iter(found), None)
        if before_comp is not None:
            cid = before_comp['id']
    else:
        before_comp = kc.get_component(cid, realm)

    if before_comp is None:
        before_comp = dict()

    # if user federation exists, get associated mappers
    if cid is not None:
        before_comp['mappers'] = sorted(kc.get_components(urlencode(dict(parent=cid)), realm), key=lambda x: x.get('name'))

    # build a changeset
    changeset = dict()

    for param in comp_params:
        new_param_value = module.params.get(param)
        old_value = before_comp[camel(param)] if camel(param) in before_comp else None
        if param == 'mappers':
            new_param_value = [dict((k, v) for k, v in x.items() if x[k] is not None) for x in new_param_value]
        if new_param_value != old_value:
            changeset[camel(param)] = new_param_value

    # special handling of mappers list to allow change detection
    if module.params.get('mappers') is not None:
        if module.params['provider_id'] == 'kerberos':
            module.fail_json(msg='Cannot configure mappers for Kerberos federations.')
        for change in module.params['mappers']:
            change = dict((k, v) for k, v in change.items() if change[k] is not None)
            if change.get('id') is None and change.get('name') is None:
                module.fail_json(msg='Either `name` or `id` has to be specified on each mapper.')
            if cid is None:
                old_mapper = dict()
            elif change.get('id') is not None:
                old_mapper = kc.get_component(change['id'], realm)
                if old_mapper is None:
                    old_mapper = dict()
            else:
                found = kc.get_components(urlencode(dict(parent=cid, name=change['name'])), realm)
                if len(found) > 1:
                    module.fail_json(msg='Found multiple mappers with name `{name}`. Cannot continue.'.format(name=change['name']))
                if len(found) == 1:
                    old_mapper = found[0]
                else:
                    old_mapper = dict()
            new_mapper = old_mapper.copy()
            new_mapper.update(change)
            if new_mapper != old_mapper:
                if changeset.get('mappers') is None:
                    changeset['mappers'] = list()
                changeset['mappers'].append(new_mapper)

    # prepare the new representation
    updated_comp = before_comp.copy()
    updated_comp.update(changeset)

    result['proposed'] = sanitize(changeset)
    result['existing'] = sanitize(before_comp)

    # if before_comp is none, the user federation doesn't exist.
    if before_comp == dict():
        if state == 'absent':
            # nothing to do.
            if module._diff:
                result['diff'] = dict(before='', after='')
            result['changed'] = False
            result['end_state'] = dict()
            result['msg'] = 'User federation does not exist; doing nothing.'
            module.exit_json(**result)

        # for 'present', create a new user federation.
        result['changed'] = True

        if module._diff:
            result['diff'] = dict(before='', after=updated_comp)

        if module.check_mode:
            module.exit_json(**result)

        # do it for real!
        updated_comp = updated_comp.copy()
        updated_mappers = updated_comp.pop('mappers', [])
        after_comp = kc.create_component(updated_comp, realm)

        for mapper in updated_mappers:
            if mapper.get('id') is not None:
                kc.update_component(mapper, realm)
            else:
                if mapper.get('parentId') is None:
                    mapper['parentId'] = after_comp['id']
                mapper = kc.create_component(mapper, realm)

        after_comp['mappers'] = updated_mappers
        result['end_state'] = sanitize(after_comp)

        result['msg'] = "User federation {id} has been created".format(id=after_comp['id'])
        module.exit_json(**result)

    else:
        if state == 'present':
            # no changes
            if updated_comp == before_comp:
                result['changed'] = False
                result['end_state'] = updated_comp
                result['msg'] = "No changes required to user federation {id}.".format(id=cid)
                module.exit_json(**result)

            # update the existing role
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_comp, after=updated_comp)

            if module.check_mode:
                module.exit_json(**result)

            # do the update
            updated_comp = updated_comp.copy()
            updated_mappers = updated_comp.pop('mappers', [])
            kc.update_component(updated_comp, realm)
            after_comp = kc.get_component(cid, realm)

            for mapper in updated_mappers:
                if mapper.get('id') is not None:
                    kc.update_component(mapper, realm)
                else:
                    if mapper.get('parentId') is None:
                        mapper['parentId'] = updated_comp['id']
                    mapper = kc.create_component(mapper, realm)

            after_comp['mappers'] = updated_mappers
            result['end_state'] = sanitize(after_comp)

            result['msg'] = "User federation {id} has been updated".format(id=cid)
            module.exit_json(**result)

        elif state == 'absent':
            result['changed'] = True

            if module._diff:
                result['diff'] = dict(before=before_comp, after='')

            if module.check_mode:
                module.exit_json(**result)

            # delete for real
            kc.delete_component(cid, realm)

            result['end_state'] = dict()

            result['msg'] = "User federation {id} has been deleted".format(id=cid)
            module.exit_json(**result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
