#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway VPC management module
#
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: scaleway_compute_private_network
short_description: Scaleway compute - private network management
version_added: 5.2.0
author: Pascal MANGIN (@pastral)
description:
  - This module add or remove a private network to a compute instance (U(https://developer.scaleway.com)).
extends_documentation_fragment:
  - community.general.scaleway
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  state:
    type: str
    description:
      - Indicate desired state of the VPC.
    default: present
    choices:
      - present
      - absent

  project:
    type: str
    description:
      - Project identifier.
    required: true

  region:
    type: str
    description:
      - Scaleway region to use (for example V(par1)).
    required: true
    choices:
      - ams1
      - EMEA-NL-EVS
      - ams2
      - ams3
      - par1
      - EMEA-FR-PAR1
      - par2
      - EMEA-FR-PAR2
      - par3
      - waw1
      - EMEA-PL-WAW1
      - waw2
      - waw3

  compute_id:
    type: str
    description:
      - ID of the compute instance (see M(community.general.scaleway_compute)).
    required: true

  private_network_id:
    type: str
    description:
      - ID of the private network (see M(community.general.scaleway_private_network)).
    required: true
"""

EXAMPLES = r"""
- name: Plug a VM to a private network
  community.general.scaleway_compute_private_network:
    project: '{{ scw_project }}'
    state: present
    region: par1
    compute_id: "12345678-f1e6-40ec-83e5-12345d67ed89"
    private_network_id: "22345678-f1e6-40ec-83e5-12345d67ed89"
  register: nicsvpc_creation_task

- name: Unplug a VM from a private network
  community.general.scaleway_compute_private_network:
    project: '{{ scw_project }}'
    state: absent
    region: par1
    compute_id: "12345678-f1e6-40ec-83e5-12345d67ed89"
    private_network_id: "22345678-f1e6-40ec-83e5-12345d67ed89"
"""

RETURN = r"""
scaleway_compute_private_network:
  description: Information on the VPC.
  returned: success when O(state=present)
  type: dict
  sample:
    {
      "created_at": "2022-01-15T11:11:12.676445Z",
      "id": "12345678-f1e6-40ec-83e5-12345d67ed89",
      "name": "network",
      "organization_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
      "project_id": "a123b4cd-ef5g-678h-90i1-jk2345678l90",
      "tags": [
        "tag1",
        "tag2",
        "tag3",
        "tag4",
        "tag5"
      ],
      "updated_at": "2022-01-15T11:12:04.624837Z",
      "zone": "fr-par-2"
    }
"""

from ansible_collections.community.general.plugins.module_utils.scaleway import SCALEWAY_LOCATION, scaleway_argument_spec, Scaleway
from ansible.module_utils.basic import AnsibleModule


def get_nics_info(api, compute_id, private_network_id):

    response = api.get('servers/' + compute_id + '/private_nics')
    if not response.ok:
        msg = "Error during get servers information: %s: '%s' (%s)" % (response.info['msg'], response.json['message'], response.json)
        api.module.fail_json(msg=msg)

    i = 0
    list_nics = response.json['private_nics']

    while i < len(list_nics):
        if list_nics[i]['private_network_id'] == private_network_id:
            return list_nics[i]
        i += 1

    return None


def present_strategy(api, compute_id, private_network_id):

    changed = False
    nic = get_nics_info(api, compute_id, private_network_id)
    if nic is not None:
        return changed, nic

    data = {"private_network_id": private_network_id}
    changed = True
    if api.module.check_mode:
        return changed, {"status": "a private network would be add to a server"}

    response = api.post(path='servers/' + compute_id + '/private_nics', data=data)

    if not response.ok:
        api.module.fail_json(msg='Error when adding a private network to a server [{0}: {1}]'.format(response.status_code, response.json))

    return changed, response.json


def absent_strategy(api, compute_id, private_network_id):

    changed = False
    nic = get_nics_info(api, compute_id, private_network_id)
    if nic is None:
        return changed, {}

    changed = True
    if api.module.check_mode:
        return changed, {"status": "private network would be destroyed"}

    response = api.delete('servers/' + compute_id + '/private_nics/' + nic['id'])

    if not response.ok:
        api.module.fail_json(msg='Error deleting private network from server [{0}: {1}]'.format(
            response.status_code, response.json))

    return changed, response.json


def core(module):

    compute_id = module.params['compute_id']
    pn_id = module.params['private_network_id']

    region = module.params["region"]
    module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint"]

    api = Scaleway(module=module)
    if module.params["state"] == "absent":
        changed, summary = absent_strategy(api=api, compute_id=compute_id, private_network_id=pn_id)
    else:
        changed, summary = present_strategy(api=api, compute_id=compute_id, private_network_id=pn_id)
    module.exit_json(changed=changed, scaleway_compute_private_network=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['absent', 'present']),
        project=dict(required=True),
        region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())),
        compute_id=dict(required=True),
        private_network_id=dict(required=True)
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()
