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

short_description: Proxmox Schedule Backup Info  

description: Retrieve information such as backup times, VM name, VM ID, mode, backup type, and backup schedule using the Proxmox Server API.

author: 
    - Marzieh Raoufnezhad
    - Maryam Mayabi

options:
      api_user:
        description: The user must have access to the proxmox server 
        required: true
      api_password:
        description: The password for the proxmox user 
        required: true
      api_host:
        description: Poroxmox server domain name or ip address
        required: true
      vm_name:
        description: Proxmox vm name
        required: false
      vm_id:
        description: Proxmox vm id
        required: false
      backup_section:
        description: proxmox_backup_section
        required: false
        defulat: false
"""

EXAMPLES = """
---
- name: Print all backup information by vmid and vm name
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'

---
- name: Print proxmox backup information for a specific vm based on its name
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      vm_name: 'mailsrv'

---
- name: Print proxmox backup information for a specific vm based on its vmid
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      vm_id: '150'

---
- name: Print proxmox all backup job information 
  proxmox_backup_info:
      api_user: 'myUser@pam'
      api_password: '*******'
      api_host: '192.168.20.20'
      backup_section: 'true'
"""

RETURN = """
---
result:
    description: The return value provided by proxmox_backup_info.
    type: dict
"""

from datetime import datetime
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, HAS_PROXMOXER, PROXMOXER_IMP_ERR, proxmox_to_ansible_bool)

class ProxmoxBackupInfoAnsible(ProxmoxAnsible):

    # Get all backup information
    def getSectionsList(self):
        try:
            backupSections=self.proxmox_api.cluster.backup.get()
        except Exception as e:
            module.fail_json(msg="Getting backup sections failed: %s" % e)
        return backupSections
    
    # Get vm information
    def getVmsList(self):
        try:
            vms=self.proxmox_api.cluster.resources.get(type='vm')
        except Exception as e:
            module.fail_json(msg="Getting vms info from cluster failed: %s" % e)
        return vms

    # Get all backup information by vmid and vm name
    def vmsBackupInfo(self):
        backupList=self.getSectionsList()
        vmInfo=self.getVmsList()
        bkInfo=[]
        for backupItem in backupList:
            nextrun = datetime.fromtimestamp(backupItem['next-run'])
            vmids=backupItem['vmid'].split(',')
            for vmid in vmids:
                for vm in vmInfo:
                    if vm['vmid'] == int(vmid):
                        vmName = vm['name']
                        break
                bkInfoData = { 'id': backupItem['id'], 
                               'schedule': backupItem['schedule'], 
                               'storage': backupItem['storage'], 
                               'mode': backupItem['mode'], 
                               'next-run': nextrun.strftime("%Y-%m-%d %H:%M:%S"), 
                               'enabled': backupItem['enabled'], 
                               'bktype': backupItem['type'], 
                               'vmid': vmid,
                               'vm_name': vmName }
                bkInfo.append(bkInfoData)
        return bkInfo
    
    # Get proxmox backup information for a specific vm based on its vmid or vm name
    def specificVmBackupInfo(self,vm_name_id):
        fullBackupInfo = self.vmsBackupInfo()
        vmBackupSections = []
        for vm in fullBackupInfo:
            if (vm["vm_name"] == vm_name_id or int(vm["vmid"]) == vm_name_id):
                vmBackupSections.append(vm)
        return vmBackupSections
    
def main():
    # Define module args
    args = proxmox_auth_argument_spec()
    backup_info_args = dict(
                            vm_id=dict(type='int',required=False),
                            vm_name=dict(type='str',required=False),
                            backup_section=dict(type='bool',default=False,required=False)
                           )
    args.update(backup_info_args)

    module = AnsibleModule(
        argument_spec=args,
        mutually_exclusive=[('backup_section', 'vm_id', 'vm_name')],
        supports_check_mode=True)
    
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
    backup_section = module.params['backup_section']

    # Update result value based on what requested (module args)
    if backup_section:
        result['backup_info'] = proxmox.getSectionsList()
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
