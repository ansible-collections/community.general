#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024 Marzieh Raoufnezhad <raoufnezhad at gmail.com>
# Copyright (c) 2024 Maryam Mayabi <mayabi.ahm at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
module: proxmox_backup_info

short_description: Retrieve information on Proxmox scheduled backups

version_added: 10.3.0

description:
  - Retrieve information such as backup times, VM name, VM ID, mode, backup type, and backup schedule using the Proxmox Server API.

author:
  - "Marzieh Raoufnezhad (@raoufnezhad) <raoufnezhad@gmail.com>"
  - "Maryam Mayabi (@mmayabi) <mayabi.ahm@gmail.com>"

options:
  vm_name:
    description:
      - The name of the Proxmox VM.
      - If defined, the returned list will contain backup jobs that have been parsed and filtered based on O(vm_name) value.
      - Mutually exclusive with O(vm_id) and O(backup_jobs).
    type: str
  vm_id:
    description:
      - The ID of the Proxmox VM.
      - If defined, the returned list will contain backup jobs that have been parsed and filtered based on O(vm_id) value.
      - Mutually exclusive with O(vm_name) and O(backup_jobs).
    type: str
  backup_jobs:
    description:
      - If V(true), the module will return all backup jobs information.
      - If V(false), the module will parse all backup jobs based on VM IDs and return a list of VMs' backup information.
      - Mutually exclusive with O(vm_id) and O(vm_name).
    default: false
    type: bool

extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.proxmox.actiongroup_proxmox
"""

EXAMPLES = """
- name: Print all backup information by VM ID and VM name
  community.general.proxmox_backup_info:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'

- name: Print Proxmox backup information for a specific VM based on its name
  community.general.proxmox_backup_info:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_name: 'mailsrv'

- name: Print Proxmox backup information for a specific VM based on its VM ID
  community.general.proxmox_backup_info:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_id: '150'

- name: Print Proxmox all backup job information
  community.general.proxmox_backup_info:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    backup_jobs: true
"""

RETURN = """
---
backup_info:
  description: The return value provides backup job information based on VM ID or VM name, or total backup job information.
  returned: on success, but can be empty
  type: list
  elements: dict
  contains:
    bktype:
      description: The type of the backup.
      returned: on success
      type: str
      sample: vzdump
    enabled:
      description: V(1) if backup is enabled else V(0).
      returned: on success
      type: int
      sample: 1
    id:
      description: The backup job ID.
      returned: on success
      type: str
      sample: backup-83831498-c631
    mode:
      description: The backup job mode such as snapshot.
      returned: on success
      type: str
      sample: snapshot
    next-run:
      description: The next backup time.
      returned: on success
      type: str
      sample: "2024-12-28 11:30:00"
    schedule:
      description: The backup job schedule.
      returned: on success
      type: str
      sample: "sat 15:00"
    storage:
      description: The backup storage location.
      returned: on success
      type: str
      sample: local
    vm_name:
      description: The VM name.
      returned: on success
      type: str
      sample: test01
    vmid:
      description: The VM ID.
      returned: on success
      type: str
      sample: "100"
"""

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR)


class ProxmoxBackupInfoAnsible(ProxmoxAnsible):

    # Get all backup information
    def get_jobs_list(self):
        try:
            backupJobs = self.proxmox_api.cluster.backup.get()
        except Exception as e:
            self.module.fail_json(msg="Getting backup jobs failed: %s" % e)
        return backupJobs

    # Get VM information
    def get_vms_list(self):
        try:
            vms = self.proxmox_api.cluster.resources.get(type='vm')
        except Exception as e:
            self.module.fail_json(msg="Getting VMs info from cluster failed: %s" % e)
        return vms

    # Get all backup information by VM ID and VM name
    def vms_backup_info(self):
        backupList = self.get_jobs_list()
        vmInfo = self.get_vms_list()
        bkInfo = []
        for backupItem in backupList:
            nextrun = datetime.fromtimestamp(backupItem['next-run'])
            vmids = backupItem['vmid'].split(',')
            for vmid in vmids:
                for vm in vmInfo:
                    if vm['vmid'] == int(vmid):
                        vmName = vm['name']
                        break
                bkInfoData = {'id': backupItem['id'],
                              'schedule': backupItem['schedule'],
                              'storage': backupItem['storage'],
                              'mode': backupItem['mode'],
                              'next-run': nextrun.strftime("%Y-%m-%d %H:%M:%S"),
                              'enabled': backupItem['enabled'],
                              'bktype': backupItem['type'],
                              'vmid': vmid,
                              'vm_name': vmName}
                bkInfo.append(bkInfoData)
        return bkInfo

    # Get proxmox backup information for a specific VM based on its VM ID or VM name
    def specific_vmbackup_info(self, vm_name_id):
        fullBackupInfo = self.vms_backup_info()
        vmBackupJobs = []
        for vm in fullBackupInfo:
            if (vm["vm_name"] == vm_name_id or vm["vmid"] == vm_name_id):
                vmBackupJobs.append(vm)
        return vmBackupJobs


def main():
    # Define module args
    args = proxmox_auth_argument_spec()
    backup_info_args = dict(
        vm_id=dict(type='str'),
        vm_name=dict(type='str'),
        backup_jobs=dict(type='bool', default=False)
    )
    args.update(backup_info_args)

    module = AnsibleModule(
        argument_spec=args,
        mutually_exclusive=[('backup_jobs', 'vm_id', 'vm_name')],
        supports_check_mode=True
    )

    # Define (init) result value
    result = dict(
        changed=False
    )

    # Check if proxmoxer exist
    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

    # Start to connect to proxmox to get backup data
    proxmox = ProxmoxBackupInfoAnsible(module)
    vm_id = module.params['vm_id']
    vm_name = module.params['vm_name']
    backup_jobs = module.params['backup_jobs']

    # Update result value based on what requested (module args)
    if backup_jobs:
        result['backup_info'] = proxmox.get_jobs_list()
    elif vm_id:
        result['backup_info'] = proxmox.specific_vmbackup_info(vm_id)
    elif vm_name:
        result['backup_info'] = proxmox.specific_vmbackup_info(vm_name)
    else:
        result['backup_info'] = proxmox.vms_backup_info()

    # Return result value
    module.exit_json(**result)


if __name__ == '__main__':
    main()
