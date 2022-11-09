#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: linode_v4
short_description: Manage instances on the Linode cloud
description: Manage instances on the Linode cloud.
requirements:
  - python >= 2.7
  - linode_api4 >= 2.0.0
author:
  - Luke Murphy (@decentral1se)
notes:
  - No Linode resizing is currently implemented. This module will, in time,
    replace the current Linode module which uses deprecated API bindings on the
    Linode side.
options:
  region:
    description:
      - The region of the instance. This is a required parameter only when
        creating Linode instances. See
        U(https://www.linode.com/docs/api/regions/).
    type: str
  image:
    description:
      - The image of the instance. This is a required parameter only when
        creating Linode instances. See
        U(https://www.linode.com/docs/api/images/).
    type: str
  type:
    description:
      - The type of the instance. This is a required parameter only when
        creating Linode instances. See
        U(https://www.linode.com/docs/api/linode-types/).
    type: str
  label:
    description:
      - The instance label. This label is used as the main determiner for
        idempotence for the module and is therefore mandatory.
    type: str
    required: true
  group:
    description:
       - The group that the instance should be marked under. Please note, that
         group labelling is deprecated but still supported. The encouraged
         method for marking instances is to use tags.
    type: str
  private_ip:
    description:
      - If C(true), the created Linode will have private networking enabled and
        assigned a private IPv4 address.
    type: bool
    default: false
    version_added: 3.0.0
  tags:
    description:
      - The tags that the instance should be marked under. See
        U(https://www.linode.com/docs/api/tags/).
    type: list
    elements: str
  root_pass:
    description:
      - The password for the root user. If not specified, one will be
        generated. This generated password will be available in the task
        success JSON.
    type: str
  authorized_keys:
    description:
      - A list of SSH public key parts to deploy for the root user.
    type: list
    elements: str
  state:
    description:
      - The desired instance state.
    type: str
    choices:
        - present
        - absent
    required: true
  access_token:
    description:
      - The Linode API v4 access token. It may also be specified by exposing
        the C(LINODE_ACCESS_TOKEN) environment variable. See
        U(https://www.linode.com/docs/api#access-and-authentication).
    required: true
    type: str
  stackscript_id:
    description:
      - The numeric ID of the StackScript to use when creating the instance.
        See U(https://www.linode.com/docs/api/stackscripts/).
    type: int
    version_added: 1.3.0
  stackscript_data:
    description:
      - An object containing arguments to any User Defined Fields present in
        the StackScript used when creating the instance.
        Only valid when a stackscript_id is provided.
        See U(https://www.linode.com/docs/api/stackscripts/).
    type: dict
    version_added: 1.3.0
'''

EXAMPLES = """
- name: Create a new Linode.
  community.general.linode_v4:
    label: new-linode
    type: g6-nanode-1
    region: eu-west
    image: linode/debian9
    root_pass: passw0rd
    authorized_keys:
      - "ssh-rsa ..."
    stackscript_id: 1337
    stackscript_data:
      variable: value
    state: present

- name: Delete that new Linode.
  community.general.linode_v4:
    label: new-linode
    state: absent
"""

RETURN = """
instance:
  description: The instance description in JSON serialized form.
  returned: Always.
  type: dict
  sample: {
    "root_pass": "foobar",  # if auto-generated
    "alerts": {
      "cpu": 90,
      "io": 10000,
      "network_in": 10,
      "network_out": 10,
      "transfer_quota": 80
    },
    "backups": {
      "enabled": false,
      "schedule": {
        "day": null,
        "window": null
      }
    },
    "created": "2018-09-26T08:12:33",
    "group": "Foobar Group",
    "hypervisor": "kvm",
    "id": 10480444,
    "image": "linode/centos7",
    "ipv4": [
      "130.132.285.233"
    ],
    "ipv6": "2a82:7e00::h03c:46ff:fe04:5cd2/64",
    "label": "lin-foo",
    "region": "eu-west",
    "specs": {
      "disk": 25600,
      "memory": 1024,
      "transfer": 1000,
      "vcpus": 1
    },
    "status": "running",
    "tags": [],
    "type": "g6-nanode-1",
    "updated": "2018-09-26T10:10:14",
    "watchdog_enabled": true
  }
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, env_fallback, missing_required_lib
from ansible_collections.community.general.plugins.module_utils.linode import get_user_agent

LINODE_IMP_ERR = None
try:
    from linode_api4 import Instance, LinodeClient
    HAS_LINODE_DEPENDENCY = True
except ImportError:
    LINODE_IMP_ERR = traceback.format_exc()
    HAS_LINODE_DEPENDENCY = False


def create_linode(module, client, **kwargs):
    """Creates a Linode instance and handles return format."""
    if kwargs['root_pass'] is None:
        kwargs.pop('root_pass')

    try:
        response = client.linode.instance_create(**kwargs)
    except Exception as exception:
        module.fail_json(msg='Unable to query the Linode API. Saw: %s' % exception)

    try:
        if isinstance(response, tuple):
            instance, root_pass = response
            instance_json = instance._raw_json
            instance_json.update({'root_pass': root_pass})
            return instance_json
        else:
            return response._raw_json
    except TypeError:
        module.fail_json(msg='Unable to parse Linode instance creation response. Please raise a bug against this'
                             ' module on https://github.com/ansible-collections/community.general/issues'
                         )


def maybe_instance_from_label(module, client):
    """Try to retrieve an instance based on a label."""
    try:
        label = module.params['label']
        result = client.linode.instances(Instance.label == label)
        return result[0]
    except IndexError:
        return None
    except Exception as exception:
        module.fail_json(msg='Unable to query the Linode API. Saw: %s' % exception)


def initialise_module():
    """Initialise the module parameter specification."""
    return AnsibleModule(
        argument_spec=dict(
            label=dict(type='str', required=True),
            state=dict(
                type='str',
                required=True,
                choices=['present', 'absent']
            ),
            access_token=dict(
                type='str',
                required=True,
                no_log=True,
                fallback=(env_fallback, ['LINODE_ACCESS_TOKEN']),
            ),
            authorized_keys=dict(type='list', elements='str', no_log=False),
            group=dict(type='str'),
            image=dict(type='str'),
            private_ip=dict(type='bool', default=False),
            region=dict(type='str'),
            root_pass=dict(type='str', no_log=True),
            tags=dict(type='list', elements='str'),
            type=dict(type='str'),
            stackscript_id=dict(type='int'),
            stackscript_data=dict(type='dict'),
        ),
        supports_check_mode=False,
        required_one_of=(
            ['state', 'label'],
        ),
        required_together=(
            ['region', 'image', 'type'],
        )
    )


def build_client(module):
    """Build a LinodeClient."""
    return LinodeClient(
        module.params['access_token'],
        user_agent=get_user_agent('linode_v4_module')
    )


def main():
    """Module entrypoint."""
    module = initialise_module()

    if not HAS_LINODE_DEPENDENCY:
        module.fail_json(msg=missing_required_lib('linode-api4'), exception=LINODE_IMP_ERR)

    client = build_client(module)
    instance = maybe_instance_from_label(module, client)

    if module.params['state'] == 'present' and instance is not None:
        module.exit_json(changed=False, instance=instance._raw_json)

    elif module.params['state'] == 'present' and instance is None:
        instance_json = create_linode(
            module, client,
            authorized_keys=module.params['authorized_keys'],
            group=module.params['group'],
            image=module.params['image'],
            label=module.params['label'],
            private_ip=module.params['private_ip'],
            region=module.params['region'],
            root_pass=module.params['root_pass'],
            tags=module.params['tags'],
            ltype=module.params['type'],
            stackscript=module.params['stackscript_id'],
            stackscript_data=module.params['stackscript_data'],
        )
        module.exit_json(changed=True, instance=instance_json)

    elif module.params['state'] == 'absent' and instance is not None:
        instance.delete()
        module.exit_json(changed=True, instance=instance._raw_json)

    elif module.params['state'] == 'absent' and instance is None:
        module.exit_json(changed=False, instance={})


if __name__ == "__main__":
    main()
