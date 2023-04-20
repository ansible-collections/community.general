#!/usr/bin/python

# Copyright (c) 2022, Gregory Furlong <gnfzdz@fzdz.io>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: btrfs_info
short_description: Query btrfs filesystem info
version_added: "6.6.0"
description: Query status of available btrfs filesystems, including uuid, label, subvolumes and mountpoints.

author:
    - Gregory Furlong (@gnfzdz)

extends_documentation_fragment:
      - community.general.attributes
      - community.general.attributes.info_module
'''

EXAMPLES = r'''

- name: Query information about mounted btrfs filesystems
  community.general.btrfs_info:
  register: my_btrfs_info

'''

RETURN = r'''

filesystems:
    description: Summaries of the current state for all btrfs filesystems found on the target host.
    type: list
    elements: dict
    returned: success
    contains:
        uuid:
            description: A unique identifier assigned to the filesystem.
            type: str
            sample: 96c9c605-1454-49b8-a63a-15e2584c208e
        label:
            description: An optional label assigned to the filesystem.
            type: str
            sample: Tank
        devices:
            description: A list of devices assigned to the filesystem.
            type: list
            sample:
                - /dev/sda1
                - /dev/sdb1
        default_subvolume:
            description: The id of the filesystem's default subvolume.
            type: int
            sample: 5
        subvolumes:
            description: A list of dicts containing metadata for all of the filesystem's subvolumes.
            type: list
            elements: dict
            contains:
                id:
                    description: An identifier assigned to the subvolume, unique within the containing filesystem.
                    type: int
                    sample: 256
                mountpoints:
                    description: Paths where the subvolume is mounted on the targeted host.
                    type: list
                    sample: ['/home']
                parent:
                    description: The identifier of this subvolume's parent.
                    type: int
                    sample: 5
                path:
                    description: The full path of the subvolume relative to the btrfs fileystem's root.
                    type: str
                    sample: /@home

'''


from ansible_collections.community.general.plugins.module_utils.btrfs import BtrfsFilesystemsProvider
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict()

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    provider = BtrfsFilesystemsProvider(module)
    filesystems = [x.get_summary() for x in provider.get_filesystems()]
    result = {
        "filesystems": filesystems,
    }
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
