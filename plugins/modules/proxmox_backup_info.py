from proxmoxer import ProxmoxAPI
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible, proxmox_to_ansible_bool)

import urllib3

urllib3.disable_warnings()

DOCUMENTATION = '''
---
module: proxmox_backup_info
short_description: Retrieve information about one or more Proxmox VE backups
version_added: 2.2.0
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
    id: "{{ id | default(omit) }}"
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
      description: Notification event type
      returned: on success
      type: str
    storage:
      description: Storage used in backup job
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
      description: Backup mode
      returned: on success
      type: str
    next-run:
      description: Timestamp of next run
      returned: on success
      type: str
    repeat-missed:
      description: If true, the job will be run as soon as possible if it was missed while the scheduler was not running.
      returned: on success
      type: bool
    type:
      description: Type of backup
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
      description: Backup mode
      returned: on success
      type: str
    vmid:
      description: The ID of the guest system backuped.
      returned: on success
      type: str
'''


class ProxmoxBackupInfoAnsible(ProxmoxAnsible):
    def get_backup(self, id):
        if id:
            try:
                backup = self.proxmox_api.cluster.backup.get(id)
            except Exception:
                self.module.fail_json(msg="Backup with id '%s' does not exist" % id)
            return ProxmoxBackup(backup)
        else:
            backups = self.proxmox_api.cluster.backup.get()
            backups = [ProxmoxBackup(backup) for backup in backups]
            return backups


class ProxmoxBackup:
    def __init__(self, backups):
        self.backups = backups
        # Convert proxmox representation of lists, dicts and boolean for easier
        # manipulation within ansible.
        if 'mailnotification' in self.backups:
            self.backups['mailnotification'] = self.backups['mailnotification']
        if 'storage' in self.backups:
            self.backups['storage'] = self.backups['storage']
        if 'notes-template' in self.backups:
            self.backups['notes-template'] = self.backups['notes-template']
        if 'mailto' in self.backups:
            self.backups['mailto'] = self.backups['mailto']
        if 'id' in self.backups:
            self.backups['id'] = self.backups['id']
        if 'mode' in self.backups:
            self.backups['mode'] = self.backups['mode']
        if 'next-run' in self.backups:
            self.backups['next-run'] = self.backups['next-run']
        if 'repeat-missed' in self.backups:
            self.backups['repeat-missed'] = proxmox_to_ansible_bool(self.backups['repeat-missed'])
        if 'type' in self.backups:
            self.backups['type'] = self.backups['type']
        if 'enabled' in self.backups:
            self.backups['enabled'] = proxmox_to_ansible_bool(self.backups['enabled'])
        if 'all' in self.backups:
            self.backups['all'] = proxmox_to_ansible_bool(self.backups['all'])
        if 'pool' in self.backups:
            self.backups['pool'] = self.backups['pool']
        if 'vmid' in self.backups:
            self.backups['vmid'] = self.backups['vmid']


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
        mutually_exclusive=[('id')],
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
