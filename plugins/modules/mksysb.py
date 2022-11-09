#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Alexei Znamensky (@russoz) <russoz@gmail.com>
# Copyright (c) 2017, Kairo Araujo <kairo@kairo.eti.br>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
author: Kairo Araujo (@kairoaraujo)
module: mksysb
short_description: Generates AIX mksysb rootvg backups
description:
  - This module manages a basic AIX mksysb (image) of rootvg.
options:
  backup_crypt_files:
    description:
      - Backup encrypted files.
    type: bool
    default: true
  backup_dmapi_fs:
    description:
      - Back up DMAPI filesystem files.
    type: bool
    default: true
  create_map_files:
    description:
      - Creates a new MAP files.
    type: bool
    default: false
  exclude_files:
    description:
      - Excludes files using C(/etc/rootvg.exclude).
    type: bool
    default: false
  exclude_wpar_files:
    description:
      - Excludes WPAR files.
    type: bool
    default: false
  extended_attrs:
    description:
      - Backup extended attributes.
    type: bool
    default: true
  name:
    type: str
    description:
      - Backup name
    required: true
  new_image_data:
    description:
      - Creates a new file data.
    type: bool
    default: true
  software_packing:
    description:
      - Exclude files from packing option listed in
        C(/etc/exclude_packing.rootvg).
    type: bool
    default: false
  storage_path:
    type: str
    description:
      - Storage path where the mksysb will stored.
    required: true
  use_snapshot:
    description:
      - Creates backup using snapshots.
    type: bool
    default: false
'''

EXAMPLES = '''
- name: Running a backup image mksysb
  community.general.mksysb:
    name: myserver
    storage_path: /repository/images
    exclude_files: true
    exclude_wpar_files: true
'''

RETURN = '''
changed:
  description: Return changed for mksysb actions as true or false.
  returned: always
  type: bool
msg:
  description: Return message regarding the action.
  returned: always
  type: str
'''

import os

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ArgFormat
)


class MkSysB(ModuleHelper):
    module = dict(
        argument_spec=dict(
            backup_crypt_files=dict(type='bool', default=True),
            backup_dmapi_fs=dict(type='bool', default=True),
            create_map_files=dict(type='bool', default=False),
            exclude_files=dict(type='bool', default=False),
            exclude_wpar_files=dict(type='bool', default=False),
            extended_attrs=dict(type='bool', default=True),
            name=dict(type='str', required=True),
            new_image_data=dict(type='bool', default=True),
            software_packing=dict(type='bool', default=False),
            storage_path=dict(type='str', required=True),
            use_snapshot=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )
    command_args_formats = dict(
        create_map_files=cmd_runner_fmt.as_bool("-m"),
        use_snapshot=cmd_runner_fmt.as_bool("-T"),
        exclude_files=cmd_runner_fmt.as_bool("-e"),
        exclude_wpar_files=cmd_runner_fmt.as_bool("-G"),
        new_image_data=cmd_runner_fmt.as_bool("-i"),
        software_packing=cmd_runner_fmt.as_bool_not("-p"),
        extended_attrs=cmd_runner_fmt.as_bool("-a"),
        backup_crypt_files=cmd_runner_fmt.as_bool_not("-Z"),
        backup_dmapi_fs=cmd_runner_fmt.as_bool("-A"),
        combined_path=cmd_runner_fmt.as_func(cmd_runner_fmt.unpack_args(lambda p, n: ["%s/%s" % (p, n)])),
    )

    def __init_module__(self):
        if not os.path.isdir(self.vars.storage_path):
            self.do_raise("Storage path %s is not valid." % self.vars.storage_path)

    def __run__(self):
        def process(rc, out, err):
            if rc != 0:
                self.do_raise("mksysb failed.")
            self.vars.msg = out

        runner = CmdRunner(
            self.module,
            ['mksysb', '-X'],
            self.command_args_formats,
        )
        with runner(['create_map_files', 'use_snapshot', 'exclude_files', 'exclude_wpar_files', 'software_packing',
                     'extended_attrs', 'backup_crypt_files', 'backup_dmapi_fs', 'new_image_data', 'combined_path'],
                    output_process=process, check_mode_skip=True) as ctx:
            ctx.run(combined_path=[self.vars.storage_path, self.vars.name])

        self.changed = True


def main():
    MkSysB.execute()


if __name__ == '__main__':
    main()
