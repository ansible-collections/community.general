#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Scaleway volumes management module
#
# Copyright (C) 2018 Henryk Konsek Consulting (hekonsek@gmail.com).
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: scaleway_volume
short_description: Scaleway volumes management module
author: Henryk Konsek (@hekonsek)
description:
    - This module manages volumes on Scaleway account
      U(https://developer.scaleway.com)
extends_documentation_fragment:
- community.general.scaleway


options:
  state:
    type: str
    description:
     - Indicate desired state of the volume.
    default: present
    choices:
      - present
      - absent
  region:
    type: str
    description:
     - Scaleway region to use (for example par1).
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
     - Name used to identify the volume.
    required: true
  project:
    type: str
    description:
     - Scaleway project ID to which volume belongs.
    version_added: 4.3.0
  organization:
    type: str
    description:
     - ScaleWay organization ID to which volume belongs.
  size:
    type: int
    description:
     - Size of the volume in bytes.
  volume_type:
    type: str
    description:
     - Type of the volume (for example 'l_ssd').
'''

EXAMPLES = '''
- name: Create 10GB volume
  community.general.scaleway_volume:
    name: my-volume
    state: present
    region: par1
    project: "{{ scw_org }}"
    "size": 10000000000
    volume_type: l_ssd
  register: server_creation_check_task

- name: Make sure volume deleted
  community.general.scaleway_volume:
    name: my-volume
    state: absent
    region: par1
'''

RETURN = '''
data:
    description: This is only present when C(state=present)
    returned: when C(state=present)
    type: dict
    sample: {
      "volume": {
        "export_uri": null,
        "id": "c675f420-cfeb-48ff-ba2a-9d2a4dbe3fcd",
        "name": "volume-0-3",
        "project": "000a115d-2852-4b0a-9ce8-47f1134ba95a",
         "server": null,
         "size": 10000000000,
         "volume_type": "l_ssd"
  }
}
'''

from ansible_collections.community.general.plugins.module_utils.scaleway import SCALEWAY_LOCATION, scaleway_argument_spec, Scaleway
from ansible.module_utils.basic import AnsibleModule


def core(module):
    region = module.params["region"]
    state = module.params['state']
    name = module.params['name']
    organization = module.params['organization']
    project = module.params['project']
    size = module.params['size']
    volume_type = module.params['volume_type']
    module.params['api_url'] = SCALEWAY_LOCATION[region]["api_endpoint"]

    account_api = Scaleway(module)
    response = account_api.get('volumes')
    status_code = response.status_code
    volumes_json = response.json

    if project is None:
        project = organization

    if not response.ok:
        module.fail_json(msg='Error getting volume [{0}: {1}]'.format(
            status_code, response.json['message']))

    volumeByName = None
    for volume in volumes_json['volumes']:
        if volume['project'] == project and volume['name'] == name:
            volumeByName = volume

    if state in ('present',):
        if volumeByName is not None:
            module.exit_json(changed=False)

        payload = {'name': name, 'project': project, 'size': size, 'volume_type': volume_type}

        response = account_api.post('/volumes', payload)

        if response.ok:
            module.exit_json(changed=True, data=response.json)

        module.fail_json(msg='Error creating volume [{0}: {1}]'.format(
            response.status_code, response.json))

    elif state in ('absent',):
        if volumeByName is None:
            module.exit_json(changed=False)

        if module.check_mode:
            module.exit_json(changed=True)

        response = account_api.delete('/volumes/' + volumeByName['id'])
        if response.status_code == 204:
            module.exit_json(changed=True, data=response.json)

        module.fail_json(msg='Error deleting volume [{0}: {1}]'.format(
            response.status_code, response.json))


def main():
    argument_spec = scaleway_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['absent', 'present']),
        name=dict(required=True),
        size=dict(type='int'),
        project=dict(),
        organization=dict(),
        volume_type=dict(),
        region=dict(required=True, choices=list(SCALEWAY_LOCATION.keys())),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ('organization', 'project'),
        ],
        required_one_of=[
            ('organization', 'project'),
        ],
    )

    core(module)


if __name__ == '__main__':
    main()
