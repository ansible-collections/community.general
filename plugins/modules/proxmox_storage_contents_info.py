#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Julian Vanden Broeck (@l00ptr) <julian.vandenbroeck at dalibo.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: proxmox_storage_contents_info
short_description: List content from a Proxmox VE storage
version_added: 8.2.0
description:
  - Retrieves information about stored objects on a specific storage attached to a node.
attributes:
  action_group:
    version_added: 9.0.0
options:
  storage:
    description:
      - Only return content stored on that specific storage.
    aliases: ['name']
    type: str
    required: true
  node:
    description:
      - Proxmox node to which the storage is attached.
    type: str
    required: true
  content:
    description:
      - Filter on a specific content type.
    type: str
    choices: ["all", "backup", "rootdir", "images", "iso"]
    default: "all"
  vmid:
    description:
      - Filter on a specific VMID.
    type: int
author: Julian Vanden Broeck (@l00ptr)
extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
"""


EXAMPLES = r"""
- name: List existing storages
  community.general.proxmox_storage_contents_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    storage: lvm2
    content: backup
    vmid: 130
"""


RETURN = r"""
proxmox_storage_content:
  description: Content of of storage attached to a node.
  type: list
  returned: success
  elements: dict
  contains:
    content:
      description: Proxmox content of listed objects on this storage.
      type: str
      returned: success
    ctime:
      description: Creation time of the listed objects.
      type: str
      returned: success
    format:
      description: Format of the listed objects (can be V(raw), V(pbs-vm), V(iso),...).
      type: str
      returned: success
    size:
      description: Size of the listed objects.
      type: int
      returned: success
    subtype:
      description: Subtype of the listed objects (can be V(qemu) or V(lxc)).
      type: str
      returned: When storage is dedicated to backup, typically on PBS storage.
    verification:
      description: Backup verification status of the listed objects.
      type: dict
      returned: When storage is dedicated to backup, typically on PBS storage.
      sample: {
        "state": "ok",
        "upid": "UPID:backup-srv:00130F49:1A12D8375:00001CD7:657A2258:verificationjob:daily\\x3av\\x2dd0cc18c5\\x2d8707:root@pam:"
        }
    volid:
      description: Volume identifier of the listed objects.
      type: str
      returned: success
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    ProxmoxAnsible, proxmox_auth_argument_spec)


def proxmox_storage_info_argument_spec():
    return dict(
        storage=dict(type="str", required=True, aliases=["name"]),
        content=dict(type="str", required=False, default="all", choices=["all", "backup", "rootdir", "images", "iso"]),
        vmid=dict(type="int"),
        node=dict(required=True, type="str"),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    storage_info_args = proxmox_storage_info_argument_spec()
    module_args.update(storage_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[("api_password", "api_token_id")],
        required_together=[("api_token_id", "api_token_secret")],
        supports_check_mode=True,
    )
    result = dict(changed=False)
    proxmox = ProxmoxAnsible(module)
    res = proxmox.get_storage_content(
        node=module.params["node"],
        storage=module.params["storage"],
        content=None if module.params["content"] == "all" else module.params["content"],
        vmid=module.params["vmid"],
    )
    result["proxmox_storage_content"] = res
    module.exit_json(**result)


if __name__ == "__main__":
    main()
