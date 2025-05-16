#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright: (c) 2016, Adfinis SyGroup AG
# Tobias Rueetschi <tobias.ruetschi@adfinis-sygroup.ch>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: udm_share
author:
- Tobias Rüetschi (@keachi)
short_description: Manage samba shares on a univention corporate server
description:
    - "This module allows to manage samba shares on a univention corporate
       server (UCS).
       It uses the python API of the UCS to create a new object or edit it."
requirements:
    - Python >= 2.6
options:
    state:
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the share is present or not.
    name:
        required: true
        description:
            - Name
    host:
        required: false
        description:
            - Host FQDN (server which provides the share), e.g. C({{
              ansible_fqdn }}). Required if C(state=present).
    path:
        required: false
        description:
            - Directory on the providing server, e.g. C(/home). Required if C(state=present).
    samba_name:
        required: false
        description:
            - Windows name. Required if C(state=present).
        aliases: [ sambaName ]
    ou:
        required: true
        description:
            - Organisational unit, inside the LDAP Base DN.
    owner:
        default: 0
        description:
            - Directory owner of the share's root directory.
    group:
        default: '0'
        description:
            - Directory owner group of the share's root directory.
    directorymode:
        default: '00755'
        description:
            - Permissions for the share's root directory.
    root_squash:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Modify user ID for root user (root squashing).
    subtree_checking:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Subtree checking.
    sync:
        default: 'sync'
        description:
            - NFS synchronisation.
    writeable:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - NFS write access.
    samba_block_size:
        description:
            - Blocking size.
        aliases: [ sambaBlockSize ]
    samba_blocking_locks:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Blocking locks.
        aliases: [ sambaBlockingLocks ]
    samba_browseable:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Show in Windows network environment.
        aliases: [ sambaBrowseable ]
    samba_create_mode:
        default: '0744'
        description:
            - File mode.
        aliases: [ sambaCreateMode ]
    samba_csc_policy:
        default: 'manual'
        description:
            - Client-side caching policy.
        aliases: [ sambaCscPolicy ]
    samba_custom_settings:
        default: []
        description:
            - Option name in smb.conf and its value.
        aliases: [ sambaCustomSettings ]
    samba_directory_mode:
        default: '0755'
        description:
            - Directory mode.
        aliases: [ sambaDirectoryMode ]
    samba_directory_security_mode:
        default: '0777'
        description:
            - Directory security mode.
        aliases: [ sambaDirectorySecurityMode ]
    samba_dos_filemode:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Users with write access may modify permissions.
        aliases: [ sambaDosFilemode ]
    samba_fake_oplocks:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Fake oplocks.
        aliases: [ sambaFakeOplocks ]
    samba_force_create_mode:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Force file mode.
        aliases: [ sambaForceCreateMode ]
    samba_force_directory_mode:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Force directory mode.
        aliases: [ sambaForceDirectoryMode ]
    samba_force_directory_security_mode:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Force directory security mode.
        aliases: [ sambaForceDirectorySecurityMode ]
    samba_force_group:
        description:
            - Force group.
        aliases: [ sambaForceGroup ]
    samba_force_security_mode:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Force security mode.
        aliases: [ sambaForceSecurityMode ]
    samba_force_user:
        description:
            - Force user.
        aliases: [ sambaForceUser ]
    samba_hide_files:
        description:
            - Hide files.
        aliases: [ sambaHideFiles ]
    samba_hide_unreadable:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Hide unreadable files/directories.
        aliases: [ sambaHideUnreadable ]
    samba_hosts_allow:
        default: []
        description:
            - Allowed host/network.
        aliases: [ sambaHostsAllow ]
    samba_hosts_deny:
        default: []
        description:
            - Denied host/network.
        aliases: [ sambaHostsDeny ]
    samba_inherit_acls:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Inherit ACLs.
        aliases: [ sambaInheritAcls ]
    samba_inherit_owner:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Create files/directories with the owner of the parent directory.
        aliases: [ sambaInheritOwner ]
    samba_inherit_permissions:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Create files/directories with permissions of the parent directory.
        aliases: [ sambaInheritPermissions ]
    samba_invalid_users:
        description:
            - Invalid users or groups.
        aliases: [ sambaInvalidUsers ]
    samba_level_2_oplocks:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Level 2 oplocks.
        aliases: [ sambaLevel2Oplocks ]
    samba_locking:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Locking.
        aliases: [ sambaLocking ]
    samba_msdfs_root:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - MSDFS root.
        aliases: [ sambaMSDFSRoot ]
    samba_nt_acl_support:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - NT ACL support.
        aliases: [ sambaNtAclSupport ]
    samba_oplocks:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Oplocks.
        aliases: [ sambaOplocks ]
    samba_postexec:
        description:
            - Postexec script.
        aliases: [ sambaPostexec ]
    samba_preexec:
        description:
            - Preexec script.
        aliases: [ sambaPreexec ]
    samba_public:
        default: '0'
        choices: [ '0', '1' ]
        description:
            - Allow anonymous read-only access with a guest user.
        aliases: [ sambaPublic ]
    samba_security_mode:
        default: '0777'
        description:
            - Security mode.
        aliases: [ sambaSecurityMode ]
    samba_strict_locking:
        default: 'Auto'
        description:
            - Strict locking.
        aliases: [ sambaStrictLocking ]
    samba_vfs_objects:
        description:
            - VFS objects.
        aliases: [ sambaVFSObjects ]
    samba_valid_users:
        description:
            - Valid users or groups.
        aliases: [ sambaValidUsers ]
    samba_write_list:
        description:
            - Restrict write access to these users/groups.
        aliases: [ sambaWriteList ]
    samba_writeable:
        default: '1'
        choices: [ '0', '1' ]
        description:
            - Samba write access.
        aliases: [ sambaWriteable ]
    nfs_hosts:
        default: []
        description:
            - Only allow access for this host, IP address or network.
    nfs_custom_settings:
        default: []
        description:
            - Option name in exports file.
        aliases: [ nfsCustomSettings ]
'''


EXAMPLES = '''
- name: Create a share named home on the server ucs.example.com with the path /home
  community.general.udm_share:
    name: home
    path: /home
    host: ucs.example.com
    sambaName: Home
'''


RETURN = '''# '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.univention_umc import (
    umc_module_for_add,
    umc_module_for_edit,
    ldap_search,
    base_dn,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True,
                      type='str'),
            ou=dict(required=True,
                    type='str'),
            owner=dict(type='str',
                       default='0'),
            group=dict(type='str',
                       default='0'),
            path=dict(type='path',
                      default=None),
            directorymode=dict(type='str',
                               default='00755'),
            host=dict(type='str',
                      default=None),
            root_squash=dict(type='bool',
                             default=True),
            subtree_checking=dict(type='bool',
                                  default=True),
            sync=dict(type='str',
                      default='sync'),
            writeable=dict(type='bool',
                           default=True),
            sambaBlockSize=dict(type='str',
                                aliases=['samba_block_size'],
                                default=None),
            sambaBlockingLocks=dict(type='bool',
                                    aliases=['samba_blocking_locks'],
                                    default=True),
            sambaBrowseable=dict(type='bool',
                                 aliases=['samba_browsable'],
                                 default=True),
            sambaCreateMode=dict(type='str',
                                 aliases=['samba_create_mode'],
                                 default='0744'),
            sambaCscPolicy=dict(type='str',
                                aliases=['samba_csc_policy'],
                                default='manual'),
            sambaCustomSettings=dict(type='list',
                                     aliases=['samba_custom_settings'],
                                     default=[]),
            sambaDirectoryMode=dict(type='str',
                                    aliases=['samba_directory_mode'],
                                    default='0755'),
            sambaDirectorySecurityMode=dict(type='str',
                                            aliases=['samba_directory_security_mode'],
                                            default='0777'),
            sambaDosFilemode=dict(type='bool',
                                  aliases=['samba_dos_filemode'],
                                  default=False),
            sambaFakeOplocks=dict(type='bool',
                                  aliases=['samba_fake_oplocks'],
                                  default=False),
            sambaForceCreateMode=dict(type='bool',
                                      aliases=['samba_force_create_mode'],
                                      default=False),
            sambaForceDirectoryMode=dict(type='bool',
                                         aliases=['samba_force_directory_mode'],
                                         default=False),
            sambaForceDirectorySecurityMode=dict(type='bool',
                                                 aliases=['samba_force_directory_security_mode'],
                                                 default=False),
            sambaForceGroup=dict(type='str',
                                 aliases=['samba_force_group'],
                                 default=None),
            sambaForceSecurityMode=dict(type='bool',
                                        aliases=['samba_force_security_mode'],
                                        default=False),
            sambaForceUser=dict(type='str',
                                aliases=['samba_force_user'],
                                default=None),
            sambaHideFiles=dict(type='str',
                                aliases=['samba_hide_files'],
                                default=None),
            sambaHideUnreadable=dict(type='bool',
                                     aliases=['samba_hide_unreadable'],
                                     default=False),
            sambaHostsAllow=dict(type='list',
                                 aliases=['samba_hosts_allow'],
                                 default=[]),
            sambaHostsDeny=dict(type='list',
                                aliases=['samba_hosts_deny'],
                                default=[]),
            sambaInheritAcls=dict(type='bool',
                                  aliases=['samba_inherit_acls'],
                                  default=True),
            sambaInheritOwner=dict(type='bool',
                                   aliases=['samba_inherit_owner'],
                                   default=False),
            sambaInheritPermissions=dict(type='bool',
                                         aliases=['samba_inherit_permissions'],
                                         default=False),
            sambaInvalidUsers=dict(type='str',
                                   aliases=['samba_invalid_users'],
                                   default=None),
            sambaLevel2Oplocks=dict(type='bool',
                                    aliases=['samba_level_2_oplocks'],
                                    default=True),
            sambaLocking=dict(type='bool',
                              aliases=['samba_locking'],
                              default=True),
            sambaMSDFSRoot=dict(type='bool',
                                aliases=['samba_msdfs_root'],
                                default=False),
            sambaName=dict(type='str',
                           aliases=['samba_name'],
                           default=None),
            sambaNtAclSupport=dict(type='bool',
                                   aliases=['samba_nt_acl_support'],
                                   default=True),
            sambaOplocks=dict(type='bool',
                              aliases=['samba_oplocks'],
                              default=True),
            sambaPostexec=dict(type='str',
                               aliases=['samba_postexec'],
                               default=None),
            sambaPreexec=dict(type='str',
                              aliases=['samba_preexec'],
                              default=None),
            sambaPublic=dict(type='bool',
                             aliases=['samba_public'],
                             default=False),
            sambaSecurityMode=dict(type='str',
                                   aliases=['samba_security_mode'],
                                   default='0777'),
            sambaStrictLocking=dict(type='str',
                                    aliases=['samba_strict_locking'],
                                    default='Auto'),
            sambaVFSObjects=dict(type='str',
                                 aliases=['samba_vfs_objects'],
                                 default=None),
            sambaValidUsers=dict(type='str',
                                 aliases=['samba_valid_users'],
                                 default=None),
            sambaWriteList=dict(type='str',
                                aliases=['samba_write_list'],
                                default=None),
            sambaWriteable=dict(type='bool',
                                aliases=['samba_writeable'],
                                default=True),
            nfs_hosts=dict(type='list',
                           default=[]),
            nfsCustomSettings=dict(type='list',
                                   aliases=['nfs_custom_settings'],
                                   default=[]),
            state=dict(default='present',
                       choices=['present', 'absent'],
                       type='str')
        ),
        supports_check_mode=True,
        required_if=([
            ('state', 'present', ['path', 'host', 'sambaName'])
        ])
    )
    name = module.params['name']
    state = module.params['state']
    changed = False
    diff = None

    obj = list(ldap_search(
        '(&(objectClass=univentionShare)(cn={0}))'.format(name),
        attr=['cn']
    ))

    exists = bool(len(obj))
    container = 'cn=shares,ou={0},{1}'.format(module.params['ou'], base_dn())
    dn = 'cn={0},{1}'.format(name, container)

    if state == 'present':
        try:
            if not exists:
                obj = umc_module_for_add('shares/share', container)
            else:
                obj = umc_module_for_edit('shares/share', dn)

            module.params['printablename'] = '{0} ({1})'.format(name, module.params['host'])
            for k in obj.keys():
                if module.params[k] is True:
                    module.params[k] = '1'
                elif module.params[k] is False:
                    module.params[k] = '0'
                obj[k] = module.params[k]

            diff = obj.diff()
            if exists:
                for k in obj.keys():
                    if obj.hasChanged(k):
                        changed = True
            else:
                changed = True
            if not module.check_mode:
                if not exists:
                    obj.create()
                elif changed:
                    obj.modify()
        except Exception as err:
            module.fail_json(
                msg='Creating/editing share {0} in {1} failed: {2}'.format(
                    name,
                    container,
                    err,
                )
            )

    if state == 'absent' and exists:
        try:
            obj = umc_module_for_edit('shares/share', dn)
            if not module.check_mode:
                obj.remove()
            changed = True
        except Exception as err:
            module.fail_json(
                msg='Removing share {0} in {1} failed: {2}'.format(
                    name,
                    container,
                    err,
                )
            )

    module.exit_json(
        changed=changed,
        name=name,
        diff=diff,
        container=container
    )


if __name__ == '__main__':
    main()
