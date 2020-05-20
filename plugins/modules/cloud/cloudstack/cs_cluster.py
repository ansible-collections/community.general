#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2016, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_cluster
short_description: Manages host clusters on Apache CloudStack based clouds.
description:
    - Create, update and remove clusters.
author: René Moser (@resmo)
options:
  name:
    description:
      - name of the cluster.
    type: str
    required: true
  zone:
    description:
      - Name of the zone in which the cluster belongs to.
      - If not set, default zone is used.
    type: str
  pod:
    description:
      - Name of the pod in which the cluster belongs to.
    type: str
  cluster_type:
    description:
      - Type of the cluster.
      - Required if I(state=present)
    type: str
    choices: [ CloudManaged, ExternalManaged ]
  hypervisor:
    description:
      - Name the hypervisor to be used.
      - Required if I(state=present).
      - Possible values are C(KVM), C(VMware), C(BareMetal), C(XenServer), C(LXC), C(HyperV), C(UCS), C(OVM), C(Simulator).
    type: str
  url:
    description:
      - URL for the cluster
    type: str
  username:
    description:
      - Username for the cluster.
    type: str
  password:
    description:
      - Password for the cluster.
    type: str
  guest_vswitch_name:
    description:
      - Name of virtual switch used for guest traffic in the cluster.
      - This would override zone wide traffic label setting.
    type: str
  guest_vswitch_type:
    description:
      - Type of virtual switch used for guest traffic in the cluster.
      - Allowed values are, vmwaresvs (for VMware standard vSwitch) and vmwaredvs (for VMware distributed vSwitch)
    type: str
    choices: [ vmwaresvs, vmwaredvs ]
  public_vswitch_name:
    description:
      - Name of virtual switch used for public traffic in the cluster.
      - This would override zone wide traffic label setting.
    type: str
  public_vswitch_type:
    description:
      - Type of virtual switch used for public traffic in the cluster.
      - Allowed values are, vmwaresvs (for VMware standard vSwitch) and vmwaredvs (for VMware distributed vSwitch)
    type: str
    choices: [ vmwaresvs, vmwaredvs ]
  vms_ip_address:
    description:
      - IP address of the VSM associated with this cluster.
    type: str
  vms_username:
    description:
      - Username for the VSM associated with this cluster.
    type: str
  vms_password:
    description:
      - Password for the VSM associated with this cluster.
    type: str
  ovm3_cluster:
    description:
      - Ovm3 native OCFS2 clustering enabled for cluster.
    type: str
  ovm3_pool:
    description:
      - Ovm3 native pooling enabled for cluster.
    type: str
  ovm3_vip:
    description:
      - Ovm3 vip to use for pool (and cluster).
    type: str
  state:
    description:
      - State of the cluster.
    type: str
    choices: [ present, absent, disabled, enabled ]
    default: present
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: Ensure a cluster is present
  cs_cluster:
    name: kvm-cluster-01
    zone: ch-zrh-ix-01
    hypervisor: KVM
    cluster_type: CloudManaged
  delegate_to: localhost

- name: Ensure a cluster is disabled
  cs_cluster:
    name: kvm-cluster-01
    zone: ch-zrh-ix-01
    state: disabled
  delegate_to: localhost

- name: Ensure a cluster is enabled
  cs_cluster:
    name: kvm-cluster-01
    zone: ch-zrh-ix-01
    state: enabled
  delegate_to: localhost

- name: Ensure a cluster is absent
  cs_cluster:
    name: kvm-cluster-01
    zone: ch-zrh-ix-01
    state: absent
  delegate_to: localhost
'''

RETURN = '''
---
id:
  description: UUID of the cluster.
  returned: success
  type: str
  sample: 04589590-ac63-4ffc-93f5-b698b8ac38b6
name:
  description: Name of the cluster.
  returned: success
  type: str
  sample: cluster01
allocation_state:
  description: State of the cluster.
  returned: success
  type: str
  sample: Enabled
cluster_type:
  description: Type of the cluster.
  returned: success
  type: str
  sample: ExternalManaged
cpu_overcommit_ratio:
  description: The CPU overcommit ratio of the cluster.
  returned: success
  type: str
  sample: 1.0
memory_overcommit_ratio:
  description: The memory overcommit ratio of the cluster.
  returned: success
  type: str
  sample: 1.0
managed_state:
  description: Whether this cluster is managed by CloudStack.
  returned: success
  type: str
  sample: Managed
ovm3_vip:
  description: Ovm3 VIP to use for pooling and/or clustering
  returned: success
  type: str
  sample: 10.10.10.101
hypervisor:
  description: Hypervisor of the cluster
  returned: success
  type: str
  sample: VMware
zone:
  description: Name of zone the cluster is in.
  returned: success
  type: str
  sample: ch-gva-2
pod:
  description: Name of pod the cluster is in.
  returned: success
  type: str
  sample: pod01
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
    cs_required_together,
)


class AnsibleCloudStackCluster(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackCluster, self).__init__(module)
        self.returns = {
            'allocationstate': 'allocation_state',
            'hypervisortype': 'hypervisor',
            'clustertype': 'cluster_type',
            'podname': 'pod',
            'managedstate': 'managed_state',
            'memoryovercommitratio': 'memory_overcommit_ratio',
            'cpuovercommitratio': 'cpu_overcommit_ratio',
            'ovm3vip': 'ovm3_vip',
        }
        self.cluster = None

    def _get_common_cluster_args(self):
        args = {
            'clustername': self.module.params.get('name'),
            'hypervisor': self.module.params.get('hypervisor'),
            'clustertype': self.module.params.get('cluster_type'),
        }
        state = self.module.params.get('state')
        if state in ['enabled', 'disabled']:
            args['allocationstate'] = state.capitalize()
        return args

    def get_pod(self, key=None):
        args = {
            'name': self.module.params.get('pod'),
            'zoneid': self.get_zone(key='id'),
        }
        pods = self.query_api('listPods', **args)
        if pods:
            return self._get_by_key(key, pods['pod'][0])
        self.module.fail_json(msg="Pod %s not found in zone %s" % (self.module.params.get('pod'), self.get_zone(key='name')))

    def get_cluster(self):
        if not self.cluster:
            args = {}

            uuid = self.module.params.get('id')
            if uuid:
                args['id'] = uuid
                clusters = self.query_api('listClusters', **args)
                if clusters:
                    self.cluster = clusters['cluster'][0]
                    return self.cluster

            args['name'] = self.module.params.get('name')
            clusters = self.query_api('listClusters', **args)
            if clusters:
                self.cluster = clusters['cluster'][0]
                # fix different return from API then request argument given
                self.cluster['hypervisor'] = self.cluster['hypervisortype']
                self.cluster['clustername'] = self.cluster['name']
        return self.cluster

    def present_cluster(self):
        cluster = self.get_cluster()
        if cluster:
            cluster = self._update_cluster()
        else:
            cluster = self._create_cluster()
        return cluster

    def _create_cluster(self):
        required_params = [
            'cluster_type',
            'hypervisor',
        ]
        self.module.fail_on_missing_params(required_params=required_params)

        args = self._get_common_cluster_args()
        args['zoneid'] = self.get_zone(key='id')
        args['podid'] = self.get_pod(key='id')
        args['url'] = self.module.params.get('url')
        args['username'] = self.module.params.get('username')
        args['password'] = self.module.params.get('password')
        args['guestvswitchname'] = self.module.params.get('guest_vswitch_name')
        args['guestvswitchtype'] = self.module.params.get('guest_vswitch_type')
        args['publicvswitchtype'] = self.module.params.get('public_vswitch_name')
        args['publicvswitchtype'] = self.module.params.get('public_vswitch_type')
        args['vsmipaddress'] = self.module.params.get('vms_ip_address')
        args['vsmusername'] = self.module.params.get('vms_username')
        args['vmspassword'] = self.module.params.get('vms_password')
        args['ovm3cluster'] = self.module.params.get('ovm3_cluster')
        args['ovm3pool'] = self.module.params.get('ovm3_pool')
        args['ovm3vip'] = self.module.params.get('ovm3_vip')

        self.result['changed'] = True

        cluster = None
        if not self.module.check_mode:
            res = self.query_api('addCluster', **args)

            # API returns a list as result CLOUDSTACK-9205
            if isinstance(res['cluster'], list):
                cluster = res['cluster'][0]
            else:
                cluster = res['cluster']
        return cluster

    def _update_cluster(self):
        cluster = self.get_cluster()

        args = self._get_common_cluster_args()
        args['id'] = cluster['id']

        if self.has_changed(args, cluster):
            self.result['changed'] = True

            if not self.module.check_mode:
                res = self.query_api('updateCluster', **args)
                cluster = res['cluster']

        return cluster

    def absent_cluster(self):
        cluster = self.get_cluster()
        if cluster:
            self.result['changed'] = True

            args = {
                'id': cluster['id'],
            }

            if not self.module.check_mode:
                self.query_api('deleteCluster', **args)

        return cluster


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        zone=dict(),
        pod=dict(),
        cluster_type=dict(choices=['CloudManaged', 'ExternalManaged']),
        hypervisor=dict(),
        state=dict(choices=['present', 'enabled', 'disabled', 'absent'], default='present'),
        url=dict(),
        username=dict(),
        password=dict(no_log=True),
        guest_vswitch_name=dict(),
        guest_vswitch_type=dict(choices=['vmwaresvs', 'vmwaredvs']),
        public_vswitch_name=dict(),
        public_vswitch_type=dict(choices=['vmwaresvs', 'vmwaredvs']),
        vms_ip_address=dict(),
        vms_username=dict(),
        vms_password=dict(no_log=True),
        ovm3_cluster=dict(),
        ovm3_pool=dict(),
        ovm3_vip=dict(),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=cs_required_together(),
        supports_check_mode=True
    )

    acs_cluster = AnsibleCloudStackCluster(module)

    state = module.params.get('state')
    if state in ['absent']:
        cluster = acs_cluster.absent_cluster()
    else:
        cluster = acs_cluster.present_cluster()

    result = acs_cluster.get_result(cluster)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
