# -*- coding: utf-8 -*-
#
# (c) 2024, zerchevack <leverrierd@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: proxmox_backup_info
short_description: Retrieve information about one or more Proxmox VE backups
version_added: 9.0.0
description:
  - Retrieve information about one or more Proxmox VE backups.
options:
  id:
    description:
      - Only return information on a specific backup.
    type: str
author: Leverrier Dylan (@tleguern)
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
  - community.general.attributes.info_module
notes:
  - Backup specific options can be returned by this module, please look at the documentation at U(https://pve.proxmox.com/wiki/Backup_and_Restore).
'''

EXAMPLES = '''
- name: List existing backups
  community.general.proxmox_backup_info:
    api_host: helldorado
    api_user: root@pam
    api_password: "{{ password | default(omit) }}"
    api_token_id: "{{ token_id | default(omit) }}"
    api_token_secret: "{{ token_secret | default(omit) }}"
    validate_certs: "{{ validate_certs | default(omit) }}"
  register: proxmox_backups
'''

RETURN = '''
proxmox_backups:
  description: List of backup job.
  returned: on success
  type: list
  elements: dict
  contains:
    mailnotification:
      description: Notification event type.
      returned: on success
      type: str
    storage:
      description: Storage used in backup job.
      returned: on success
      type: str
    notes-template:
      description: Template string for generating notes for the backup(s).
      returned: on success
      type: str
    mailto:
      description: Comma-separated list of email addresses or users that should receive email notifications.
      returned: on success
      type: str
    id:
      description: Job ID.
      returned: on success
      type: str
    mode:
      description: Backup mode.
      returned: on success
      type: str
    next-run:
      description: Timestamp of next run.
      returned: on success
      type: str
    repeat-missed:
      description: If true, the job will be run as soon as possible if it was missed while the scheduler was not running.
      returned: on success
      type: bool
    type:
      description: Type of backup.
      returned: on success
      type: str
    enabled:
      description: If true, this job is enable else it is disable the job.
      returned: on success
      type: bool
    all:
      description: If true, this job bacukup all known guest systems on this host.
      returned: on success
      type: bool
    pool:
      description: Backup mode.
      returned: on success
      type: str
    vmid:
      description: The ID of the guest system backuped.
      returned: on success
      type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, url_argument_spec
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, proxmox_to_ansible_bool)


class ProxmoxBackupInfoAnsible(ProxmoxAnsible):
    def __init__(self, module):
        self.module = module
        self.api_host = module.params['api_host']
        self.api_user = module.params['api_user']
        self.api_password = module.params.get('api_password')
        self.api_token_id = module.params.get('api_token_id')
        self.api_token_secret = module.params.get('api_token_secret')
        self.validate_certs = module.params['validate_certs']

    def fetch_backup_data(self, endpoint):
        if self.api_token_id and self.api_token_secret:
            headers = {
                'Authorization': f'PVEAPIToken={self.api_user}!{self.api_token_id}={self.api_token_secret}'
            }
            url = f'https://{self.api_host}:8006/api2/json/{endpoint}'
            response = fetch_url(self.module, url, headers=headers)

            if response['status'] != 200:
                self.module.fail_json(msg=f"Failed to fetch data from Proxmox API: {response}")
            return response.read()
        else:
            return "Error : please define api_token_id and api_token_secret"

    def get_backup(self, id):
        if id:
            try:
                backup = self.fetch_backup_data(f'cluster/backup/{id}')
            except Exception:
                self.module.fail_json(msg="Backup with id '%s' does not exist" % id)
            return ProxmoxBackup(backup)
        else:
            backups = self.fetch_backup_data('cluster/backup')
            backups = [ProxmoxBackup(backup) for backup in backups]
            return backups


class ProxmoxBackup(object):
    def __init__(self, backup):
        self.backup = backup
        # Convert proxmox representation of lists, dicts and boolean for easier
        # manipulation within ansible.
        if 'mailnotification' in self.backup:
            self.backup['mailnotification'] = self.backup['mailnotification']
        if 'storage' in self.backup:
            self.backup['storage'] = self.backup['storage']
        if 'notes-template' in backup:
            self.backup['notes-template'] = self.backup['notes-template']
        if 'mailto' in self.backup:
            self.backup['mailto'] = self.backup['mailto']
        if 'id' in self.backup:
            self.backup['id'] = self.backup['id']
        if 'mode' in self.backup:
            self.backup['mode'] = self.backup['mode']
        if 'next-run' in self.backup:
            self.backup['next-run'] = self.backup['next-run']
        if 'repeat-missed' in self.backup:
            self.backup['repeat-missed'] = proxmox_to_ansible_bool(self.backup['repeat-missed'])
        if 'type' in self.backup:
            self.backup['type'] = self.backup['type']
        if 'enabled' in self.backup:
            self.backup['enabled'] = proxmox_to_ansible_bool(self.backup['enabled'])
        if 'all' in self.backup:
            self.backup['all'] = proxmox_to_ansible_bool(self.backup['all'])
        if 'pool' in self.backup:
            self.backup['pool'] = self.backup['pool']
        if 'vmid' in self.backup:
            self.backup['vmid'] = self.backup['vmid']


def proxmox_backup_info_argument_spec():
    return dict(
        id=dict(type='str', aliases=['id']),
    )


def main():
    module_args = proxmox_auth_argument_spec()
    backup_info_args = proxmox_backup_info_argument_spec()
    module_args.update(backup_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        supports_check_mode=True
    )
    result = dict(
        changed=False
    )

    proxmox = ProxmoxBackupInfoAnsible(module)
    backup = module.params['id']

    if backup:
        backups = [proxmox.get_backup(backup)]
    else:
        backups = proxmox.get_backup(id=None)
    result['proxmox_backups'] = [backups.backups for backups in backups]

    module.exit_json(**result)


if __name__ == '__main__':

    main()
