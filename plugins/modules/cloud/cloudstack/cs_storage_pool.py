#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2017, Netservers Ltd. <support@netservers.co.uk>
# (c) 2017, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_storage_pool
short_description: Manages Primary Storage Pools on Apache CloudStack based clouds.
description:
    - Create, update, put into maintenance, disable, enable and remove storage pools.
author:
    - Netservers Ltd. (@netservers)
    - René Moser (@resmo)
options:
  name:
    description:
      - Name of the storage pool.
    type: str
    required: true
  zone:
    description:
      - Name of the zone in which the host should be deployed.
      - If not set, default zone is used.
    type: str
  storage_url:
    description:
      - URL of the storage pool.
      - Required if I(state=present).
    type: str
  pod:
    description:
      - Name of the pod.
    type: str
  cluster:
    description:
      - Name of the cluster.
    type: str
  scope:
    description:
      - The scope of the storage pool.
      - Defaults to cluster when C(cluster) is provided, otherwise zone.
    type: str
    choices: [ cluster, zone ]
  managed:
    description:
      - Whether the storage pool should be managed by CloudStack.
      - Only considered on creation.
    type: bool
  hypervisor:
    description:
      - Required when creating a zone scoped pool.
      - Possible values are C(KVM), C(VMware), C(BareMetal), C(XenServer), C(LXC), C(HyperV), C(UCS), C(OVM), C(Simulator).
    type: str
  storage_tags:
    description:
      - Tags associated with this storage pool.
    type: list
    aliases: [ storage_tag ]
  provider:
    description:
      - Name of the storage provider e.g. SolidFire, SolidFireShared, DefaultPrimary, CloudByte.
    type: str
    default: DefaultPrimary
  capacity_bytes:
    description:
      - Bytes CloudStack can provision from this storage pool.
    type: int
  capacity_iops:
    description:
      - Bytes CloudStack can provision from this storage pool.
    type: int
  allocation_state:
    description:
      - Allocation state of the storage pool.
    type: str
    choices: [ enabled, disabled, maintenance ]
  state:
    description:
      - State of the storage pool.
    type: str
    default: present
    choices: [ present, absent ]
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: ensure a zone scoped storage_pool is present
  cs_storage_pool:
    zone: zone01
    storage_url: rbd://admin:SECRET@ceph-mons.domain/poolname
    provider: DefaultPrimary
    name: Ceph RBD
    scope: zone
    hypervisor: KVM
  delegate_to: localhost

- name: ensure a cluster scoped storage_pool is disabled
  cs_storage_pool:
    name: Ceph RBD
    zone: zone01
    cluster: cluster01
    pod: pod01
    storage_url: rbd://admin:SECRET@ceph-the-mons.domain/poolname
    provider: DefaultPrimary
    scope: cluster
    allocation_state: disabled
  delegate_to: localhost

- name: ensure a cluster scoped storage_pool is in maintenance
  cs_storage_pool:
    name: Ceph RBD
    zone: zone01
    cluster: cluster01
    pod: pod01
    storage_url: rbd://admin:SECRET@ceph-the-mons.domain/poolname
    provider: DefaultPrimary
    scope: cluster
    allocation_state: maintenance
  delegate_to: localhost

- name: ensure a storage_pool is absent
  cs_storage_pool:
    name: Ceph RBD
    state: absent
  delegate_to: localhost
'''

RETURN = '''
---
id:
  description: UUID of the pool.
  returned: success
  type: str
  sample: a3fca65a-7db1-4891-b97c-48806a978a96
created:
  description: Date of the pool was created.
  returned: success
  type: str
  sample: 2014-12-01T14:57:57+0100
capacity_iops:
  description: IOPS CloudStack can provision from this storage pool
  returned: when available
  type: int
  sample: 60000
zone:
  description: The name of the zone.
  returned: success
  type: str
  sample: Zone01
cluster:
  description: The name of the cluster.
  returned: when scope is cluster
  type: str
  sample: Cluster01
pod:
  description: The name of the pod.
  returned: when scope is cluster
  type: str
  sample: Cluster01
disk_size_allocated:
  description: The pool's currently allocated disk space.
  returned: success
  type: int
  sample: 2443517624320
disk_size_total:
  description: The total size of the pool.
  returned: success
  type: int
  sample: 3915055693824
disk_size_used:
  description: The pool's currently used disk size.
  returned: success
  type: int
  sample: 1040862622180
scope:
  description: The scope of the storage pool.
  returned: success
  type: str
  sample: cluster
hypervisor:
  description: Hypervisor related to this storage pool.
  returned: when available
  type: str
  sample: KVM
state:
  description: The state of the storage pool as returned by the API.
  returned: success
  type: str
  sample: Up
allocation_state:
  description: The state of the storage pool.
  returned: success
  type: str
  sample: enabled
path:
  description: The storage pool path used in the storage_url.
  returned: success
  type: str
  sample: poolname
overprovision_factor:
  description: The overprovision factor of the storage pool.
  returned: success
  type: str
  sample: 2.0
suitable_for_migration:
  description: Whether the storage pool is suitable to migrate a volume or not.
  returned: success
  type: bool
  sample: false
storage_capabilities:
  description: Capabilities of the storage pool.
  returned: success
  type: dict
  sample: {"VOLUME_SNAPSHOT_QUIESCEVM": "false"}
storage_tags:
  description: the tags for the storage pool.
  returned: success
  type: list
  sample: ["perf", "ssd"]
'''

# import cloudstack common
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
    cs_required_together,
)


class AnsibleCloudStackStoragePool(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackStoragePool, self).__init__(module)
        self.returns = {
            'capacityiops': 'capacity_iops',
            'podname': 'pod',
            'clustername': 'cluster',
            'disksizeallocated': 'disk_size_allocated',
            'disksizetotal': 'disk_size_total',
            'disksizeused': 'disk_size_used',
            'scope': 'scope',
            'hypervisor': 'hypervisor',
            'type': 'type',
            'ip_address': 'ipaddress',
            'path': 'path',
            'overprovisionfactor': 'overprovision_factor',
            'storagecapabilities': 'storage_capabilities',
            'suitableformigration': 'suitable_for_migration',
        }
        self.allocation_states = {
            # Host state: param state
            'Up': 'enabled',
            'Disabled': 'disabled',
            'Maintenance': 'maintenance',
        }
        self.storage_pool = None

    def _get_common_args(self):
        return {
            'name': self.module.params.get('name'),
            'url': self.module.params.get('storage_url'),
            'zoneid': self.get_zone(key='id'),
            'provider': self.get_storage_provider(),
            'scope': self.module.params.get('scope'),
            'hypervisor': self.module.params.get('hypervisor'),
            'capacitybytes': self.module.params.get('capacity_bytes'),
            'capacityiops': self.module.params.get('capacity_iops'),
        }

    def _allocation_state_enabled_disabled_changed(self, pool, allocation_state):
        if allocation_state in ['enabled', 'disabled']:
            for pool_state, param_state in self.allocation_states.items():
                if pool_state == pool['state'] and allocation_state != param_state:
                    return True
        return False

    def _handle_allocation_state(self, pool, state=None):
        allocation_state = state or self.module.params.get('allocation_state')
        if not allocation_state:
            return pool

        if self.allocation_states.get(pool['state']) == allocation_state:
            return pool

        # Cancel maintenance if target state is enabled/disabled
        elif allocation_state in ['enabled', 'disabled']:
            pool = self._cancel_maintenance(pool)
            pool = self._update_storage_pool(pool=pool, allocation_state=allocation_state)

        # Only an enabled host can put in maintenance
        elif allocation_state == 'maintenance':
            pool = self._update_storage_pool(pool=pool, allocation_state='enabled')
            pool = self._enable_maintenance(pool=pool)

        return pool

    def _create_storage_pool(self):
        args = self._get_common_args()
        args.update({
            'clusterid': self.get_cluster(key='id'),
            'podid': self.get_pod(key='id'),
            'managed': self.module.params.get('managed'),
        })

        scope = self.module.params.get('scope')
        if scope is None:
            args['scope'] = 'cluster' if args['clusterid'] else 'zone'

        self.result['changed'] = True

        if not self.module.check_mode:
            res = self.query_api('createStoragePool', **args)
            return res['storagepool']

    def _update_storage_pool(self, pool, allocation_state=None):
        args = {
            'id': pool['id'],
            'capacitybytes': self.module.params.get('capacity_bytes'),
            'capacityiops': self.module.params.get('capacity_iops'),
            'tags': self.get_storage_tags(),
        }

        if self.has_changed(args, pool) or self._allocation_state_enabled_disabled_changed(pool, allocation_state):
            self.result['changed'] = True
            args['enabled'] = allocation_state == 'enabled' if allocation_state in ['enabled', 'disabled'] else None
            if not self.module.check_mode:
                res = self.query_api('updateStoragePool', **args)
                pool = res['storagepool']
        return pool

    def _enable_maintenance(self, pool):
        if pool['state'].lower() != "maintenance":
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('enableStorageMaintenance', id=pool['id'])
                pool = self.poll_job(res, 'storagepool')
        return pool

    def _cancel_maintenance(self, pool):
        if pool['state'].lower() == "maintenance":
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('cancelStorageMaintenance', id=pool['id'])
                pool = self.poll_job(res, 'storagepool')
        return pool

    def get_storage_tags(self):
        storage_tags = self.module.params.get('storage_tags')
        if storage_tags is None:
            return None
        return ','.join(storage_tags)

    def get_storage_pool(self, key=None):
        if self.storage_pool is None:
            zoneid = self.get_zone(key='id')
            clusterid = self.get_cluster(key='id')
            podid = self.get_pod(key='id')

            args = {
                'zoneid': zoneid,
                'podid': podid,
                'clusterid': clusterid,
                'name': self.module.params.get('name'),
            }

            res = self.query_api('listStoragePools', **args)
            if 'storagepool' not in res:
                return None

            self.storage_pool = res['storagepool'][0]

        return self.storage_pool

    def present_storage_pool(self):
        pool = self.get_storage_pool()
        if pool:
            pool = self._update_storage_pool(pool=pool)
        else:
            pool = self._create_storage_pool()

        if pool:
            pool = self._handle_allocation_state(pool=pool)

        return pool

    def absent_storage_pool(self):
        pool = self.get_storage_pool()
        if pool:
            self.result['changed'] = True

            args = {
                'id': pool['id'],
            }
            if not self.module.check_mode:
                # Only a pool in maintenance can be deleted
                self._handle_allocation_state(pool=pool, state='maintenance')
                self.query_api('deleteStoragePool', **args)
        return pool

    def get_storage_provider(self, type="primary"):
        args = {
            'type': type,
        }
        provider = self.module.params.get('provider')
        storage_providers = self.query_api('listStorageProviders', **args)
        for sp in storage_providers.get('dataStoreProvider') or []:
            if sp['name'].lower() == provider.lower():
                return provider
        self.fail_json(msg="Storage provider %s not found" % provider)

    def get_pod(self, key=None):
        pod = self.module.params.get('pod')
        if not pod:
            return None
        args = {
            'name': pod,
            'zoneid': self.get_zone(key='id'),
        }
        pods = self.query_api('listPods', **args)
        if pods:
            return self._get_by_key(key, pods['pod'][0])

        self.fail_json(msg="Pod %s not found" % self.module.params.get('pod'))

    def get_cluster(self, key=None):
        cluster = self.module.params.get('cluster')
        if not cluster:
            return None

        args = {
            'name': cluster,
            'zoneid': self.get_zone(key='id'),
        }

        clusters = self.query_api('listClusters', **args)
        if clusters:
            return self._get_by_key(key, clusters['cluster'][0])

        self.fail_json(msg="Cluster %s not found" % cluster)

    def get_result(self, pool):
        super(AnsibleCloudStackStoragePool, self).get_result(pool)
        if pool:
            self.result['storage_url'] = "%s://%s/%s" % (pool['type'], pool['ipaddress'], pool['path'])
            self.result['scope'] = pool['scope'].lower()
            self.result['storage_tags'] = pool['tags'].split(',') if pool.get('tags') else []
            self.result['allocation_state'] = self.allocation_states.get(pool['state'])
        return self.result


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        storage_url=dict(),
        zone=dict(),
        pod=dict(),
        cluster=dict(),
        scope=dict(choices=['zone', 'cluster']),
        hypervisor=dict(),
        provider=dict(default='DefaultPrimary'),
        capacity_bytes=dict(type='int'),
        capacity_iops=dict(type='int'),
        managed=dict(type='bool'),
        storage_tags=dict(type='list', aliases=['storage_tag']),
        allocation_state=dict(choices=['enabled', 'disabled', 'maintenance']),
        state=dict(choices=['present', 'absent'], default='present'),
    ))

    required_together = cs_required_together()
    required_together.extend([
        ['pod', 'cluster'],
    ])
    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=required_together,
        required_if=[
            ('state', 'present', ['storage_url']),
        ],
        supports_check_mode=True
    )

    acs_storage_pool = AnsibleCloudStackStoragePool(module)

    state = module.params.get('state')
    if state in ['absent']:
        pool = acs_storage_pool.absent_storage_pool()
    else:
        pool = acs_storage_pool.present_storage_pool()

    result = acs_storage_pool.get_result(pool)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
