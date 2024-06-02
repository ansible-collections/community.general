#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright John Berninger (@jberning) <john.berninger at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: proxmox_backup
short_description: Create, delete, or update Proxmox VE backup jobs
version_added: 9.1.0
description:
  - Allows you to perform some supported operations on a backup job in a Proxmox VE cluster.
author: Dylan Leverrier (@zerchevack)
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  state:
    description:
      - Set to V(present) to create or update job.
      - Set to V(absent) to delete job.
    choices: ['present', 'absent']
    type: str
    required: true
  all:
    description:
      - Backup all known guest systems on this host.
      - Can not be use with O(vmid) and O(pool) in same job.
    type: bool
  bwlimit:
    description:
      - Limit I/O bandwidth (in KiB/s).
    type: int
  comment:
    description:
      - Description for the job.
    type: str
  compress:
    description:
      - >
        If you choose a remote storage (like Proxmox Backup Server storage), V(zstd) will be set automatically and this the only available value.
        If you choose a local storage you can choose between V(gzip), V(lzo) and V(zstd).
    choices: ['gzip', 'lzo', 'zstd']
    type: str
  dow:
    description:
      - Day of week selection.
    type: str
  dumpdir:
    description:
      - Store resulting files to specified directory.
    type: str
  enabled:
    description:
      - Enable or disable the job.
    type: bool
  exclude:
    description:
      - Exclude specified guest systems (assumes V(--all)).
    type: str
  exclude_path:
    description:
      - >
        Exclude certain files/directories (shell globs).
        Paths starting with '/' are anchored to the container's root,
        other paths match relative to each subdirectory.
    choices: ['ignore', 'on']
    type: str
  fleecing:
    description:
      - Options for backup fleecing (VM only).
    type: str
  id:
    description:
      - Required if O(state=absent).
      - If O(state=present), it allow you to set a pattern of ID (example V(backup-12345678-9123)). If it is not set an ID will be generate automatically.
      - Required if O(state=present) and you want to update a existing job.
    type: str
  ionice:
    description:
      - Set IO priority when using the BFQ scheduler.
      - For snapshot and suspend mode backups of VMs, this only affects the compressor.
      - A value of 8 means the idle priority is used,
        otherwise the best-effort priority is used with the specified value.
    type: int
  lockwait:
    description:
      - Maximal time to wait for the global lock (minutes).
    type: int
  mailnotification:
    description:
      - Specify when to send a notification mail.
    choices: ['always', 'failure']
    type: str
  mailto:
    description:
      - List of email addresses or users that should receive email notifications.
    type: list
    elements: str
  maxfiles:
    description:
      - Maximal number of backup files per guest system.
    type: int
  mode:
    description:
      - Backup mode.
    choices: ['snapshot', 'suspend', 'stop']
    type: str
  node:
    description:
      - Only run if executed on this node.
    type: str
  notes_template:
    description:
      - Template string for generating notes for the backup(s).
      - It can contain variables which will be replaced by their values.
      - Currently supported are V({{cluster}}), V{({guestname}}), V({{node}}), and V({{vmid}}), but more might be added in the future.
      - Needs to be a single line, newline and backslash need to be escaped.
    type: str
  performance:
    description:
      - Other performance-related settings.
    type: str
  pigz:
    description:
      - Use pigz instead of gzip when V(N>0).
      - V(N=1) uses half of cores, V(N>1) uses N as thread count.
    type: int
  pool:
    description:
      - Backup all known guest systems included in the specified pool.
      - Can not be use with O(vmid) and O(pool) in same job.
    type: str
  protected:
    description:
      - If V(true), mark backup(s) as protected.
    type: bool
  prune_backups:
    description:
      - Use these retention options instead of those from the storage configuration.
    type: str
  quiet:
    description:
      - Be quiet.
    type: bool
  remove:
    description:
      - Prune older backups according to O(prune_backups).
    type: bool
  repeat_missed:
    description:
      - If V(true), the job will be run as soon as possible if it was missed while the scheduler was not running.
    type: bool
  schedule:
    description:
      - Backup schedule. The format is a subset of `systemd` calendar events.
    type: str
  script:
    description:
      - Use specified hook script.
    type: str
  starttime:
    description:
      - Job Start time.
    type: str
  stdexcludes:
    description:
      - Exclude temporary files and logs.
    type: bool
  stop:
    description:
      - Stop running backup jobs on this host.
    type: bool
  stopwait:
    description:
      - Maximal time to wait until a guest system is stopped (minutes).
    type: int
  storage:
    description:
      - Store resulting file to this storage.
    type: str
  tmpdir:
    description:
      - Store temporary files to specified directory.
    type: str
  vmid:
    description:
      - The ID of the guest system you want to backup.
      - Can not be use with vmid and pool in same job
    type: str
  zstd:
    description:
      - Zstd threads. V(N=0) uses half of the available cores,
        if V(N) is set to a value bigger than V(0), V(N) is used as thread count.
    type: int

extends_documentation_fragment:
  - community.general.proxmox.actiongroup_proxmox
  - community.general.proxmox.documentation
  - community.general.attributes
'''

EXAMPLES = '''
- name: List all backup jobs
  community.general.proxmox_backup:
    api_host: "node1"
    api_user: user@realm
    api_password: password
    validate_certs: false
    state: list
  register: backup_result

- name: Show current backup job
  ansible.builtin.debug:
    var: backup_result

- name: Create backup with id backup-20bad73a-d245
  community.general.proxmox_backup:
    api_host: "node1"
    api_token_id: "token_id"
    api_token_secret: "token_secret"
    validate_certs: false
    id: "backup-20bad73a-d245"
    vmid: "103"
    mode: "snapshot"
    mailnotification: "always"
    mailto: "my mail address"
    repeat_missed: 0
    enabled: 1
    prune_backups:
        keep_yearly: "6"
        keep_weekly: "5"
        keep_hourly: "4"
        keep_daily: "2"
        keep_last: "1"
        keep_monthly: "3"
    storage: "backup-idcheck-preprod-0"
    schedule: "*-*-* 22:00:00"
    state: present

- name: Delete backup job
  community.general.proxmox_backup:
    api_host: "node1"
    api_token_id: "token_id"
    api_token_secret: "token_secret"
    validate_certs: false
    id: "backup-20bad73a-d245"
    state: absent

- name: Update backup with id backup-20bad73a-d245 (Change VM ID backuped)
  community.general.proxmox_backup:
    api_host: "node1"
    api_token_id: "token_id"
    api_token_secret: "token_secret"
    validate_certs: false
    id: "backup-20bad73a-d245"
    vmid: "111"
    state: present
'''

RETURN = '''
proxmox_backup:
    description: List of Proxmox VE backups.
    returned: on success
    type: list
    elements: dict
    contains:
      all:
        description: Backup all known guest systems on this host.
        returned: on success
        type: bool
      bwlimit:
        description: Limit I/O bandwidth (in KiB/s).
        returned: on success
        type: int
      comment:
        description: Description for the Job.
        returned: on success
        type: str
      compress:
        description: Compress dump file.
        returned: on success
        type: str
      dow:
        description: Day of week selection.
        returned: on success
        type: str
      dumpdir:
        description: Store resulting files to specified directory.
        returned: on success
        type: str
      enabled:
        description: Enable or disable the job.
        returned: on success
        type: bool
      exclude:
        description: Exclude specified guest systems (assumes --all)
        returned: on success
        type: str
      exclude_path:
        description:
          - >
            Exclude certain files/directories (shell globs).
            Paths starting with '/' are anchored to the container's root, other paths match relative to each subdirectory.
        returned: on success
        type: list
      fleecing:
        description: Options for backup fleecing (VM only).
        returned: on success
        type: str
      id:
        description: Job ID (will be autogenerated).
        returned: on success
        type: str
      ionice:
        description:
          - >
            Set IO priority when using the BFQ scheduler.
            For snapshot and suspend mode backups of VMs, this only affects the compressor.
          - >
            A value of 8 means the idle priority is used, otherwise the best-effort priority is used with the specified value.
        returned: on success
        type: int
      lockwait:
        description: Maximal time to wait for the global lock (minutes).
        returned: on success
        type: int
      mailnotification:
        description: Specify when to send a notification mail
        returned: on success
        type: str
      mailto:
        description:
          - >
            List of email addresses or users that should receive email notifications.
        returned: on success
        type: list
        elements: str
      maxfiles:
        description: Maximal number of backup files per guest system.
        returned: on success
        type: int
      mode:
        description: Backup mode.
        returned: on success
        type: str
      node:
        description: Only run if executed on this node.
        returned: on success
        type: str
      notes_template:
        description:
          - Template string for generating notes for the backup(s).
          - It can contain variables which will be replaced by their values.
          - Currently supported are V({{cluster}}), V({{guestname}}), V({{node}}) and V({{vmid}}), but more might be added in the future.
          - Needs to be a single line, newline and backslash need to be escaped.
        returned: on success
        type: str
      performance:
        description:
          - >
            Other performance-related settings.
            (Possible values [max-workers=<integer>] [,pbs-entries-max=<integer>])
        returned: on success
        type: str
      pigz:
        description:
          - >
            Use pigz instead of gzip when V(N>0). V(N=1) uses half of cores,
            V(N>1) uses V(N) as thread count.
        returned: on success
        type: int
      pool:
        description:
          - Backup all known guest systems included in the specified pool.
        returned: on success
        type: str
      protected:
        description: If true, mark backup(s) as protected.
        returned: on success
        type: bool
      prune_backups:
        description:
          - >
            Use these retention options instead of those from the storage configuration.
            (Format [keep-all=<1|0>] [,keep-daily=<N>] [,keep-hourly=<N>] [,keep-last=<N>] [,keep-monthly=<N>] [,keep-weekly=<N>] [,keep-yearly=<N>])
        returned: on success
        type: str
      quiet:
        description: Be quiet.
        returned: on success
        type: bool
      remove:
        description: Prune older backups according to 'prune-backups'.
        returned: on success
        type: bool
      repeat_missed:
        description:
          - >
            If true, the job will be run as soon as possible
            if it was missed while the scheduler was not running.
        returned: on success
        type: bool
      schedule:
        description:
          - >
            Backup schedule.
            The format is a subset of `systemd` calendar events.
        returned: on success
        type: str
      script:
        description: Use specified hook script.
        returned: on success
        type: str
      starttime:
        description: Job Start time.
        returned: on success
        type: str
      stdexcludes:
        description: Exclude temporary files and logs.
        returned: on success
        type: str
      stop:
        description: Stop running backup jobs on this host.
        returned: on success
        type: bool
      stopwait:
        description:
          - Maximal time to wait until a guest system is stopped (minutes).
        returned: on success
        type: int
      storage:
        description: Store resulting file to this storage.
        returned: on success
        type: str
      tmpdir:
        description: Store temporary files to specified directory.
        returned: on success
        type: str
      vmid:
        description: The ID of the guest system you want to backup.
        returned: on success
        type: str
      zstd:
        description:
          - >
            Zstd threads. N=0 uses half of the available cores,
            if N is set to a value bigger than 0, N is used as thread count.
        returned: on success
        type: int
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (
    proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxBackupAnsible(ProxmoxAnsible):
    def __init__(self, module):
        super().__init__(module)
        self.result = dict()

    def existing_job(self, id):
        jobs = self.proxmox_api.cluster.backup.get()
        for job in jobs:
            if job['id'] == id:
                return True

    def get_backups(self, id):
        output = dict()
        if id:
            if self.existing_job(id):
                backups = self.proxmox_api.cluster.backup.get()
                for backup in backups:
                    if backup['id'] == id:
                        output = {backup['id']: backup}
                        return output
            else:
                backups = self.proxmox_api.cluster.backup.get()
                output = {backup['id']: backup for backup in backups}
                return output
        else:
            backups = self.proxmox_api.cluster.backup.get()
            if backups:
                output = {backup['id']: backup for backup in backups}
                return output
            else:
                return output

    def delete_backup(self, id):
        result = dict()
        if self.module.check_mode:
            result['changed'] = True
            if self.module._diff:
                result['diff'] = {'before': self.get_backups(id=id),
                                  'after': {}}
            self.module.exit_json(**result)
        else:
            current_config = self.get_backups(id=None)
            self.proxmox_api.cluster.backup.delete(id)
            new_config = self.get_backups(id=None)
            diff = {}
            for key in current_config:
                if key not in new_config:
                    diff[key] = current_config[key]
            if diff:
                result['changed'] = True
                if self.module._diff:
                    result['diff'] = {'before': current_config,
                                      'after': new_config}
                self.module.exit_json(**result)
            else:
                result['changed'] = False

    def create_job(self, id):
        payload = self.get_task_parameters()
        payload_dict = {id: payload}
        if id:
            current_config = self.get_backups(id=id)
        else:
            current_config = self.get_backups(id=None)

        if id:
            if self.existing_job(id):
                if self.module.check_mode:
                    self.result['changed'] = True
                    if self.module._diff:
                        self.result['diff'] = {'before': {},
                                               'after': payload_dict}
                    self.module.exit_json(**self.result)
                else:
                    diff = {}
                    self.proxmox_api.cluster.backup(id).put(**payload)
                    new_config = self.get_backups(id=id)
                    for key in new_config:
                        if key in current_config:
                            if any(new_config[key][prop] != current_config[key][prop] for prop in new_config[key]):
                                diff[key] = new_config[key]
                    if diff:
                        self.result['changed'] = True
                        if self.module._diff:
                            self.result['diff'] = {'before': current_config,
                                                   'after': diff}
                        self.module.exit_json(**self.result)
                    else:
                        self.result['changed'] = False
                        self.module.exit_json(**self.result)
        else:
            if self.module.check_mode:
                self.result['changed'] = True
                if self.module._diff:
                    self.result['diff'] = {'before': {}, 'after': payload_dict}
                self.module.exit_json(**self.result)
            else:
                self.proxmox_api.cluster.backup.post(**payload)
                new_config = self.get_backups(id=id)
                for key in new_config:
                    if key in current_config:
                        if any(new_config[key][prop] != current_config[key][prop] for prop in new_config[key]):
                            diff[key] = new_config[key]
                if diff:
                    new_config = self.get_backups(id)
                    diff = {key: value for key, value in new_config.items() if
                            key not in current_config}
                    self.result['changed'] = True
                    if self.module._diff:
                        self.result['diff'] = {'before': {}, 'after': diff}
                    self.module.exit_json(**self.result)
                else:
                    self.result['changed'] = False
                    self.module.exit_json(**self.result)

    def get_task_parameters(self):
        # Filtre pour exclure les paramètres d'authentification
        exclude_keys = ['api_host', 'api_user', 'api_password', 'api_token_id',
                     'api_token_secret', 'validate_certs', 'state', 'mailto']
        task_params = {
            k.replace('_', '-'): (1 if v is True else (0 if v is False else v))
            for k, v in self.module.params.items()
            if k not in exclude_keys and v is not None
        }

        if 'mailto' in self.module.params and self.module.params['mailto'] is not None:
            task_params['mailto'] = ','.join(self.module.params['mailto'])
        return task_params


def proxmox_backup_argument_spec():
    return {
        'validate_certs': {
            'type': 'bool',
            'default': False,
            'required': False
        },
        'state': {
            'type': 'str',
            'choices': ['present', 'absent'],
            'required': True
        },
        'all': {
            'type': 'bool'
        },
        'bwlimit': {
            'type': 'int'
        },
        'comment': {
            'type': 'str'
        },
        'compress': {
            'type': 'str',
            'choices': ['gzip', 'lzo', 'zstd']
        },
        'dow': {
            'type': 'str'
        },
        'dumpdir': {
            'type': 'str'
        },
        'enabled': {
            'type': 'bool'
        },
        'exclude': {
            'type': 'str'
        },
        'exclude_path': {
            'type': 'str',
            'choices': ['ignore', 'on']
        },
        'fleecing': {
            'type': 'str'
        },
        'id': {
            'type': 'str'
        },
        'ionice': {
            'type': 'int'
        },
        'lockwait': {
            'type': 'int'
        },
        'mailnotification': {
            'type': 'str',
            'choices': ['always', 'failure']
        },
        'mailto': {
            'type': 'list',
            'elements': 'str'
        },
        'maxfiles': {
            'type': 'int'
        },
        'mode': {
            'type': 'str',
            'choices': ['snapshot', 'suspend', 'stop']
        },
        'node': {
            'type': 'str'
        },
        'notes_template': {
            'type': 'str'
        },
        'performance': {
            'type': 'str'
        },
        'pigz': {
            'type': 'int'
        },
        'pool': {
            'type': 'str'
        },
        'protected': {
            'type': 'bool'
        },
        'prune_backups': {
            'type': 'str'
        },
        'quiet': {
            'type': 'bool'
        },
        'remove': {
            'type': 'bool'
        },
        'repeat_missed': {
            'type': 'bool'
        },
        'schedule': {
            'type': 'str'
        },
        'script': {
            'type': 'str'
        },
        'starttime': {
            'type': 'str'
        },
        'stdexcludes': {
            'type': 'bool'
        },
        'stop': {
            'type': 'bool'
        },
        'stopwait': {
            'type': 'int'
        },
        'storage': {
            'type': 'str'
        },
        'tmpdir': {
            'type': 'str'
        },
        'vmid': {
            'type': 'str'
        },
        'zstd': {
            'type': 'int'
        }
    }


def main():
    result = dict()
    module_args = proxmox_auth_argument_spec()
    backups_info_args = proxmox_backup_argument_spec()
    module_args.update(backups_info_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_one_of=[('api_password', 'api_token_id')],
        required_together=[('api_token_id', 'api_token_secret')],
        mutually_exclusive=[('all', 'vmid', 'pool')],
        supports_check_mode=True,
    )

    proxmox = ProxmoxBackupAnsible(module)

    try:
        if module.params['state'] == 'absent':
            proxmox.delete_backup(module.params['id'])
        elif module.params['state'] == 'present':
            if module.params['id']:
                proxmox.create_job(id=module.params['id'])
            else:
                proxmox.create_job(id=None)
        module.exit_json(**result)
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
