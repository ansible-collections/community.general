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

DOCUMENTATION = '''
---
module: scaleway_private_network
short_description: Scaleway private network management
version_added: 4.5.0
author: Pascal MANGIN (@pastral)
description:
    - "This module manages private network on Scaleway account (U(https://developer.scaleway.com))."
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
     - Scaleway region to use (for example C(par1)).
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
    - Name of the VPC.

  tags:
    type: list
    elements: str
    description:
    - List of tags to apply to the instance.
    default: []

'''

EXAMPLES = '''
- name: Create an private network
  community.general.scaleway_vpc:
    project: '{{ scw_project }}'
    name: 'vpc_one'
    state: present
    region: par1
  register: vpc_creation_task

- name: Make sure private network with name 'foo' is deleted in region par1
  community.general.scaleway_vpc:
    name: 'foo'
    state: absent
    region: par1
'''

RETURN = '''
scaleway_private_network:
    description: Information on the VPC.
    returned: success when I(state=present)
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
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import SCALEWAY_LOCATION, scaleway_argument_spec, Scaleway
from ansible.module_utils.basic import AnsibleModule


def get_private_network(api, name, page=1):
    page_size = 10
    response = api.get('private-networks', params={'name': name, 'order_by': 'name_asc', 'page': page, 'page_size': page_size})
    if not response.ok:
        msg = "Error during get private network creation: %s: '%s' (%s)" % (response.info['msg'], response.json['message'], response.json)
        api.module.fail_json(msg=msg)

    if response.json['total_count'] == 0:
        return None

    i = 0
    while i < len(response.json['private_networks']):
        if response.json['private_networks'][i]['name'] == name:
            return response.json['private_networks'][i]
        i += 1

    # search on next page if needed
    if (page * page_size) < response.json['total_count']:
        return get_private_network(api, name, page + 1)

    return None


def present_strategy(api, wished_private_network):

    changed = False
    private_network = get_private_network(api, wished_private_network['name'])
    if private_network is not None:
        if set(wished_private_network['tags']) == set(private_network['tags']):
            return changed, private_network
        else:
            # private network need to be updated
            data = {'name': wished_private_network['name'],
                    'tags': wished_private_network['tags']
                    }
            changed = True
            if api.module.check_mode:
                return changed, {"status": "private network would be updated"}

            response = api.patch(path='private-networks/' + private_network['id'], data=data)
            if not response.ok:
                api.module.fail_json(msg='Error updating private network [{0}: {1}]'.format(response.status_code, response.json))

            return changed, response.json

    # private network need to be create
    changed = True
    if api.module.check_mode:
        return changed, {"status": "private network would be created"}

    data = {'name': wished_private_network['name'],
            'project_id': wished_private_network['project'],
            'tags': wished_private_network['tags']
            }

    response = api.post(path='private-networks/', data=data)

    if not response.ok:
        api.module.fail_json(msg='Error creating private network [{0}: {1}]'.format(response.status_code, response.json))

    return changed, response.json


def absent_strategy(api, wished_private_network):

    changed = False
    private_network = get_private_network(api, wished_private_network['name'])
    if private_network is None:
        return changed, {}

    changed = True
    if api.module.check_mode:
        return changed, {"status": "private network would be destroyed"}

    response = api.delete('private-networks/' + private_network['id'])

    if not response.ok:
        api.module.fail_json(msg='Error deleting private network [{0}: {1}]'.format(
            response.status_code, response.json))

    return changed, response.json


def core(module):

    wished_private_network = {
        "project": module.params['project'],
        "tags": module.params['tags'],
        "name": module.params['name']
    }

    region = module.params["region"]
    module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint_vpc"]

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
        tags=dict(type="list", elements="str", default=[]),
        name=dict()
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    core(module)


if __name__ == '__main__':
    main()
