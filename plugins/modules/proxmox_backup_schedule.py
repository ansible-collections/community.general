#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Marzieh Raoufnezhad <raoufnezhad@gmail.com>
# Copyright (c) 2024 Maryam Mayabi <mayabi.ahm at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
module: proxmox_backup_schedule

short_description: Scheduling VM backups and removing it.

version_added: 10.3.0

description: The module modifies backup jobs such as set or delete C(vmid).

author:
  - "Marzieh Raoufnezhad (@raoufnezhad) <raoufnezhad@gmail.com>"
  - "Maryam Mayabi (@mmayabi) <mayabi.ahm@gmail.com>"

options:
  vm_name:
    description:
      - The name of the Proxmox VM.
      - Mutually exclusive with O(vm_id).
    type: str
  vm_id:
    description:
      - The ID of the Proxmox VM.
      - Mutually exclusive with O(vm_name).
    type: str
  backup_id:
    description: The backup job ID.
    type: str
  backup_action:
    description:
        - If V(update_vmid), the module will update backup job with new VM ID.
        - If V(delete_vmid), the module will remove the VM ID from all backup jobs where the VM ID has existed.
    required: true
    choices: ["update_vmid", "delete_vmid"]
    type: str

extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
  - community.general.proxmox.actiongroup_proxmox
"""

EXAMPLES = """
- name: Scheduling VM Backups based on VM name.
  proxmox_backup_schedule:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_name: 'VM Name'
    backup_id: 'backup-b2adffdc-316e'
    backup_action: 'update_vmid'

- name: Scheduling VM Backups based on VM ID.
  proxmox_backup_schedule:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_id: 'VM ID'
    backup_id: 'backup-b2adffdc-316e'
    backup_action: 'update_vmid'

- name: Removing backup setting based on VM name.
  proxmox_backup_schedule:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_name: 'VM Name'
    backup_action: 'delete_vmid'

- name: Removing backup setting based on VM ID.
  proxmox_backup_schedule:
    api_user: 'myUser@pam'
    api_password: '*******'
    api_host: '192.168.20.20'
    vm_id: 'VM ID'
    backup_action: 'delete_vmid'
"""

RETURN = """
---
backup_schedule:
  description:
    - When backup_action is 'update_vmid', the backup_schedule will return True after successfully adding the VM ID to the backup job.
    - When backup_action is 'delete_vmid', the backup_schedule will return a list of backup job IDs where the VM ID has been removed.
  returned: always, but can be empty
  type: bool | list
  sample:
    - True
    - ['backup-job-id1', 'backup-job-id2']
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR)


class ProxmoxSetVMBackupAnsible(ProxmoxAnsible):
    # Getting backup sections
    def get_cluster_bklist(self):
        try:
            backupSections = self.proxmox_api.cluster.backup.get()
        except Exception as e:
            self.module.fail_json(msg="Getting backup sections failed: %s" % e)
        return backupSections

    def get_cluster_specific_bkjobid(self, backup_id):
        try:
            specificBackupID = self.proxmox_api.cluster.backup.get(backup_id)
        except Exception as e:
            self.module.fail_json(msg="Getting specific backup ID failed: %s" % e)
        return specificBackupID

    def set_vmid_backup(self, backup_id, bk_id_vmids):
        try:
            self.proxmox_api.cluster.backup.put(backup_id, vmid=bk_id_vmids)
        except Exception as e:
            self.module.fail_json(msg="Setting vmid backup failed: %s" % e)
        return

    def get_vms_list(self):
        try:
            vms = self.proxmox_api.cluster.resources.get(type='vm')
        except Exception as e:
            self.module.fail_json(msg="Getting vms info from cluster failed: %s" % e)
        return vms

    # convert vm name to vm ID
    def vmname_2_vmid(self, vmname):
        vmInfo = self.get_vms_list()
        vms = [vm for vm in vmInfo if vm['name'] == vmname]
        return (vms[0]['vmid'])

    # add vmid to backup job
    def backup_update_vmid(self, vm_id, backup_id):
        bk_id_info = self.get_cluster_specific_bkjobid(backup_id)

        # If bk_id_info is a list, get the first item (assuming there's only one backup job returned)
        if isinstance(bk_id_info, list):
            bk_id_info = bk_id_info[0]  # Access the first item in the list
        vms_id = bk_id_info['vmid'].split(',')
        if vm_id not in vms_id:
            bk_id_vmids = bk_id_info['vmid'] + ',' + str(vm_id)
            self.set_vmid_backup(backup_id, bk_id_vmids)
            return True

    # delete vmid from backup job
    def backup_delete_vmid(self, vm_id):
        bkID_delvm = []
        backupList = self.get_cluster_bklist()
        for backupItem in backupList:
            vmids = list(backupItem['vmid'].split(','))
            if vm_id in vmids:
                if len(vmids) > 1:
                    vmids.remove(vm_id)
                    new_vmids = ','.join(map(str, vmids))
                    self.set_vmid_backup(backupItem['id'], new_vmids)
                    bkID_delvm.append(backupItem['id'])
                else:
                    self.module.fail_json(msg="No more than one vmid is assigned to %s. You just can remove job." % backupItem['id'])
        return bkID_delvm


# main function
def main():
    # Define module args
    args = proxmox_auth_argument_spec()
    backup_schedule_args = dict(
        vm_name=dict(type='str'),
        vm_id=dict(type='str'),
        backup_id=dict(type='str'),
        backup_action=dict(choices=['update_vmid', 'delete_vmid'], required=True)
    )
    args.update(backup_schedule_args)

    module = AnsibleModule(
        argument_spec=args,
        mutually_exclusive=[('vm_id', 'vm_name')],
        supports_check_mode=True
    )

    # Define (init) result value
    result = dict(
        changed=False,
        message=''
    )

    # Check if proxmoxer exist
    if not HAS_PROXMOXER:
        module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

    # Start to connect to proxmox to get backup data
    proxmox = ProxmoxSetVMBackupAnsible(module)
    vm_name = module.params['vm_name']
    vm_id = module.params['vm_id']
    backup_id = module.params['backup_id']
    backup_action = module.params['backup_action']

    if vm_name:
        vm_id = proxmox.vmname_2_vmid(vm_name)

    if backup_action == 'update_vmid':
        result['backup_schedule'] = proxmox.backup_update_vmid(vm_id, backup_id)

    if backup_action == 'delete_vmid':
        result['backup_schedule'] = proxmox.backup_delete_vmid(vm_id)

    if result['backup_schedule']:
        result['changed'] = True
        result['message'] = 'The backup schedule has been changed successfully'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
