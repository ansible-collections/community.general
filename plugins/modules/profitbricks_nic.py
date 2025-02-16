#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: profitbricks_nic
short_description: Create or Remove a NIC
description:
  - This module allows you to create or restore a volume snapshot. This module has a dependency on profitbricks >= 1.0.0.
deprecated:
  removed_in: 11.0.0
  why: Module relies on library unsupported since 2021.
  alternative: >
    Profitbricks has rebranded as Ionos Cloud and they provide a collection named ionoscloudsdk.ionoscloud.
    Whilst it is likely it will provide the features of this module, that has not been verified.
    Please refer to that collection's documentation for more details.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  datacenter:
    description:
      - The datacenter in which to operate.
    type: str
    required: true
  server:
    description:
      - The server name or ID.
    type: str
    required: true
  name:
    description:
      - The name or ID of the NIC. This is only required on deletes, but not on create.
      - If not specified, it defaults to a value based on UUID4.
    type: str
  lan:
    description:
      - The LAN to place the NIC on. You can pass a LAN that does not exist and it will be created. Required on create.
    type: str
  subscription_user:
    description:
      - The ProfitBricks username. Overrides the E(PB_SUBSCRIPTION_ID) environment variable.
    type: str
    required: true
  subscription_password:
    description:
      - THe ProfitBricks password. Overrides the E(PB_PASSWORD) environment variable.
    type: str
    required: true
  wait:
    description:
      - Wait for the operation to complete before returning.
    required: false
    default: true
    type: bool
  wait_timeout:
    description:
      - How long before wait gives up, in seconds.
    type: int
    default: 600
  state:
    description:
      - Indicate desired state of the resource.
      - 'The available choices are: V(present), V(absent).'
    type: str
    required: false
    default: 'present'

requirements: ["profitbricks"]
author: Matt Baldwin (@baldwinSPC) <baldwin@stackpointcloud.com>
"""

EXAMPLES = r"""
- name: Create a NIC
  community.general.profitbricks_nic:
    datacenter: Tardis One
    server: node002
    lan: 2
    wait_timeout: 500
    state: present

- name: Remove a NIC
  community.general.profitbricks_nic:
    datacenter: Tardis One
    server: node002
    name: 7341c2454f
    wait_timeout: 500
    state: absent
"""

import re
import uuid
import time

HAS_PB_SDK = True
try:
    from profitbricks.client import ProfitBricksService, NIC
except ImportError:
    HAS_PB_SDK = False

from ansible.module_utils.basic import AnsibleModule


uuid_match = re.compile(
    r'[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}', re.I)


def _make_default_name():
    return str(uuid.uuid4()).replace('-', '')[:10]


def _wait_for_completion(profitbricks, promise, wait_timeout, msg):
    if not promise:
        return
    wait_timeout = time.time() + wait_timeout
    while wait_timeout > time.time():
        time.sleep(5)
        operation_result = profitbricks.get_request(
            request_id=promise['requestId'],
            status=True)

        if operation_result['metadata']['status'] == "DONE":
            return
        elif operation_result['metadata']['status'] == "FAILED":
            raise Exception(
                'Request failed to complete ' + msg + ' "' + str(
                    promise['requestId']) + '" to complete.')

    raise Exception(
        'Timed out waiting for async operation ' + msg + ' "' + str(
            promise['requestId']
        ) + '" to complete.')


def create_nic(module, profitbricks):
    """
    Creates a NIC.

    module : AnsibleModule object
    profitbricks: authenticated profitbricks object.

    Returns:
        True if the nic creates, false otherwise
    """
    datacenter = module.params.get('datacenter')
    server = module.params.get('server')
    lan = module.params.get('lan')
    name = module.params.get('name')
    if name is None:
        name = _make_default_name()
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')

    # Locate UUID for Datacenter
    if not (uuid_match.match(datacenter)):
        datacenter_list = profitbricks.list_datacenters()
        for d in datacenter_list['items']:
            dc = profitbricks.get_datacenter(d['id'])
            if datacenter == dc['properties']['name']:
                datacenter = d['id']
                break

    # Locate UUID for Server
    if not (uuid_match.match(server)):
        server_list = profitbricks.list_servers(datacenter)
        for s in server_list['items']:
            if server == s['properties']['name']:
                server = s['id']
                break
    try:
        n = NIC(
            name=name,
            lan=lan
        )

        nic_response = profitbricks.create_nic(datacenter, server, n)

        if wait:
            _wait_for_completion(profitbricks, nic_response,
                                 wait_timeout, "create_nic")

        return nic_response

    except Exception as e:
        module.fail_json(msg="failed to create the NIC: %s" % str(e))


def delete_nic(module, profitbricks):
    """
    Removes a NIC

    module : AnsibleModule object
    profitbricks: authenticated profitbricks object.

    Returns:
        True if the NIC was removed, false otherwise
    """
    datacenter = module.params.get('datacenter')
    server = module.params.get('server')
    name = module.params.get('name')
    if name is None:
        name = _make_default_name()

    # Locate UUID for Datacenter
    if not (uuid_match.match(datacenter)):
        datacenter_list = profitbricks.list_datacenters()
        for d in datacenter_list['items']:
            dc = profitbricks.get_datacenter(d['id'])
            if datacenter == dc['properties']['name']:
                datacenter = d['id']
                break

    # Locate UUID for Server
    server_found = False
    if not (uuid_match.match(server)):
        server_list = profitbricks.list_servers(datacenter)
        for s in server_list['items']:
            if server == s['properties']['name']:
                server_found = True
                server = s['id']
                break

        if not server_found:
            return False

    # Locate UUID for NIC
    nic_found = False
    if not (uuid_match.match(name)):
        nic_list = profitbricks.list_nics(datacenter, server)
        for n in nic_list['items']:
            if name == n['properties']['name']:
                nic_found = True
                name = n['id']
                break

        if not nic_found:
            return False

    try:
        nic_response = profitbricks.delete_nic(datacenter, server, name)
        return nic_response
    except Exception as e:
        module.fail_json(msg="failed to remove the NIC: %s" % str(e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            datacenter=dict(required=True),
            server=dict(required=True),
            name=dict(),
            lan=dict(),
            subscription_user=dict(required=True),
            subscription_password=dict(required=True, no_log=True),
            wait=dict(type='bool', default=True),
            wait_timeout=dict(type='int', default=600),
            state=dict(default='present'),
        ),
        required_if=(
            ('state', 'absent', ['name']),
            ('state', 'present', ['lan']),
        )
    )

    if not HAS_PB_SDK:
        module.fail_json(msg='profitbricks required for this module')

    subscription_user = module.params.get('subscription_user')
    subscription_password = module.params.get('subscription_password')

    profitbricks = ProfitBricksService(
        username=subscription_user,
        password=subscription_password)

    state = module.params.get('state')

    if state == 'absent':
        try:
            (changed) = delete_nic(module, profitbricks)
            module.exit_json(changed=changed)
        except Exception as e:
            module.fail_json(msg='failed to set nic state: %s' % str(e))

    elif state == 'present':
        try:
            (nic_dict) = create_nic(module, profitbricks)
            module.exit_json(nics=nic_dict)  # @FIXME changed not calculated?
        except Exception as e:
            module.fail_json(msg='failed to set nic state: %s' % str(e))


if __name__ == '__main__':
    main()
