#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_group_info
short_description: Retrieve information about one or more Proxmox VE groups
version_added: 1.3.0
description:
  - Retrieve information about one or more Proxmox VE groups
options:
  group:
    description:
      - Restrict results to a specific group.
    aliases: ['groupid', 'name']
    type: str
author: Tristan Le Guern (@Aversiste)
extends_documentation_fragment: community.general.proxmox.documentation
'''


EXAMPLES = '''
- name: List existing groups
  community.general.proxmox_group_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
  register: proxmox_groups

- name: Retrieve information about the admin group
  community.general.proxmox_group_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    group: admin
  register: proxmox_group_admin
'''


RETURN = '''
proxmox_groups:
    description: List of groups.
    returned: always, but can be empty
    type: list
    elements: dict
    contains:
      comment:
        description: Short description of the group.
        returned: on success, can be absent
        type: str
      groupid:
        description: Group name.
        returned: on success
        type: str
      users:
        description: List of users in the group.
        returned: on success
        type: list
        elements: str
'''


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR)


class ProxmoxGroupInfoAnsible(ProxmoxAnsible):
    def get_group(self, groupid):
        try:
            group = self.proxmox_api.access.groups.get(groupid)
        except Exception:
            self.module.fail_json(msg="Group '%s' does not exist" % groupid)
        group['groupid'] = groupid
        return ProxmoxGroup(group)

    def get_groups(self):
        groups = self.proxmox_api.access.groups.get()
        return [ProxmoxGroup(group) for group in groups]


class ProxmoxGroup:
    def __init__(self, group):
        self.group = dict()
        # Data representation is not the same depending on API calls
        for k, v in group.items():
            if k == 'users' and type(v) == str:
                self.group['users'] = v.split(',')
            elif k == 'members':
                self.group['users'] = group['members']
            else:
                self.group[k] = v


def proxmox_group_info_argument_spec():
    return dict(
        group=dict(type='str', aliases=['groupid', 'name']),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    group_info_args = proxmox_group_info_argument_spec()
    module_args.update(group_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

    proxmox = ProxmoxGroupInfoAnsible(module)
    group = module.params['group']

    if group:
        groups = [proxmox.get_group(group=group)]
    else:
        groups = proxmox.get_groups()
    result['proxmox_groups'] = [group.group for group in groups]

    module.exit_json(**result)


if __name__ == '__main__':
    main()
