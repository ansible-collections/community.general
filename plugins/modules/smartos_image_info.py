#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Adam Števko <adam.stevko@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: smartos_image_info
short_description: Get SmartOS image details
description:
  - Retrieve information about all installed images on SmartOS.
author: Adam Števko (@xen0l)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  filters:
    description:
      - Criteria for selecting image. Can be any value from image manifest and V(published_date), V(published), V(source),
        V(clones), and V(size).
      - More information can be found at U(https://smartos.org/man/1m/imgadm) under C(imgadm list).
    type: str
"""

EXAMPLES = r"""
- name: Return information about all installed images
  community.general.smartos_image_info:
  register: result

- name: Return all private active Linux images
  community.general.smartos_image_info:
    filters: "os=linux state=active public=false"
  register: result

- name: Show, how many clones does every image have
  community.general.smartos_image_info:
  register: result

- name: Print information
  ansible.builtin.debug:
    msg: "{{ result.smartos_images[item]['name'] }}-{{ result.smartos_images[item]['version'] }} has {{ result.smartos_images[item]['clones'] }} VM(s)"
  with_items: "{{ result.smartos_images.keys() | list }}"

- name: Print information
  ansible.builtin.debug:
    msg: "{{ smartos_images[item]['name'] }}-{{ smartos_images[item]['version'] }} has {{ smartos_images[item]['clones'] }} VM(s)"
  with_items: "{{ smartos_images.keys() | list }}"
"""

RETURN = r"""
"""

import json
from ansible.module_utils.basic import AnsibleModule


class ImageFacts(object):

    def __init__(self, module):
        self.module = module

        self.filters = module.params['filters']

    def return_all_installed_images(self):
        cmd = [self.module.get_bin_path('imgadm'), 'list', '-j']

        if self.filters:
            cmd.append(self.filters)

        (rc, out, err) = self.module.run_command(cmd)

        if rc != 0:
            self.module.exit_json(
                msg='Failed to get all installed images', stderr=err)

        images = json.loads(out)

        result = {}
        for image in images:
            result[image['manifest']['uuid']] = image['manifest']
            # Merge additional attributes with the image manifest.
            for attrib in ['clones', 'source', 'zpool']:
                result[image['manifest']['uuid']][attrib] = image[attrib]

        return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            filters=dict(),
        ),
        supports_check_mode=True,
    )

    image_facts = ImageFacts(module)

    data = dict(smartos_images=image_facts.return_all_installed_images())

    module.exit_json(**data)


if __name__ == '__main__':
    main()
