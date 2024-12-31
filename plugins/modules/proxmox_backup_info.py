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

description:
  - Retrieve information such as backup times, VM name, VM ID, mode, backup type, and backup schedule using the Proxmox Server API.

author:
  - "Marzieh Raoufnezhad (@raoufnezhad) <raoufnezhad@gmail.com>"
  - "Maryam Mayabi (@mmayabi) <mayabi.ahm@gmail.com>"

options:
  vm_name:
    description: The name of the Proxmox VM.
    required: false
    type: str
  vm_id:
    description: The ID of the Proxmox VM.
    required: false
    type: int
  backup_jobs:
    description: 
      - The backup_jobs value is true or false. 
      - If set to true, this module just return all backup jobs information.
      - If set to false, what is listed depends on the other options.
    required: false
    default: false
    type: bool

extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.proxmox.actiongroup_proxmox
"""

EXAMPLES = """
- name: Print all backup information by VM id and VM name
  proxmox_backup_info:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'

- name: Print proxmox backup information for a specific VM based on its name
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      vm_name: 'mailsrv'

- name: Print proxmox backup information for a specific VM based on its VM id
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      vm_id: '150'

- name: Print proxmox all backup job information
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      backup_jobs: true
"""

RETURN = """
---
backup_info:
  description: The return value provides backup job information based on VM ID or VM name, or total backup job information.
  returned: always, but can be empty
  type: list
  elements: dict
  contains:
    bktype:
      description: The type of the backup.
      returned: on success
      type: str
    enabled:
      description: 1 if backup is enabled else 0.
      returned: on success
      type: int
    id:
      description: The backup job id.
      returned: on success
      type: str
    mode:
      description: The backup job mode such as snapshot.
      returned: on success
      type: str
    next-run:
      description: The next backup time.
      returned: on success
      type: str
    schedule:
      description: The backup job schedule.
      returned: on success
      type: str
    storage:
      description: The backup storage location.
      returned: on success
      type: str
    vm_name:
      description: The VM name.
      returned: on success
      type: str
    vmid:
      description: The VM vmid.
      returned: on success
      type: int
"""

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR)


class ProxmoxBackupInfoAnsible(ProxmoxAnsible):

    # Get all backup information
    def getJobsList(self):
        try:
            backupJobs = self.proxmox_api.cluster.backup.get()
        except Exception as e:
            self.module.fail_json(msg="Getting backup jobs failed: %s" % e)
        return backupJobs

    # Get VM information
    def getVmsList(self):
        try:
            vms = self.proxmox_api.cluster.resources.get(type='vm')
        except Exception as e:
            self.module.fail_json(msg="Getting VMs info from cluster failed: %s" % e)
        return vms

    # Get all backup information by VM id and VM name
    def vmsBackupInfo(self):
        backupList = self.getJobsList()
        vmInfo = self.getVmsList()
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

    # Get proxmox backup information for a specific VM based on its VM id or VM name
    def specificVmBackupInfo(self, vm_name_id):
        fullBackupInfo = self.vmsBackupInfo()
        vmBackupJobs = []
        for vm in fullBackupInfo:
            if (vm["vm_name"] == vm_name_id or int(vm["vmid"]) == vm_name_id):
                vmBackupJobs.append(vm)
        return vmBackupJobs


def main():
    # Define module args
    args = proxmox_auth_argument_spec()
    backup_info_args = dict(
        vm_id=dict(type='int', required=False),
        vm_name=dict(type='str', required=False),
        backup_jobs=dict(type='bool', default=False, required=False)
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
        result['backup_info'] = proxmox.getJobsList()
    elif vm_id:
        result['backup_info'] = proxmox.specificVmBackupInfo(vm_id)
    elif vm_name:
        result['backup_info'] = proxmox.specificVmBackupInfo(vm_name)
    else:
        result['backup_info'] = proxmox.vmsBackupInfo()

    # Return result value
    module.exit_json(**result)


if __name__ == '__main__':
    main()
