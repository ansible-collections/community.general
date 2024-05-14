#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright John Berninger (@jberning) <john.berninger at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_backup
short_description: Get, delete, create or update Proxmox VE backup jobs.
version_added: 8.2.0
description:
  - Allows you to perform some supported operations on a backup job in a Proxmox VE cluster.
author: Dylan Leverrier (@zerchevack)
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  action_group:
    version_added: 9.0.0
options:
  state:
    description:
     - Indicate desired state of the job.
     - Set to list to get one or all jobs.
     - Set to present to create or update job.
     - Set to absent to delete job.
    choices: ['list', 'present', 'absent']
    type: str
  all:
    description:
      - Backup all known guest systems on this host.
      - Can not be use with vmid and pool in same job
    type: bool
    default: 0
  bwlimit:
    description:
      - Limit I/O bandwidth (in KiB/s).
    format: <integer> (0 - N)
    type: int
    default: 0
  comment:
    description:
      - Description for the Job.
    choices: ['0', '1', 'gzip', 'lzo', 'zstd']
    type: str
  compress:
    description:
      - Compress dump file.
    type: str
    default: 0
  dow:
    description:
      - Day of week selection.
    type: str
    default: mon,tue,wed,thu,fri,sat,sun
  dumpdir:
    description:
      - Store resulting files to specified directory.
    type: str
  enabled:
    description:
      - Enable or disable the job.
    type: bool
    default: 1
  exclude:
    description:
      - Exclude specified guest systems (assumes --all)
    type: str
  exclude_path:
    description:
      - Exclude certain files/directories (shell globs).
      - Paths starting with '/' are anchored to the container's root,
      - other paths match relative to each subdirectory.
    format: [<string>, ...]
    type: list
  fleecing:
    description:
      - Options for backup fleecing (VM only).
    format: [[enabled=]<1|0>] [,storage=<storage ID>]
    type: str
  id:
    description:
      - If state if list and you want to get properties of one job it needed,
      - if it not set all jobs will be return.
      - It needed if you state is delete.
      - If state is present, it allow you to set a pattern of id,
      - (Example backup-12345678-9123) if it not set an ID will be generate automaticly.
      - If state is present and you want to update a existing job, it needed.
    type: str
  ionice:
    description:
      - Set IO priority when using the BFQ scheduler.
      - For snapshot and suspend mode backups of VMs, this only affects the compressor.
      - A value of 8 means the idle priority is used,
      - otherwise the best-effort priority is used with the specified value.
    format: <integer> (0 - 8)
    type: int
    default: 7
  lockwait:
    description:
      - Maximal time to wait for the global lock (minutes).
    format: <integer> (0 - N)
    type: int
    default: 180
  mailnotification:
    description:
      - Specify when to send a notification mail
    choices: ['always', 'failure']
    type: str
    default: always
  mailto:
    description:
      - Comma-separated list of email addresses or users that should receive email notifications.
    type: str
  maxfiles:
    description:
      - Maximal number of backup files per guest system.
    format: <integer> (1 - N)
    type: int
  mode:
    description:
      - Backup mode.
    choices: ['snapshot', 'suspend', 'stop']
    type: str
    default: snapshot
  node:
    description:
      - Only run if executed on this node.
    type: str
  notes_template:
    description:
      - Template string for generating notes for the backup(s).
      - It can contain variables which will be replaced by their values.
      - Currently supported are {{cluster}}, {{guestname}}, {{node}}, and {{vmid}},but more might be added in the future.
      - Needs to be a single line, newline and backslash need to be escaped as '\n' and '\\' respectively.
    type: str
  performance:
    description:
      - Other performance-related settings.
    format: (Possible values [max-workers=<integer>] [,pbs-entries-max=<integer>])
    type: str
  pigz:
    description:
      - Use pigz instead of gzip when N>0.
      - N=1 uses half of cores, N>1 uses N as thread count.
    type: int
    default: 0
  pool:
    description:
      - Backup all known guest systems included in the specified pool.
      - Can not be use with vmid and pool in same job
    type: str
  protected:
    description:
      - If true, mark backup(s) as protected.
    type: bool
  prune_backups:
    description:
      - Use these retention options instead of those from the storage configuration.
    Format: [keep-all=<1|0>] [,keep-daily=<N>] [,keep-hourly=<N>] [,keep-last=<N>] [,keep-monthly=<N>] [,keep-weekly=<N>] [,keep-yearly=<N>])
    type: str
    default: keep-all=1
  quiet:
    description:
     - Be quiet.
    type: bool
    default: 0
  remove:
    description:
     - Prune older backups according to 'prune-backups'.
    type: bool
    default: 1
  repeat_missed:
    description:
     - If true, the job will be run as soon as possible if it was missed while the scheduler was not running.
    type: bool
    default: 0
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
    format: HH:MM
    type: str
  stdexcludes:
    description:
     - Exclude temporary files and logs.
    type: bool
    default: 0
  stop:
    description:
     - Stop running backup jobs on this host.
    type: bool
    default: 0
  stopwait:
    description:
     - Maximal time to wait until a guest system is stopped (minutes).
    format: <integer> (0 - N)
    type: int
    default: 10
  storage:
    description:
     - Store resulting file to this storage.
    format: <storage ID>
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
      - Zstd threads. N=0 uses half of the available cores,
      - if N is set to a value bigger than 0, N is used as thread count.
    type: int
    default: 1

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
  mailto: "preprod@idnow.io"
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
    description: List of Proxmox VE backup.
    returned: always
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
          - Exclude certain files/directories (shell globs).
          - Paths starting with '/' are anchored to the container's root,
          - other paths match relative to each subdirectory.
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
          - Set IO priority when using the BFQ scheduler.
          - For snapshot and suspend mode backups of VMs,
          - this only affects the compressor.
          - A value of 8 means the idle priority is used,
          - otherwise the best-effort priority is used with the specified value.
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
          - Comma-separated list of email addresses or users
          - that should receive email notifications.
        returned: on success
        type: str
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
          - Currently supported are {{cluster}}, {{guestname}}, {{node}},
          - and {{vmid}}, but more might be added in the future.
          - Needs to be a single line, newline and backslash need to be escaped as '\n' and '\\' respectively.
        returned: on success
        type: str
      performance:
        description:
          - Other performance-related settings.
          - (Possible values [max-workers=<integer>] [,pbs-entries-max=<integer>])
        returned: on success
        type: str
      pigz:
        description:
          - Use pigz instead of gzip when N>0. N=1 uses half of cores,
          - N>1 uses N as thread count.
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
          - Use these retention options instead of those from the storage configuration.
          - (Format [keep-all=<1|0>] [,keep-daily=<N>] [,keep-hourly=<N>]
          - [,keep-last=<N>] [,keep-monthly=<N>] [,keep-weekly=<N>] [,keep-yearly=<N>])
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
          - If true, the job will be run as soon as possible
          - if it was missed while the scheduler was not running.
        returned: on success
        type: bool
      schedule:
        description:
          - Backup schedule.
          - The format is a subset of `systemd` calendar events.
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
          - Zstd threads. N=0 uses half of the available cores,
          - if N is set to a value bigger than 0, N is used as thread count.
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
        auth_keys = ['api_host', 'api_user', 'api_password', 'api_token_id',
                     'api_token_secret', 'validate_certs', 'state']
        task_params = {
            k.replace('_', '-'): (1 if v is True else (0 if v is False else v))
            for k, v in self.module.params.items()
            if k not in auth_keys and v is not None
        }
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
            'choices': ['list', 'present', 'absent'],
            'required': True
        },
        'all': {
            'type': 'bool',
            'default': 0
        },
        'bwlimit': {
            'type': 'int',
            'default': 0
        },
        'comment': {
            'type': 'str'
        },
        'compress': {
            'type': 'str',
            'choices': ['0', '1', 'gzip', 'lzo', 'zstd'],
            'default': '0'
        },
        'dow': {
            'type': 'str'
        },
        'dumpdir': {
            'type': 'str'
        },
        'enabled': {
            'type': 'bool',
            'default': 1
        },
        'exclude': {
            'type': 'str'
        },
        'exclude_path': {
            'type': 'list',
            'choices': ['ignore', 'on'],
            'format': '[<string>, ...]'
        },
        'fleecing': {
            'type': 'str',
            'format': '[[enabled:]<1|0>] [,storage:<storage ID>]'
        },
        'id': {
            'type': 'str'
        },
        'ionice': {
            'type': 'int',
            'default': 8,
            'format': '<integer> (0 - 8)'
        },
        'lockwait': {
            'type': 'int'
        },
        'mailnotification': {
            'type': 'str',
            'choices': ['always', 'failure'],
            'default': 'always'
        },
        'mailto': {
            'type': 'str'
        },
        'maxfiles': {
            'type': 'int',
            'format': '<integer> (1 - N)'
        },
        'mode': {
            'type': 'str',
            'choices': ['snapshot', 'suspend', 'stop'],
            'default': 'snapshot'
        },
        'node': {
            'type': 'str'
        },
        'notes_template': {
            'type': 'str'
        },
        'notification_target': {
            'type': 'str'
        },
        'performance': {
            'type': 'str'
        },
        'pigz': {
            'type': 'int',
            'default': 0
        },
        'pool': {
            'type': 'str'
        },
        'protected': {
            'type': 'bool'
        },
        'prune_backups': {
            'type': 'str',
            'format': '''[keep-all:<1|0>] [,keep-daily:<N>] [,keep-hourly:<N>]
                        [,keep-last:<N>] [,keep-monthly:<N>] [,keep-weekly:<N>]
                        [,keep-yearly:<N>]'''
        },
        'quiet': {
            'type': 'bool',
            'default': 0
        },
        'remove': {
            'type': 'bool',
            'default': 1
        },
        'repeat_missed': {
            'type': 'bool',
            'default': 0
        },
        'schedule': {
            'type': 'str',
            'format': '*-*-* 22:00'
        },
        'script': {
            'type': 'str'
        },
        'starttime': {
            'type': 'str',
            'format': 'HH:MM'
        },
        'stdexcludes': {
            'type': 'bool',
            'default': 1
        },
        'stop': {
            'type': 'bool',
            'default': 0
        },
        'stopwait': {
            'type': 'int',
            'default': 10,
            'format': '<integer> (0 - N)'
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
            'type': 'int',
            'default': 1
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
        mutually_exclusive=[('all', 'pool', 'wmid')],
        supports_check_mode=True,
    )

    proxmox = ProxmoxBackupAnsible(module)

    try:
        if module.params['state'] == 'list':
            backups = proxmox.get_backups(module.params.get('id'))
            result['backups'] = backups
        elif module.params['state'] == 'absent':
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
