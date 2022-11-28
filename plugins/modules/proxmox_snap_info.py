#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Jeffrey van Pelt (@Thulium-Drake) <jeff@vanpelt.one>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_snap_info
short_description: Snapshot management of instances in Proxmox VE cluster
version_added: 2.0.0
description:
  - Allows you to create/delete/restore snapshots from instances in Proxmox VE cluster.
  - Supports both KVM and LXC, OpenVZ has not been tested, as it is no longer supported on Proxmox VE.
options:
  hostname:
    description:
      - The instance name.
    type: str
  vmid:
    description:
      - The instance id.
      - If not set, will be fetched from PromoxAPI based on the hostname.
    type: str
  timeout:
    description:
      - Timeout for operations.
    default: 30
    type: int
  snapname:
    description:
      - Name of the snapshot that has to be created/deleted/restored.
    default: ''
    type: str
  getsnapshots:
    description:
      - Lists all snapshots of a vm
      - to be optionally combined with older_than
      - to be optionally combine with snapname (finds snapshot starting with the snapname)
    default: false
    type: bool
  older_than:
    description:
      - Minimum age of backup to be listed by getsnapshots in days
    default: 0
    type: int

notes:
  - Requires proxmoxer and requests modules on host. These modules can be installed with pip.
  - Supports C(check_mode).
requirements: [ "proxmoxer", "python >= 2.7", "requests" ]
author: Jeffrey van Pelt (@Thulium-Drake)
extends_documentation_fragment:
    - community.general.proxmox.documentation
'''

EXAMPLES = r'''

- name: Get all snapshots older than 2 days
  community.general.proxmox_snap_info:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    getsnapshots: True
    older_than: 2
    snapname: snapshot_
  register: snaplist

- name: delete Snapshots from list
  community.general.proxmox_snap:
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    vmid: 100
    snapname: "{{ item }}"
    state: absent
  loop: "{{ snaplist['results'] }}"
'''

RETURN = r'''#'''

import time

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

import traceback

try:
    from ansible_collections.community.general.plugins.modules.proxmox_snap import (ProxmoxSnapAnsible)

    HAS_PROXMOX_SNAP = True
    PROXMOX_SNAP_IMPORT_ERROR = None
except ImportError:
    HAS_PROXMOX_SNAP = False
    PROXMOX_SNAP_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PROXMOX_SNAP = True

from ansible_collections.community.general.plugins.module_utils.proxmox import (
    ansible_to_proxmox_bool, proxmox_auth_argument_spec, ProxmoxAnsible)


def main():
    module_args = proxmox_auth_argument_spec()
    snap_args = dict(
        vmid=dict(required=False),
        hostname=dict(),
        timeout=dict(type='int', default=30),
        snapname=dict(type='str', default=''),
        getsnapshots=dict(type='bool', default=False),
        older_than=dict(type='int', default=0)
    )
    module_args.update(snap_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_PROXMOX_SNAP:
        # Needs: from ansible.module_utils.basic import missing_required_lib
        module.fail_json(
            msg=missing_required_lib('proxmox_snap'),
            exception=PROXMOX_SNAP_IMPORT_ERROR)

    proxmox = ProxmoxSnapAnsible(module)

    vmid = module.params['vmid']
    hostname = module.params['hostname']
    snapname = module.params['snapname']
    timeout = module.params['timeout']
    getsnapshots = module.params['getsnapshots']
    older_than = module.params['older_than']

    # If hostname is set get the VM id from ProxmoxAPI
    if not vmid and hostname:
        vmid = proxmox.get_vmid(hostname)
    elif not vmid:
        module.exit_json(changed=False, msg="Vmid could not be fetched")

    vm = proxmox.get_vm(vmid)

    if getsnapshots:
        snapshotlist = proxmox.snapshot(vm, vmid).get()
        oldsnapshotlist = []

        for s in snapshotlist:
            if s["name"] == "current":
                continue
            if snapname != '':
                if not s["name"][0:len(snapname)] == snapname:
                    continue
            if ((time.time() - s["snaptime"]) / 60 / 60 / 24) > older_than:
                oldsnapshotlist.append(s["name"])

        snapshotdict = {"results": oldsnapshotlist, "older_than": older_than}

        module.exit_json(**snapshotdict)


if __name__ == '__main__':
    main()
