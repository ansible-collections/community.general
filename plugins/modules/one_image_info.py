#!/usr/bin/python
# Copyright (c) 2018, Milan Ilic <milani@nordeus.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
module: one_image_info
short_description: Gather information on OpenNebula images
description:
  - Gather information on OpenNebula images.
requirements:
  - pyone
extends_documentation_fragment:
  - community.general.opennebula
  - community.general.attributes
  - community.general.attributes.info_module
options:
  ids:
    description:
      - A list of images IDs whose facts you want to gather.
      - Module can use integers too.
    aliases: ['id']
    type: list
    elements: str
  name:
    description:
      - A O(name) of the image whose facts is gathered.
      - If the O(name) begins with V(~) the O(name) is used as regex pattern, which restricts the list of images (whose facts
        is returned) whose names match specified regex.
      - Also, if the O(name) begins with V(~*) case-insensitive matching is performed.
      - See examples for more details.
    type: str
author:
  - "Milan Ilic (@ilicmilan)"
  - "Jan Meerkamp (@meerkampdvv)"
"""

EXAMPLES = r"""
- name: Gather facts about all images
  community.general.one_image_info:
  register: result

- name: Print all images facts
  ansible.builtin.debug:
    msg: result

- name: Gather facts about an image using ID
  community.general.one_image_info:
    ids: 123

- name: Gather facts about an image using list of ID
  community.general.one_image_info:
    ids:
      - 123
      - 456
      - 789
      - 0

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
"""

RETURN = r"""
images:
  description: A list of images info.
  type: complex
  returned: success
  contains:
    id:
      description: The image's ID.
      type: int
      sample: 153
    name:
      description: The image's name.
      type: str
      sample: app1
    group_id:
      description: The image's group ID.
      type: int
      sample: 1
    group_name:
      description: The image's group name.
      type: str
      sample: one-users
    owner_id:
      description: The image's owner ID.
      type: int
      sample: 143
    owner_name:
      description: The image's owner name.
      type: str
      sample: ansible-test
    state:
      description: The image's state.
      type: str
      sample: READY
    used:
      description: The image's usage status.
      type: bool
      sample: true
    running_vms:
      description: The image's count of running vms that use this image.
      type: int
      sample: 7
    permissions:
      description: The image's permissions.
      type: dict
      version_added: 9.5.0
      contains:
        owner_u:
          description: The image's owner USAGE permissions.
          type: str
          sample: 1
        owner_m:
          description: The image's owner MANAGE permissions.
          type: str
          sample: 0
        owner_a:
          description: The image's owner ADMIN permissions.
          type: str
          sample: 0
        group_u:
          description: The image's group USAGE permissions.
          type: str
          sample: 0
        group_m:
          description: The image's group MANAGE permissions.
          type: str
          sample: 0
        group_a:
          description: The image's group ADMIN permissions.
          type: str
          sample: 0
        other_u:
          description: The image's other users USAGE permissions.
          type: str
          sample: 0
        other_m:
          description: The image's other users MANAGE permissions.
          type: str
          sample: 0
        other_a:
          description: The image's other users ADMIN permissions.
          type: str
          sample: 0
      sample:
        owner_u: 1
        owner_m: 0
        owner_a: 0
        group_u: 0
        group_m: 0
        group_a: 0
        other_u: 0
        other_m: 0
        other_a: 0
    type:
      description: The image's type.
      type: int
      sample: 0
      version_added: 9.5.0
    disk_type:
      description: The image's format type.
      type: int
      sample: 0
      version_added: 9.5.0
    persistent:
      description: The image's persistence status (1 means true, 0 means false).
      type: int
      sample: 1
      version_added: 9.5.0
    source:
      description: The image's source.
      type: str
      sample: /var/lib/one//datastores/100/somerandomstringxd
      version_added: 9.5.0
    path:
      description: The image's filesystem path.
      type: str
      sample: /var/tmp/hello.qcow2
      version_added: 9.5.0
    fstype:
      description: The image's filesystem type.
      type: str
      sample: ext4
      version_added: 9.5.0
    size:
      description: The image's size in MegaBytes.
      type: int
      sample: 10000
      version_added: 9.5.0
    cloning_ops:
      description: The image's cloning operations per second.
      type: int
      sample: 0
      version_added: 9.5.0
    cloning_id:
      description: The image's cloning ID.
      type: int
      sample: -1
      version_added: 9.5.0
    target_snapshot:
      description: The image's target snapshot.
      type: int
      sample: 1
      version_added: 9.5.0
    datastore_id:
      description: The image's datastore ID.
      type: int
      sample: 100
      version_added: 9.5.0
    datastore:
      description: The image's datastore name.
      type: int
      sample: image_datastore
      version_added: 9.5.0
    vms:
      description: The image's list of VM ID's.
      type: list
      elements: int
      version_added: 9.5.0
      sample:
        - 1
        - 2
        - 3
    clones:
      description: The image's list of clones ID's.
      type: list
      elements: int
      version_added: 9.5.0
      sample:
        - 1
        - 2
        - 3
    app_clones:
      description: The image's list of app_clones ID's.
      type: list
      elements: int
      version_added: 9.5.0
      sample:
        - 1
        - 2
        - 3
    snapshots:
      description: The image's list of snapshots.
      type: list
      version_added: 9.5.0
      sample:
        - date: 123123
          parent: 1
          size: 10228
          allow_orphans: 1
          children: 0
          active: 1
          name: SampleName
"""


from ansible_collections.community.general.plugins.module_utils.opennebula import OpenNebulaModule


IMAGE_STATES = [
    "INIT",
    "READY",
    "USED",
    "DISABLED",
    "LOCKED",
    "ERROR",
    "CLONE",
    "DELETE",
    "USED_PERS",
    "LOCKED_USED",
    "LOCKED_USED_PERS",
]


class ImageInfoModule(OpenNebulaModule):
    def __init__(self):
        argument_spec = dict(
            ids=dict(type="list", aliases=["id"], elements="str"),
            name=dict(type="str"),
        )
        mutually_exclusive = [
            ["ids", "name"],
        ]

        OpenNebulaModule.__init__(self, argument_spec, supports_check_mode=True, mutually_exclusive=mutually_exclusive)

    def run(self, one, module, result):
        params = module.params
        ids = params.get("ids")
        name = params.get("name")

        if ids:
            images = self.get_images_by_ids(ids)
        elif name:
            images = self.get_images_by_name(name)
        else:
            images = self.get_all_images().IMAGE

        self.result = {"images": [self.get_image_info(image) for image in images]}

        self.exit()

    def get_all_images(self):
        pool = self.one.imagepool.info(-2, -1, -1, -1)
        # Filter -2 means fetch all images user can Use

        return pool

    def get_images_by_ids(self, ids):
        images = []
        pool = self.get_all_images()

        for image in pool.IMAGE:
            if str(image.ID) in ids:
                images.append(image)
                ids.remove(str(image.ID))
                if len(ids) == 0:
                    break

        if len(ids) > 0:
            self.module.fail_json(msg=f"There is no IMAGE(s) with id(s)={', '.join(str(image_id) for image_id in ids)}")

        return images

    def get_images_by_name(self, name_pattern):
        images = []
        pattern = None

        pool = self.get_all_images()

        if name_pattern.startswith("~"):
            import re

            if name_pattern[1] == "*":
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
            self.module.fail_json(msg=f"There is no IMAGE with name={name_pattern}")

        return images


def main():
    ImageInfoModule().run_module()


if __name__ == "__main__":
    main()
