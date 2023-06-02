#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2015, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_vmsnapshot
short_description: Manages VM snapshots on Apache CloudStack based clouds.
description:
    - Create, remove and revert VM from snapshots.
author: René Moser (@resmo)
options:
  name:
    description:
      - Unique Name of the snapshot. In CloudStack terms display name.
    type: str
    required: true
    aliases: [ display_name ]
  vm:
    description:
      - Name of the virtual machine.
    type: str
    required: true
  description:
    description:
      - Description of the snapshot.
    type: str
  snapshot_memory:
    description:
      - Snapshot memory if set to true.
    default: no
    type: bool
  zone:
    description:
      - Name of the zone in which the VM is in. If not set, default zone is used.
    type: str
  project:
    description:
      - Name of the project the VM is assigned to.
    type: str
  state:
    description:
      - State of the snapshot.
    type: str
    default: present
    choices: [ present, absent, revert ]
  domain:
    description:
      - Domain the VM snapshot is related to.
    type: str
  account:
    description:
      - Account the VM snapshot is related to.
    type: str
  poll_async:
    description:
      - Poll async jobs until job has finished.
    default: yes
    type: bool
  tags:
    description:
      - List of tags. Tags are a list of dictionaries having keys I(key) and I(value).
      - "To delete all tags, set a empty list e.g. I(tags: [])."
    type: list
    aliases: [ tag ]
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: Create a VM snapshot of disk and memory before an upgrade
  cs_vmsnapshot:
    name: Snapshot before upgrade
    vm: web-01
    snapshot_memory: yes
  delegate_to: localhost

- name: Revert a VM to a snapshot after a failed upgrade
  cs_vmsnapshot:
    name: Snapshot before upgrade
    vm: web-01
    state: revert
  delegate_to: localhost

- name: Remove a VM snapshot after successful upgrade
  cs_vmsnapshot:
    name: Snapshot before upgrade
    vm: web-01
    state: absent
  delegate_to: localhost
'''

RETURN = '''
---
id:
  description: UUID of the snapshot.
  returned: success
  type: str
  sample: a6f7a5fc-43f8-11e5-a151-feff819cdc9f
name:
  description: Name of the snapshot.
  returned: success
  type: str
  sample: snapshot before update
display_name:
  description: Display name of the snapshot.
  returned: success
  type: str
  sample: snapshot before update
created:
  description: date of the snapshot.
  returned: success
  type: str
  sample: 2015-03-29T14:57:06+0200
current:
  description: true if the snapshot is current
  returned: success
  type: bool
  sample: True
state:
  description: state of the vm snapshot
  returned: success
  type: str
  sample: Allocated
type:
  description: type of vm snapshot
  returned: success
  type: str
  sample: DiskAndMemory
description:
  description: description of vm snapshot
  returned: success
  type: str
  sample: snapshot brought to you by Ansible
domain:
  description: Domain the vm snapshot is related to.
  returned: success
  type: str
  sample: example domain
account:
  description: Account the vm snapshot is related to.
  returned: success
  type: str
  sample: example account
project:
  description: Name of project the vm snapshot is related to.
  returned: success
  type: str
  sample: Production
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
    cs_required_together
)


class AnsibleCloudStackVmSnapshot(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackVmSnapshot, self).__init__(module)
        self.returns = {
            'type': 'type',
            'current': 'current',
        }

    def get_snapshot(self):
        args = {
            'virtualmachineid': self.get_vm('id'),
            'account': self.get_account('name'),
            'domainid': self.get_domain('id'),
            'projectid': self.get_project('id'),
            'name': self.module.params.get('name'),
        }
        snapshots = self.query_api('listVMSnapshot', **args)
        if snapshots:
            return snapshots['vmSnapshot'][0]
        return None

    def create_snapshot(self):
        snapshot = self.get_snapshot()
        if not snapshot:
            self.result['changed'] = True

            args = {
                'virtualmachineid': self.get_vm('id'),
                'name': self.module.params.get('name'),
                'description': self.module.params.get('description'),
                'snapshotmemory': self.module.params.get('snapshot_memory'),
            }
            if not self.module.check_mode:
                res = self.query_api('createVMSnapshot', **args)

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    snapshot = self.poll_job(res, 'vmsnapshot')

        if snapshot:
            snapshot = self.ensure_tags(resource=snapshot, resource_type='Snapshot')

        return snapshot

    def remove_snapshot(self):
        snapshot = self.get_snapshot()
        if snapshot:
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('deleteVMSnapshot', vmsnapshotid=snapshot['id'])

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    res = self.poll_job(res, 'vmsnapshot')
        return snapshot

    def revert_vm_to_snapshot(self):
        snapshot = self.get_snapshot()
        if snapshot:
            self.result['changed'] = True

            if snapshot['state'] != "Ready":
                self.module.fail_json(msg="snapshot state is '%s', not ready, could not revert VM" % snapshot['state'])

            if not self.module.check_mode:
                res = self.query_api('revertToVMSnapshot', vmsnapshotid=snapshot['id'])

                poll_async = self.module.params.get('poll_async')
                if res and poll_async:
                    res = self.poll_job(res, 'vmsnapshot')
            return snapshot

        self.module.fail_json(msg="snapshot not found, could not revert VM")


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True, aliases=['display_name']),
        vm=dict(required=True),
        description=dict(),
        zone=dict(),
        snapshot_memory=dict(type='bool', default=False),
        state=dict(choices=['present', 'absent', 'revert'], default='present'),
        domain=dict(),
        account=dict(),
        project=dict(),
        poll_async=dict(type='bool', default=True),
        tags=dict(type='list', aliases=['tag']),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=cs_required_together(),
        supports_check_mode=True
    )

    acs_vmsnapshot = AnsibleCloudStackVmSnapshot(module)

    state = module.params.get('state')
    if state in ['revert']:
        snapshot = acs_vmsnapshot.revert_vm_to_snapshot()
    elif state in ['absent']:
        snapshot = acs_vmsnapshot.remove_snapshot()
    else:
        snapshot = acs_vmsnapshot.create_snapshot()

    result = acs_vmsnapshot.get_result(snapshot)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
