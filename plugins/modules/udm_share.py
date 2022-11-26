#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Adfinis SyGroup AG
# Tobias Rueetschi <tobias.ruetschi@adfinis-sygroup.ch>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
        type: str
    name:
        required: true
        description:
            - Name
        type: str
    host:
        required: false
        description:
            - Host FQDN (server which provides the share), e.g. C({{
              ansible_fqdn }}). Required if I(state=present).
        type: str
    path:
        required: false
        description:
            - Directory on the providing server, e.g. C(/home). Required if I(state=present).
        type: path
    sambaName:
        required: false
        description:
            - Windows name. Required if I(state=present).
        type: str
        aliases: [ samba_name ]
    ou:
        required: true
        description:
            - Organisational unit, inside the LDAP Base DN.
        type: str
    owner:
        default: '0'
        description:
            - Directory owner of the share's root directory.
        type: str
    group:
        default: '0'
        description:
            - Directory owner group of the share's root directory.
        type: str
    directorymode:
        default: '00755'
        description:
            - Permissions for the share's root directory.
        type: str
    root_squash:
        default: true
        description:
            - Modify user ID for root user (root squashing).
        type: bool
    subtree_checking:
        default: true
        description:
            - Subtree checking.
        type: bool
    sync:
        default: 'sync'
        description:
            - NFS synchronisation.
        type: str
    writeable:
        default: true
        description:
            - NFS write access.
        type: bool
    sambaBlockSize:
        description:
            - Blocking size.
        type: str
        aliases: [ samba_block_size ]
    sambaBlockingLocks:
        default: true
        description:
            - Blocking locks.
        type: bool
        aliases: [ samba_blocking_locks ]
    sambaBrowseable:
        description:
        - Show in Windows network environment.
        type: bool
        default: true
        aliases: [ samba_browsable ]
    sambaCreateMode:
        default: '0744'
        description:
            - File mode.
        type: str
        aliases: [ samba_create_mode ]
    sambaCscPolicy:
        default: 'manual'
        description:
            - Client-side caching policy.
        type: str
        aliases: [ samba_csc_policy ]
    sambaCustomSettings:
        default: []
        description:
            - Option name in smb.conf and its value.
        type: list
        elements: dict
        aliases: [ samba_custom_settings ]
    sambaDirectoryMode:
        default: '0755'
        description:
            - Directory mode.
        type: str
        aliases: [ samba_directory_mode ]
    sambaDirectorySecurityMode:
        default: '0777'
        description:
            - Directory security mode.
        type: str
        aliases: [ samba_directory_security_mode ]
    sambaDosFilemode:
        default: false
        description:
            - Users with write access may modify permissions.
        type: bool
        aliases: [ samba_dos_filemode ]
    sambaFakeOplocks:
        default: false
        description:
            - Fake oplocks.
        type: bool
        aliases: [ samba_fake_oplocks ]
    sambaForceCreateMode:
        default: false
        description:
            - Force file mode.
        type: bool
        aliases: [ samba_force_create_mode ]
    sambaForceDirectoryMode:
        default: false
        description:
            - Force directory mode.
        type: bool
        aliases: [ samba_force_directory_mode ]
    sambaForceDirectorySecurityMode:
        default: false
        description:
            - Force directory security mode.
        type: bool
        aliases: [ samba_force_directory_security_mode ]
    sambaForceGroup:
        description:
            - Force group.
        type: str
        aliases: [ samba_force_group ]
    sambaForceSecurityMode:
        default: false
        description:
            - Force security mode.
        type: bool
        aliases: [ samba_force_security_mode ]
    sambaForceUser:
        description:
            - Force user.
        type: str
        aliases: [ samba_force_user ]
    sambaHideFiles:
        description:
            - Hide files.
        type: str
        aliases: [ samba_hide_files ]
    sambaHideUnreadable:
        default: false
        description:
            - Hide unreadable files/directories.
        type: bool
        aliases: [ samba_hide_unreadable ]
    sambaHostsAllow:
        default: []
        description:
            - Allowed host/network.
        type: list
        elements: str
        aliases: [ samba_hosts_allow ]
    sambaHostsDeny:
        default: []
        description:
            - Denied host/network.
        type: list
        elements: str
        aliases: [ samba_hosts_deny ]
    sambaInheritAcls:
        default: true
        description:
            - Inherit ACLs.
        type: bool
        aliases: [ samba_inherit_acls ]
    sambaInheritOwner:
        default: false
        description:
            - Create files/directories with the owner of the parent directory.
        type: bool
        aliases: [ samba_inherit_owner ]
    sambaInheritPermissions:
        default: false
        description:
            - Create files/directories with permissions of the parent directory.
        type: bool
        aliases: [ samba_inherit_permissions ]
    sambaInvalidUsers:
        description:
            - Invalid users or groups.
        type: str
        aliases: [ samba_invalid_users ]
    sambaLevel2Oplocks:
        default: true
        description:
            - Level 2 oplocks.
        type: bool
        aliases: [ samba_level_2_oplocks ]
    sambaLocking:
        default: true
        description:
            - Locking.
        type: bool
        aliases: [ samba_locking ]
    sambaMSDFSRoot:
        default: false
        description:
            - MSDFS root.
        type: bool
        aliases: [ samba_msdfs_root ]
    sambaNtAclSupport:
        default: true
        description:
            - NT ACL support.
        type: bool
        aliases: [ samba_nt_acl_support ]
    sambaOplocks:
        default: true
        description:
            - Oplocks.
        type: bool
        aliases: [ samba_oplocks ]
    sambaPostexec:
        description:
            - Postexec script.
        type: str
        aliases: [ samba_postexec ]
    sambaPreexec:
        description:
            - Preexec script.
        type: str
        aliases: [ samba_preexec ]
    sambaPublic:
        default: false
        description:
            - Allow anonymous read-only access with a guest user.
        type: bool
        aliases: [ samba_public ]
    sambaSecurityMode:
        default: '0777'
        description:
            - Security mode.
        type: str
        aliases: [ samba_security_mode ]
    sambaStrictLocking:
        default: 'Auto'
        description:
            - Strict locking.
        type: str
        aliases: [ samba_strict_locking ]
    sambaVFSObjects:
        description:
            - VFS objects.
        type: str
        aliases: [ samba_vfs_objects ]
    sambaValidUsers:
        description:
            - Valid users or groups.
        type: str
        aliases: [ samba_valid_users ]
    sambaWriteList:
        description:
            - Restrict write access to these users/groups.
        type: str
        aliases: [ samba_write_list ]
    sambaWriteable:
        default: true
        description:
            - Samba write access.
        type: bool
        aliases: [ samba_writeable ]
    nfs_hosts:
        default: []
        description:
            - Only allow access for this host, IP address or network.
        type: list
        elements: str
    nfsCustomSettings:
        default: []
        description:
            - Option name in exports file.
        type: list
        elements: str
        aliases: [ nfs_custom_settings ]
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
            path=dict(type='path'),
            directorymode=dict(type='str',
                               default='00755'),
            host=dict(type='str'),
            root_squash=dict(type='bool',
                             default=True),
            subtree_checking=dict(type='bool',
                                  default=True),
            sync=dict(type='str',
                      default='sync'),
            writeable=dict(type='bool',
                           default=True),
            sambaBlockSize=dict(type='str',
                                aliases=['samba_block_size']),
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
                                     elements='dict',
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
                                 aliases=['samba_force_group']),
            sambaForceSecurityMode=dict(type='bool',
                                        aliases=['samba_force_security_mode'],
                                        default=False),
            sambaForceUser=dict(type='str',
                                aliases=['samba_force_user']),
            sambaHideFiles=dict(type='str',
                                aliases=['samba_hide_files']),
            sambaHideUnreadable=dict(type='bool',
                                     aliases=['samba_hide_unreadable'],
                                     default=False),
            sambaHostsAllow=dict(type='list',
                                 elements='str',
                                 aliases=['samba_hosts_allow'],
                                 default=[]),
            sambaHostsDeny=dict(type='list',
                                elements='str',
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
                                   aliases=['samba_invalid_users']),
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
                           aliases=['samba_name']),
            sambaNtAclSupport=dict(type='bool',
                                   aliases=['samba_nt_acl_support'],
                                   default=True),
            sambaOplocks=dict(type='bool',
                              aliases=['samba_oplocks'],
                              default=True),
            sambaPostexec=dict(type='str',
                               aliases=['samba_postexec']),
            sambaPreexec=dict(type='str',
                              aliases=['samba_preexec']),
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
                                 aliases=['samba_vfs_objects']),
            sambaValidUsers=dict(type='str',
                                 aliases=['samba_valid_users']),
            sambaWriteList=dict(type='str',
                                aliases=['samba_write_list']),
            sambaWriteable=dict(type='bool',
                                aliases=['samba_writeable'],
                                default=True),
            nfs_hosts=dict(type='list',
                           elements='str',
                           default=[]),
            nfsCustomSettings=dict(type='list',
                                   elements='str',
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
