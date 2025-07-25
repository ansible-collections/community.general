#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Milan Ilic <milani@nordeus.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: one_image
short_description: Manages OpenNebula images
description:
  - Manages OpenNebula images.
requirements:
  - pyone
extends_documentation_fragment:
  - community.general.opennebula
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  id:
    description:
      - A O(id) of the image you would like to manage.
    type: int
  name:
    description:
      - A O(name) of the image you would like to manage.
      - Required if O(create=true).
    type: str
  state:
    description:
      - V(present) - state that is used to manage the image.
      - V(absent) - delete the image.
      - V(cloned) - clone the image.
      - V(renamed) - rename the image to the O(new_name).
    choices: ["present", "absent", "cloned", "renamed"]
    default: present
    type: str
  enabled:
    description:
      - Whether the image should be enabled or disabled.
    type: bool
  new_name:
    description:
      - A name that is assigned to the existing or new image.
      - In the case of cloning, by default O(new_name) is set to the name of the origin image with the prefix 'Copy of'.
    type: str
  persistent:
    description:
      - Whether the image should be persistent or non-persistent.
    type: bool
    version_added: 9.5.0
  create:
    description:
      - Whether the image should be created if not present.
      - This is ignored if O(state=absent).
    type: bool
    version_added: 10.0.0
  template:
    description:
      - Use with O(create=true) to specify image template.
    type: str
    version_added: 10.0.0
  datastore_id:
    description:
      - Use with O(create=true) to specify datastore for image.
    type: int
    version_added: 10.0.0
  wait_timeout:
    description:
      - Seconds to wait until image is ready, deleted or cloned.
    type: int
    default: 60
    version_added: 10.0.0
author:
  - "Milan Ilic (@ilicmilan)"
"""

EXAMPLES = r"""
- name: Fetch the IMAGE by id
  community.general.one_image:
    id: 45
  register: result

- name: Print the IMAGE properties
  ansible.builtin.debug:
    var: result

- name: Rename existing IMAGE
  community.general.one_image:
    id: 34
    state: renamed
    new_name: bar-image

- name: Disable the IMAGE by id
  community.general.one_image:
    id: 37
    enabled: false

- name: Make the IMAGE persistent
  community.general.one_image:
    id: 37
    persistent: true

- name: Enable the IMAGE by name
  community.general.one_image:
    name: bar-image
    enabled: true

- name: Clone the IMAGE by name
  community.general.one_image:
    name: bar-image
    state: cloned
    new_name: bar-image-clone
  register: result

- name: Delete the IMAGE by id
  community.general.one_image:
    id: '{{ result.id }}'
    state: absent

- name: Make sure IMAGE is present
  community.general.one_image:
    name: myyy-image
    state: present
    create: true
    datastore_id: 100
    template: |
      PATH = "/var/tmp/image"
      TYPE = "OS"
      SIZE = 20512
      FORMAT = "qcow2"
      PERSISTENT = "Yes"
      DEV_PREFIX = "vd"

- name: Make sure IMAGE is present with a longer timeout
  community.general.one_image:
    name: big-image
    state: present
    create: true
    datastore_id: 100
    wait_timeout: 900
    template: |-
      PATH = "https://192.0.2.200/repo/tipa_image.raw"
      TYPE = "OS"
      SIZE = 82048
      FORMAT = "raw"
      PERSISTENT = "Yes"
      DEV_PREFIX = "vd"
"""

RETURN = r"""
id:
  description: Image ID.
  type: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: 153
name:
  description: Image name.
  type: str
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: app1
group_id:
  description: Image's group ID.
  type: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: 1
group_name:
  description: Image's group name.
  type: str
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: one-users
owner_id:
  description: Image's owner ID.
  type: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: 143
owner_name:
  description: Image's owner name.
  type: str
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: ansible-test
state:
  description: State of image instance.
  type: str
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: READY
used:
  description: Is image in use.
  type: bool
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: true
running_vms:
  description: Count of running vms that use this image.
  type: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample: 7
permissions:
  description: The image's permissions.
  type: dict
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
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
  type: str
  sample: 0
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
disk_type:
  description: The image's format type.
  type: str
  sample: 0
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
persistent:
  description: The image's persistence status (1 means true, 0 means false).
  type: int
  sample: 1
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
source:
  description: The image's source.
  type: str
  sample: /var/lib/one//datastores/100/somerandomstringxd
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
path:
  description: The image's filesystem path.
  type: str
  sample: /var/tmp/hello.qcow2
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
fstype:
  description: The image's filesystem type.
  type: str
  sample: ext4
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
size:
  description: The image's size in MegaBytes.
  type: int
  sample: 10000
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
cloning_ops:
  description: The image's cloning operations per second.
  type: int
  sample: 0
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
cloning_id:
  description: The image's cloning ID.
  type: int
  sample: -1
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
target_snapshot:
  description: The image's target snapshot.
  type: int
  sample: 1
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
datastore_id:
  description: The image's datastore ID.
  type: int
  sample: 100
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
datastore:
  description: The image's datastore name.
  type: int
  sample: image_datastore
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  version_added: 9.5.0
vms:
  description: The image's list of VM ID's.
  type: list
  elements: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample:
    - 1
    - 2
    - 3
  version_added: 9.5.0
clones:
  description: The image's list of clones ID's.
  type: list
  elements: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample:
    - 1
    - 2
    - 3
  version_added: 9.5.0
app_clones:
  description: The image's list of app_clones ID's.
  type: list
  elements: int
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
  sample:
    - 1
    - 2
    - 3
  version_added: 9.5.0
snapshots:
  description: The image's list of snapshots.
  type: list
  returned: when O(state=present), O(state=cloned), or O(state=renamed)
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


IMAGE_STATES = ['INIT', 'READY', 'USED', 'DISABLED', 'LOCKED', 'ERROR', 'CLONE', 'DELETE', 'USED_PERS', 'LOCKED_USED', 'LOCKED_USED_PERS']


class ImageModule(OpenNebulaModule):
    def __init__(self):
        argument_spec = dict(
            id=dict(type='int'),
            name=dict(type='str'),
            state=dict(type='str', choices=['present', 'absent', 'cloned', 'renamed'], default='present'),
            enabled=dict(type='bool'),
            new_name=dict(type='str'),
            persistent=dict(type='bool'),
            create=dict(type='bool'),
            template=dict(type='str'),
            datastore_id=dict(type='int'),
            wait_timeout=dict(type='int', default=60),
        )
        required_if = [
            ['state', 'renamed', ['id']],
            ['create', True, ['template', 'datastore_id', 'name']],
        ]
        mutually_exclusive = [
            ['id', 'name'],
        ]

        OpenNebulaModule.__init__(self,
                                  argument_spec,
                                  supports_check_mode=True,
                                  mutually_exclusive=mutually_exclusive,
                                  required_if=required_if)

    def run(self, one, module, result):
        params = module.params
        id = params.get('id')
        name = params.get('name')
        desired_state = params.get('state')
        enabled = params.get('enabled')
        new_name = params.get('new_name')
        persistent = params.get('persistent')
        create = params.get('create')
        template = params.get('template')
        datastore_id = params.get('datastore_id')
        wait_timeout = params.get('wait_timeout')

        self.result = {}

        image = self.get_image_instance(id, name)
        if not image and desired_state != 'absent':
            if create:
                self.result = self.create_image(name, template, datastore_id, wait_timeout)
            # Using 'if id:' doesn't work properly when id=0
            elif id is not None:
                module.fail_json(msg="There is no image with id=" + str(id))
            elif name is not None:
                module.fail_json(msg="There is no image with name=" + name)

        if desired_state == 'absent':
            self.result = self.delete_image(image, wait_timeout)
        else:
            if persistent is not None:
                self.result = self.change_persistence(image, persistent)
            if enabled is not None:
                self.result = self.enable_image(image, enabled)
            if desired_state == "cloned":
                self.result = self.clone_image(image, new_name, wait_timeout)
            elif desired_state == "renamed":
                self.result = self.rename_image(image, new_name)

        self.exit()

    def get_image(self, predicate):
        # Filter -2 means fetch all images user can Use
        pool = self.one.imagepool.info(-2, -1, -1, -1)

        for image in pool.IMAGE:
            if predicate(image):
                return image

        return None

    def get_image_by_name(self, image_name):
        return self.get_image(lambda image: (image.NAME == image_name))

    def get_image_by_id(self, image_id):
        return self.get_image(lambda image: (image.ID == image_id))

    def get_image_instance(self, requested_id, requested_name):
        # Using 'if requested_id:' doesn't work properly when requested_id=0
        if requested_id is not None:
            return self.get_image_by_id(requested_id)
        else:
            return self.get_image_by_name(requested_name)

    def create_image(self, image_name, template, datastore_id, wait_timeout):
        if not self.module.check_mode:
            image_id = self.one.image.allocate("NAME = \"" + image_name + "\"\n" + template, datastore_id)
            self.wait_for_ready(image_id, wait_timeout)
            image = self.get_image_by_id(image_id)
            result = self.get_image_info(image)

        result['changed'] = True
        return result

    def wait_for_ready(self, image_id, wait_timeout=60):
        import time
        start_time = time.time()

        while (time.time() - start_time) < wait_timeout:
            image = self.one.image.info(image_id)
            state = image.STATE

            if state in [IMAGE_STATES.index('ERROR')]:
                self.module.fail_json(msg="Got an ERROR state: " + image.TEMPLATE['ERROR'])

            if state in [IMAGE_STATES.index('READY')]:
                return True

            time.sleep(1)
        self.module.fail_json(msg="Wait timeout has expired!")

    def wait_for_delete(self, image_id, wait_timeout=60):
        import time
        start_time = time.time()

        while (time.time() - start_time) < wait_timeout:
            # It might be already deleted by the time this function is called
            try:
                image = self.one.image.info(image_id)
            except Exception:
                check_image = self.get_image_instance(image_id)
                if not check_image:
                    return True

            state = image.STATE

            if state in [IMAGE_STATES.index('DELETE')]:
                return True

            time.sleep(1)

        self.module.fail_json(msg="Wait timeout has expired!")

    def enable_image(self, image, enable):
        image = self.one.image.info(image.ID)
        changed = False

        state = image.STATE

        if state not in [IMAGE_STATES.index('READY'), IMAGE_STATES.index('DISABLED'), IMAGE_STATES.index('ERROR')]:
            if enable:
                self.module.fail_json(msg="Cannot enable " + IMAGE_STATES[state] + " image!")
            else:
                self.module.fail_json(msg="Cannot disable " + IMAGE_STATES[state] + " image!")

        if ((enable and state != IMAGE_STATES.index('READY')) or
                (not enable and state != IMAGE_STATES.index('DISABLED'))):
            changed = True

        if changed and not self.module.check_mode:
            self.one.image.enable(image.ID, enable)

        result = self.get_image_info(image)
        result['changed'] = changed

        return result

    def change_persistence(self, image, enable):
        image = self.one.image.info(image.ID)
        changed = False

        state = image.STATE

        if state not in [IMAGE_STATES.index('READY'), IMAGE_STATES.index('DISABLED'), IMAGE_STATES.index('ERROR')]:
            if enable:
                self.module.fail_json(msg="Cannot enable persistence for " + IMAGE_STATES[state] + " image!")
            else:
                self.module.fail_json(msg="Cannot disable persistence for " + IMAGE_STATES[state] + " image!")

        if ((enable and state != IMAGE_STATES.index('READY')) or
                (not enable and state != IMAGE_STATES.index('DISABLED'))):
            changed = True

        if changed and not self.module.check_mode:
            self.one.image.persistent(image.ID, enable)

        result = self.get_image_info(image)
        result['changed'] = changed

        return result

    def clone_image(self, image, new_name, wait_timeout):
        if new_name is None:
            new_name = "Copy of " + image.NAME

        tmp_image = self.get_image_by_name(new_name)
        if tmp_image:
            result = self.get_image_info(image)
            result['changed'] = False
            return result

        if image.STATE == IMAGE_STATES.index('DISABLED'):
            self.module.fail_json(msg="Cannot clone DISABLED image")

        if not self.module.check_mode:
            new_id = self.one.image.clone(image.ID, new_name)
            self.wait_for_ready(new_id, wait_timeout)
            image = self.one.image.info(new_id)

        result = self.get_image_info(image)
        result['changed'] = True

        return result

    def rename_image(self, image, new_name):
        if new_name is None:
            self.module.fail_json(msg="'new_name' option has to be specified when the state is 'renamed'")

        if new_name == image.NAME:
            result = self.get_image_info(image)
            result['changed'] = False
            return result

        tmp_image = self.get_image_by_name(new_name)
        if tmp_image:
            self.module.fail_json(msg="Name '" + new_name + "' is already taken by IMAGE with id=" + str(tmp_image.ID))

        if not self.module.check_mode:
            self.one.image.rename(image.ID, new_name)

        result = self.get_image_info(image)
        result['changed'] = True
        return result

    def delete_image(self, image, wait_timeout):
        if not image:
            return {'changed': False}

        if image.RUNNING_VMS > 0:
            self.module.fail_json(msg="Cannot delete image. There are " + str(image.RUNNING_VMS) + " VMs using it.")

        if not self.module.check_mode:
            self.one.image.delete(image.ID)
            self.wait_for_delete(image.ID, wait_timeout)

        return {'changed': True}


def main():
    ImageModule().run_module()


if __name__ == '__main__':
    main()
