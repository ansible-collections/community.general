#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Nate Coraor <nate@coraor.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zfs_delegate_admin
short_description: Manage ZFS delegated administration (user admin privileges)
description:
  - Manages ZFS file system delegated administration permissions, which allow unprivileged users to perform ZFS
    operations normally restricted to the superuser.
  - See the C(zfs allow) section of V(zfs(1M\)) for detailed explanations of options.
  - This module attempts to adhere to the behavior of the command line tool as much as possible.
requirements:
  - "A ZFS/OpenZFS implementation that supports delegation with C(zfs allow), including: Solaris >= 10, illumos (all
    versions), FreeBSD >= 8.0R, ZFS on Linux >= 0.7.0."
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  name:
    description:
      - File system or volume name, for example V(rpool/myfs).
    required: true
    type: str
  state:
    description:
      - Whether to allow (V(present)), or unallow (V(absent)) a permission.
      - When set to V(present), at least one "entity" param of O(users), O(groups), or O(everyone) are required.
      - When set to V(absent), removes permissions from the specified entities, or removes all permissions if no entity params are specified.
    choices: [ absent, present ]
    default: present
    type: str
  users:
    description:
      - List of users to whom permission(s) should be granted.
    type: list
    elements: str
  groups:
    description:
      - List of groups to whom permission(s) should be granted.
    type: list
    elements: str
  everyone:
    description:
      - Apply permissions to everyone.
    type: bool
    default: false
  permissions:
    description:
      - The list of permission(s) to delegate (required if O(state=present)).
      - Supported permissions depend on the ZFS version in use. See for example
        U(https://openzfs.github.io/openzfs-docs/man/8/zfs-allow.8.html) for OpenZFS.
    type: list
    elements: str
  local:
    description:
      - Apply permissions to O(name) locally (C(zfs allow -l)).
    type: bool
  descendents:
    description:
      - Apply permissions to O(name)'s descendents (C(zfs allow -d)).
    type: bool
  recursive:
    description:
      - Unallow permissions recursively (ignored when O(state=present)).
    type: bool
    default: false
author:
- Nate Coraor (@natefoo)
'''

EXAMPLES = r'''
- name: Grant `zfs allow` and `unallow` permission to the `adm` user with the default local+descendents scope
  community.general.zfs_delegate_admin:
    name: rpool/myfs
    users: adm
    permissions: allow,unallow

- name: Grant `zfs send` to everyone, plus the group `backup`
  community.general.zfs_delegate_admin:
    name: rpool/myvol
    groups: backup
    everyone: true
    permissions: send

- name: Grant `zfs send,receive` to users `foo` and `bar` with local scope only
  community.general.zfs_delegate_admin:
    name: rpool/myfs
    users: foo,bar
    permissions: send,receive
    local: true

- name: Revoke all permissions from everyone (permissions specifically assigned to users and groups remain)
  community.general.zfs_delegate_admin:
    name: rpool/myfs
    everyone: true
    state: absent
'''

# This module does not return anything other than the standard
# changed/state/msg/stdout
RETURN = '''
'''

from itertools import product

from ansible.module_utils.basic import AnsibleModule


class ZfsDelegateAdmin(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params.get('name')
        self.state = module.params.get('state')
        self.users = module.params.get('users')
        self.groups = module.params.get('groups')
        self.everyone = module.params.get('everyone')
        self.perms = module.params.get('permissions')
        self.scope = None
        self.changed = False
        self.initial_perms = None
        self.subcommand = 'allow'
        self.recursive_opt = []
        self.run_method = self.update

        self.setup(module)

    def setup(self, module):
        """ Validate params and set up for run.
        """
        if self.state == 'absent':
            self.subcommand = 'unallow'
            if module.params.get('recursive'):
                self.recursive_opt = ['-r']

        local = module.params.get('local')
        descendents = module.params.get('descendents')
        if (local and descendents) or (not local and not descendents):
            self.scope = 'ld'
        elif local:
            self.scope = 'l'
        elif descendents:
            self.scope = 'd'
        else:
            self.module.fail_json(msg='Impossible value for local and descendents')

        if not (self.users or self.groups or self.everyone):
            if self.state == 'present':
                self.module.fail_json(msg='One of `users`, `groups`, or `everyone` must be set')
            elif self.state == 'absent':
                self.run_method = self.clear
            # ansible ensures the else cannot happen here

        self.zfs_path = module.get_bin_path('zfs', True)

    @property
    def current_perms(self):
        """ Parse the output of `zfs allow <name>` to retrieve current permissions.
        """
        out = self.run_zfs_raw(subcommand='allow')
        perms = {
            'l': {'u': {}, 'g': {}, 'e': []},
            'd': {'u': {}, 'g': {}, 'e': []},
            'ld': {'u': {}, 'g': {}, 'e': []},
        }
        linemap = {
            'Local permissions:': 'l',
            'Descendent permissions:': 'd',
            'Local+Descendent permissions:': 'ld',
        }
        scope = None
        for line in out.splitlines():
            scope = linemap.get(line, scope)
            if not scope:
                continue
            if ' (unknown: ' in line:
                line = line.replace('(unknown: ', '', 1)
                line = line.replace(')', '', 1)
            try:
                if line.startswith('\tuser ') or line.startswith('\tgroup '):
                    ent_type, ent, cur_perms = line.split()
                    perms[scope][ent_type[0]][ent] = cur_perms.split(',')
                elif line.startswith('\teveryone '):
                    perms[scope]['e'] = line.split()[1].split(',')
            except ValueError:
                self.module.fail_json(msg="Cannot parse user/group permission output by `zfs allow`: '%s'" % line)
        return perms

    def run_zfs_raw(self, subcommand=None, args=None):
        """ Run a raw zfs command, fail on error.
        """
        cmd = [self.zfs_path, subcommand or self.subcommand] + (args or []) + [self.name]
        rc, out, err = self.module.run_command(cmd)
        if rc:
            self.module.fail_json(msg='Command `%s` failed: %s' % (' '.join(cmd), err))
        return out

    def run_zfs(self, args):
        """ Run zfs allow/unallow with appropriate options as per module arguments.
        """
        args = self.recursive_opt + ['-' + self.scope] + args
        if self.perms:
            args.append(','.join(self.perms))
        return self.run_zfs_raw(args=args)

    def clear(self):
        """ Called by run() to clear all permissions.
        """
        changed = False
        stdout = ''
        for scope, ent_type in product(('ld', 'l', 'd'), ('u', 'g')):
            for ent in self.initial_perms[scope][ent_type].keys():
                stdout += self.run_zfs(['-%s' % ent_type, ent])
                changed = True
        for scope in ('ld', 'l', 'd'):
            if self.initial_perms[scope]['e']:
                stdout += self.run_zfs(['-e'])
                changed = True
        return (changed, stdout)

    def update(self):
        """ Update permissions as per module arguments.
        """
        stdout = ''
        for ent_type, entities in (('u', self.users), ('g', self.groups)):
            if entities:
                stdout += self.run_zfs(['-%s' % ent_type, ','.join(entities)])
        if self.everyone:
            stdout += self.run_zfs(['-e'])
        return (self.initial_perms != self.current_perms, stdout)

    def run(self):
        """ Run an operation, return results for Ansible.
        """
        exit_args = {'state': self.state}
        self.initial_perms = self.current_perms
        exit_args['changed'], stdout = self.run_method()
        if exit_args['changed']:
            exit_args['msg'] = 'ZFS delegated admin permissions updated'
            exit_args['stdout'] = stdout
        self.module.exit_json(**exit_args)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            users=dict(type='list', elements='str'),
            groups=dict(type='list', elements='str'),
            everyone=dict(type='bool', default=False),
            permissions=dict(type='list', elements='str'),
            local=dict(type='bool'),
            descendents=dict(type='bool'),
            recursive=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
        required_if=[('state', 'present', ['permissions'])],
    )
    zfs_delegate_admin = ZfsDelegateAdmin(module)
    zfs_delegate_admin.run()


if __name__ == '__main__':
    main()
