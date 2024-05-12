#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_user_info
short_description: Retrieve information about one or more Proxmox VE users
version_added: 1.3.0
description:
  - Retrieve information about one or more Proxmox VE users
attributes:
  action_group:
    version_added: 9.0.0
options:
  domain:
    description:
      - Restrict results to a specific authentication realm.
    aliases: ['realm']
    type: str
  user:
    description:
      - Restrict results to a specific user.
    aliases: ['name']
    type: str
  userid:
    description:
      - Restrict results to a specific user ID, which is a concatenation of a user and domain parts.
    type: str
author: Tristan Le Guern (@tleguern)
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
'''

EXAMPLES = '''
- name: List existing users
  community.general.proxmox_user_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
  register: proxmox_users

- name: List existing users in the pve authentication realm
  community.general.proxmox_user_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    domain: pve
  register: proxmox_users_pve

- name: Retrieve information about admin@pve
  community.general.proxmox_user_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    userid: admin@pve
  register: proxmox_user_admin

- name: Alternative way to retrieve information about admin@pve
  community.general.proxmox_user_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    user: admin
    domain: pve
  register: proxmox_user_admin
'''


RETURN = '''
proxmox_users:
    description: List of users.
    returned: always, but can be empty
    type: list
    elements: dict
    contains:
      comment:
        description: Short description of the user.
        returned: on success
        type: str
      domain:
        description: User's authentication realm, also the right part of the user ID.
        returned: on success
        type: str
      email:
        description: User's email address.
        returned: on success
        type: str
      enabled:
        description: User's account state.
        returned: on success
        type: bool
      expire:
        description: Expiration date in seconds since EPOCH. Zero means no expiration.
        returned: on success
        type: int
      firstname:
        description: User's first name.
        returned: on success
        type: str
      groups:
        description: List of groups which the user is a member of.
        returned: on success
        type: list
        elements: str
      keys:
        description: User's two factor authentication keys.
        returned: on success
        type: str
      lastname:
        description: User's last name.
        returned: on success
        type: str
      tokens:
        description: List of API tokens associated to the user.
        returned: on success
        type: list
        elements: dict
        contains:
          comment:
            description: Short description of the token.
            returned: on success
            type: str
          expire:
            description: Expiration date in seconds since EPOCH. Zero means no expiration.
            returned: on success
            type: int
          privsep:
            description: Describe if the API token is further restricted with ACLs or is fully privileged.
            returned: on success
            type: bool
          tokenid:
            description: Token name.
            returned: on success
            type: str
      user:
        description: User's login name, also the left part of the user ID.
        returned: on success
        type: str
      userid:
        description: Proxmox user ID, represented as user@realm.
        returned: on success
        type: str
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, proxmox_to_ansible_bool)


class ProxmoxUserInfoAnsible(ProxmoxAnsible):
    def get_user(self, userid):
        try:
            user = self.proxmox_api.access.users.get(userid)
        except Exception:
            self.module.fail_json(msg="User '%s' does not exist" % userid)
        user['userid'] = userid
        return ProxmoxUser(user)

    def get_users(self, domain=None):
        users = self.proxmox_api.access.users.get(full=1)
        users = [ProxmoxUser(user) for user in users]
        if domain:
            return [user for user in users if user.user['domain'] == domain]
        return users


class ProxmoxUser:
    def __init__(self, user):
        self.user = dict()
        # Data representation is not the same depending on API calls
        for k, v in user.items():
            if k == 'enable':
                self.user['enabled'] = proxmox_to_ansible_bool(user['enable'])
            elif k == 'userid':
                self.user['user'] = user['userid'].split('@')[0]
                self.user['domain'] = user['userid'].split('@')[1]
                self.user[k] = v
            elif k in ['groups', 'tokens'] and (v == '' or v is None):
                self.user[k] = []
            elif k == 'groups' and isinstance(v, str):
                self.user['groups'] = v.split(',')
            elif k == 'tokens' and isinstance(v, list):
                for token in v:
                    if 'privsep' in token:
                        token['privsep'] = proxmox_to_ansible_bool(token['privsep'])
                self.user['tokens'] = v
            elif k == 'tokens' and isinstance(v, dict):
                self.user['tokens'] = list()
                for tokenid, tokenvalues in v.items():
                    t = tokenvalues
                    t['tokenid'] = tokenid
                    if 'privsep' in tokenvalues:
                        t['privsep'] = proxmox_to_ansible_bool(tokenvalues['privsep'])
                    self.user['tokens'].append(t)
            else:
                self.user[k] = v


def proxmox_user_info_argument_spec():
    return dict(
        domain=dict(type='str', aliases=['realm']),
        user=dict(type='str', aliases=['name']),
        userid=dict(type='str'),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    user_info_args = proxmox_user_info_argument_spec()
    module_args.update(user_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        mutually_exclusive=[('user', 'userid'), ('domain', 'userid')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    proxmox = ProxmoxUserInfoAnsible(module)
    domain = module.params['domain']
    user = module.params['user']
    if user and domain:
        userid = user + '@' + domain
    else:
        userid = module.params['userid']

    if userid:
        users = [proxmox.get_user(userid=userid)]
    else:
        users = proxmox.get_users(domain=domain)
    result['proxmox_users'] = [user.user for user in users]

    module.exit_json(**result)


if __name__ == '__main__':
    main()
