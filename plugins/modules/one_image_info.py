#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Milan Ilic <milani@nordeus.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: one_image_info
short_description: Gather information on OpenNebula images
description:
  - Gather information on OpenNebula images.
  - This module was called C(one_image_facts) before Ansible 2.9. The usage did not change.
requirements:
  - pyone
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  api_url:
    description:
      - URL of the OpenNebula RPC server.
      - It is recommended to use HTTPS so that the username/password are not
      - transferred over the network unencrypted.
      - If not set then the value of the C(ONE_URL) environment variable is used.
    type: str
  api_username:
    description:
      - Name of the user to login into the OpenNebula RPC server. If not set
      - then the value of the C(ONE_USERNAME) environment variable is used.
    type: str
  api_password:
    description:
      - Password of the user to login into OpenNebula RPC server. If not set
      - then the value of the C(ONE_PASSWORD) environment variable is used.
    type: str
  ids:
    description:
      - A list of images ids whose facts you want to gather.
    aliases: ['id']
    type: list
    elements: str
  name:
    description:
      - A C(name) of the image whose facts will be gathered.
      - If the C(name) begins with '~' the C(name) will be used as regex pattern
      - which restricts the list of images (whose facts will be returned) whose names match specified regex.
      - Also, if the C(name) begins with '~*' case-insensitive matching will be performed.
      - See examples for more details.
    type: str
author:
    - "Milan Ilic (@ilicmilan)"
    - "Jan Meerkamp (@meerkampdvv)"
'''

EXAMPLES = '''
- name: Gather facts about all images
  community.general.one_image_info:
  register: result

- name: Print all images facts
  ansible.builtin.debug:
    msg: result

- name: Gather facts about an image using ID
  community.general.one_image_info:
    ids:
      - 123

- name: Gather facts about an image using the name
  community.general.one_image_info:
    name: 'foo-image'
  register: foo_image

- name: Gather facts about all IMAGEs whose name matches regex 'app-image-.*'
  community.general.one_image_info:
    name: '~app-image-.*'
  register: app_images

- name: Gather facts about all IMAGEs whose name matches regex 'foo-image-.*' ignoring cases
  community.general.one_image_info:
    name: '~*foo-image-.*'
  register: foo_images
'''

RETURN = '''
images:
    description: A list of images info
    type: complex
    returned: success
    contains:
        id:
            description: image id
            type: int
            sample: 153
        name:
            description: image name
            type: str
            sample: app1
        group_id:
            description: image's group id
            type: int
            sample: 1
        group_name:
            description: image's group name
            type: str
            sample: one-users
        owner_id:
            description: image's owner id
            type: int
            sample: 143
        owner_name:
            description: image's owner name
            type: str
            sample: ansible-test
        state:
            description: state of image instance
            type: str
            sample: READY
        used:
            description: is image in use
            type: bool
            sample: true
        running_vms:
            description: count of running vms that use this image
            type: int
            sample: 7
'''

try:
    import pyone
    HAS_PYONE = True
except ImportError:
    HAS_PYONE = False

from ansible.module_utils.basic import AnsibleModule
import os


def get_all_images(client):
    pool = client.imagepool.info(-2, -1, -1, -1)
    # Filter -2 means fetch all images user can Use

    return pool


IMAGE_STATES = ['INIT', 'READY', 'USED', 'DISABLED', 'LOCKED', 'ERROR', 'CLONE', 'DELETE', 'USED_PERS', 'LOCKED_USED', 'LOCKED_USED_PERS']


def get_image_info(image):
    info = {
        'id': image.ID,
        'name': image.NAME,
        'state': IMAGE_STATES[image.STATE],
        'running_vms': image.RUNNING_VMS,
        'used': bool(image.RUNNING_VMS),
        'user_name': image.UNAME,
        'user_id': image.UID,
        'group_name': image.GNAME,
        'group_id': image.GID,
    }
    return info


def get_images_by_ids(module, client, ids):
    images = []
    pool = get_all_images(client)

    for image in pool.IMAGE:
        if str(image.ID) in ids:
            images.append(image)
            ids.remove(str(image.ID))
            if len(ids) == 0:
                break

    if len(ids) > 0:
        module.fail_json(msg='There is no IMAGE(s) with id(s)=' + ', '.join('{id}'.format(id=str(image_id)) for image_id in ids))

    return images


def get_images_by_name(module, client, name_pattern):

    images = []
    pattern = None

    pool = get_all_images(client)

    if name_pattern.startswith('~'):
        import re
        if name_pattern[1] == '*':
            pattern = re.compile(name_pattern[2:], re.IGNORECASE)
        else:
            pattern = re.compile(name_pattern[1:])

    for image in pool.IMAGE:
        if pattern is not None:
            if pattern.match(image.NAME):
                images.append(image)
        elif name_pattern == image.NAME:
            images.append(image)
            break

    # if the specific name is indicated
    if pattern is None and len(images) == 0:
        module.fail_json(msg="There is no IMAGE with name=" + name_pattern)

    return images


def get_connection_info(module):

    url = module.params.get('api_url')
    username = module.params.get('api_username')
    password = module.params.get('api_password')

    if not url:
        url = os.environ.get('ONE_URL')

    if not username:
        username = os.environ.get('ONE_USERNAME')

    if not password:
        password = os.environ.get('ONE_PASSWORD')

    if not (url and username and password):
        module.fail_json(msg="One or more connection parameters (api_url, api_username, api_password) were not specified")
    from collections import namedtuple

    auth_params = namedtuple('auth', ('url', 'username', 'password'))

    return auth_params(url=url, username=username, password=password)


def main():
    fields = {
        "api_url": {"required": False, "type": "str"},
        "api_username": {"required": False, "type": "str"},
        "api_password": {"required": False, "type": "str", "no_log": True},
        "ids": {"required": False, "aliases": ['id'], "type": "list", "elements": "str"},
        "name": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields,
                           mutually_exclusive=[['ids', 'name']],
                           supports_check_mode=True)

    if not HAS_PYONE:
        module.fail_json(msg='This module requires pyone to work!')

    auth = get_connection_info(module)
    params = module.params
    ids = params.get('ids')
    name = params.get('name')
    client = pyone.OneServer(auth.url, session=auth.username + ':' + auth.password)

    if ids:
        images = get_images_by_ids(module, client, ids)
    elif name:
        images = get_images_by_name(module, client, name)
    else:
        images = get_all_images(client).IMAGE

    result = {
        'images': [get_image_info(image) for image in images],
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
