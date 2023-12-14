#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Tristan Le Guern (@tleguern) <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_storage_info
short_description: Retrieve information about one or more Proxmox VE storages
version_added: 2.2.0
description:
  - Retrieve information about one or more Proxmox VE storages.
options:
  storage:
    description:
      - Only return information on a specific storage.
    aliases: ['name']
    type: str
  type:
    description:
      - Filter on a specific storage type.
    type: str
author: Tristan Le Guern (@tleguern)
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
notes:
  - Storage specific options can be returned by this module, please look at the documentation at U(https://pve.proxmox.com/wiki/Storage).
'''


EXAMPLES = '''
- name: List existing storages
  community.general.proxmox_storage_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
  register: proxmox_storages

- name: List NFS storages only
  community.general.proxmox_storage_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    type: nfs
  register: proxmox_storages_nfs

- name: Retrieve information about the lvm2 storage
  community.general.proxmox_storage_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    storage: lvm2
  register: proxmox_storage_lvm
'''


RETURN = '''
proxmox_storages:
  description: List of storage pools.
  returned: on success
  type: list
  elements: dict
  contains:
    content:
      description: Proxmox content types available in this storage
      returned: on success
      type: list
      elements: str
    digest:
      description: Storage's digest
      returned: on success
      type: str
    nodes:
      description: List of nodes associated to this storage
      returned: on success, if storage is not local
      type: list
      elements: str
    path:
      description: Physical path to this storage
      returned: on success
      type: str
    prune-backups:
      description: Backup retention options
      returned: on success
      type: list
      elements: dict
    shared:
      description: Is this storage shared
      returned: on success
      type: bool
    storage:
      description: Storage name
      returned: on success
      type: str
    type:
      description: Storage type
      returned: on success
      type: str
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible)


def proxmox_storage_info_argument_spec():
    return dict(
        storage=dict(type='str', aliases=['name']),
        type=dict(type='str'),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    storage_info_args = proxmox_storage_info_argument_spec()
    module_args.update(storage_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        mutually_exclusive=[('storage', 'type')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    storage = module.params['storage']
    storagetype = module.params['type']
    proxmox = ProxmoxAnsible(module)

    if storage:
        storages = [proxmox.get_storage(storage)]
    else:
        storages = proxmox.get_storages_as_objects(type=storagetype)
    result['proxmox_storages'] = [storage.storage for storage in storages]

    module.exit_json(**result)


if __name__ == '__main__':
    main()
