#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway VPC management module
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_vpc
short_description: Scaleway VPC management module
author: Pascal MANGIN (@pastral)
description:
    - This module manages VPC on Scaleway account ( inspired by Scaleway_ip )
      U(https://developer.scaleway.com)
extends_documentation_fragment:
- community.general.scaleway


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
     - Scaleway region to use (for example par1)
    required: true
    choices:
      - ams1
      - EMEA-NL-EVS
      - par1
      - EMEA-FR-PAR1
      - par2
      - EMEA-FR-PAR2
      - waw1
      - EMEA-PL-WAW1

  name:
    type: str
    description:
    - namle of the vpc

'''

EXAMPLES = '''
- name: Create an VPC
  community.general.scaleway_vpc:
    project: '{{ scw_project }}'
    name: 'vpc_one'
    state: present
    region: par1
  register: vpc_creation_task

- name: Make sure VPC deleted
  community.general.scaleway_ip:
    id: '{{ vpc_creation_task.scaleway_ip.id }}'
    state: absent
    region: par1
'''

RETURN = '''
data:
    description: This is only present when C(state=present)
    returned: when C(state=present)
    type: dict
    sample: {
      "ips": [
        {
            "organization": "951df375-e094-4d26-97c1-ba548eeb9c42",
            "reverse": null,
            "id": "dd9e8df6-6775-4863-b517-e0b0ee3d7477",
            "server": {
                "id": "3f1568ca-b1a2-4e98-b6f7-31a0588157f1",
                "name": "ansible_tuto-1"
            },
            "address": "212.47.232.136"
        }
    ]
    }
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import SCALEWAY_LOCATION, scaleway_argument_spec, Scaleway
from ansible.module_utils.basic import AnsibleModule

def get_private_network_id(api, name):
    response = api.get('private-networks')

    # a amélioré si plusier nom proche /changer message
    if not creation_response.ok:
        msg = "Error during ip creation: %s: '%s' (%s)" % (creation_response.info['msg'],
                                                               creation_response.json['message'],
                                                               creation_response.json)
            api.module.fail_json(msg=msg)

    if response.json['private_networks[0].name'] == name:
        
        return response.json['private_networks[0].id']
        
    return None

def present_strategy(api, wished_private_network):

    changed = False
    private_network_id = get_private_network_id(api, wished_private_network['name'])
    if(private_network_id is not None:
       return changed, {}

    changed = True
    if api.module.check_mode:
        return changed, {"status": "private network would be created"}

    data = {
        'name' : wished_private_network['name'],
        'project_id' : wished_private_network['project']
        }

    response = api.post(path='private-networks/'+private_network_id, data=data)

    if not response.ok:
       api.module.fail_json(msg='Error creating private network [{0}: {1}]'.format(
           response.status_code, response.json))

    return changed, response.json

def absent_strategy(api, wished_private_network):

    changed = False
    private_network_id = get_private_network_id(api, wished_private_network['name'])
    if(private_network_id is None:
       return changed, {}

    changed = True
    if api.module.check_mode:
        return changed, {"status": "private network would be destroyed"}
       
    response = api.delete('private-networks/'+private_network_id)

    if not response.ok:
       api.module.fail_json(msg='Error deleting private network [{0}: {1}]'.format(
           response.status_code, response.json))

    return changed, response.json

       
def core(module):

    wished_private_network = {
        "project": module.params['project'],
        "name": module.params['name']
    }
       
    region = module.params["region"]
    module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint"]

    api = Scaleway(module=module)
    if module.params["state"] == "absent":
        changed, summary = absent_strategy(api=api, wished_private_network=wished_private_network)
    else:
        changed, summary = present_strategy(api=api, wished_private_network=wished_private_network)
    module.exit_json(changed=changed, scaleway_private_network=summary)


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['absent', 'present']),
        project=dict(required=True),
        region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())),
        name=dict()
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()
