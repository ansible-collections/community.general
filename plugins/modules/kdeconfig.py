#!/usr/bin/python

# Copyright (c) 2023, Salvatore Mesoraca <s.mesoraca16@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: kdeconfig
short_description: Manage KDE configuration files
version_added: "6.5.0"
description:
  - Add or change individual settings in KDE configuration files.
  - It uses B(kwriteconfig) under the hood.

options:
  path:
    description:
      - Path to the config file. If the file does not exist it will be created.
    type: path
    required: true
  kwriteconfig_path:
    description:
      - Path to the kwriteconfig executable. If not specified, Ansible will try
        to discover it.
    type: path
  values:
    description:
      - List of values to set.
    type: list
    elements: dict
    suboptions:
      group:
        description:
          - The option's group. One between this and I(groups) is required.
        type: str
      groups:
        description:
          - List of the option's groups. One between this and I(group) is required.
        type: list
        elements: str
      key:
        description:
          - The option's name.
        type: str
        required: true
      value:
        description:
          - The option's value. One between this and I(bool_value) is required.
        type: str
      bool_value:
        description:
          - Boolean value.
          - One between this and I(value) is required.
        type: bool
    required: true
  backup:
    description:
      - Create a backup file.
    type: bool
    default: false
extends_documentation_fragment:
  - files
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
requirements:
  - kwriteconfig
author:
  - Salvatore Mesoraca (@smeso)
'''

EXAMPLES = r'''
- name: Ensure "Homepage=https://www.ansible.com/" in group "Branding"
  community.general.kdeconfig:
    path: /etc/xdg/kickoffrc
    values:
      - group: Branding
        key: Homepage
        value: https://www.ansible.com/
    mode: '0644'

- name: Ensure "KEY=true" in groups "Group" and "Subgroup", and "KEY=VALUE" in Group2
  community.general.kdeconfig:
    path: /etc/xdg/someconfigrc
    values:
      - groups: [Group, Subgroup]
        key: KEY
        bool_value: true
      - group: Group2
        key: KEY
        value: VALUE
    backup: true
'''

RETURN = r''' # '''

import os
import shutil
import tempfile
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_text


class TemporaryDirectory(object):
    """Basic backport of tempfile.TemporaryDirectory"""

    def __init__(self, suffix="", prefix="tmp", dir=None):
        self.name = None
        self.name = tempfile.mkdtemp(suffix, prefix, dir)

    def __enter__(self):
        return self.name

    def rm(self):
        if self.name:
            shutil.rmtree(self.name, ignore_errors=True)
            self.name = None

    def __exit__(self, exc, value, tb):
        self.rm()

    def __del__(self):
        self.rm()


def run_kwriteconfig(module, cmd, path, groups, key, value):
    """Invoke kwriteconfig with arguments"""
    args = [cmd, '--file', path, '--key', key]
    for group in groups:
        args.extend(['--group', group])
    if isinstance(value, bool):
        args.extend(['--type', 'bool'])
        if value:
            args.append('true')
        else:
            args.append('false')
    else:
        args.append(value)
    module.run_command(args, check_rc=True)


def run_module(module, tmpdir, kwriteconfig):
    result = dict(changed=False, msg='OK', path=module.params['path'])
    b_path = to_bytes(module.params['path'])
    tmpfile = os.path.join(tmpdir, 'file')
    b_tmpfile = to_bytes(tmpfile)
    diff = dict(
        before='',
        after='',
        before_header=result['path'],
        after_header=result['path'],
    )
    try:
        with open(b_tmpfile, 'wb') as dst:
            try:
                with open(b_path, 'rb') as src:
                    b_data = src.read()
            except IOError:
                result['changed'] = True
            else:
                dst.write(b_data)
                try:
                    diff['before'] = to_text(b_data)
                except UnicodeError:
                    diff['before'] = repr(b_data)
    except IOError:
        module.fail_json(msg='Unable to create temporary file', traceback=traceback.format_exc())

    for row in module.params['values']:
        groups = row['groups']
        if groups is None:
            groups = [row['group']]
        key = row['key']
        value = row['bool_value']
        if value is None:
            value = row['value']
        run_kwriteconfig(module, kwriteconfig, tmpfile, groups, key, value)

    with open(b_tmpfile, 'rb') as tmpf:
        b_data = tmpf.read()
        try:
            diff['after'] = to_text(b_data)
        except UnicodeError:
            diff['after'] = repr(b_data)

    result['changed'] = result['changed'] or diff['after'] != diff['before']

    file_args = module.load_file_common_arguments(module.params)

    if module.check_mode:
        if not result['changed']:
            shutil.copystat(b_path, b_tmpfile)
            uid, gid = module.user_and_group(b_path)
            os.chown(b_tmpfile, uid, gid)
            if module._diff:
                diff = {}
            else:
                diff = None
            result['changed'] = module.set_fs_attributes_if_different(file_args, result['changed'], diff=diff)
        if module._diff:
            result['diff'] = diff
        module.exit_json(**result)

    if result['changed']:
        if module.params['backup'] and os.path.exists(b_path):
            result['backup_file'] = module.backup_local(result['path'])
        try:
            module.atomic_move(b_tmpfile, b_path)
        except IOError:
            module.ansible.fail_json(msg='Unable to move temporary file %s to %s, IOError' % (tmpfile, result['path']), traceback=traceback.format_exc())

    if result['changed']:
        module.set_fs_attributes_if_different(file_args, result['changed'])
    else:
        if module._diff:
            diff = {}
        else:
            diff = None
        result['changed'] = module.set_fs_attributes_if_different(file_args, result['changed'], diff=diff)
    if module._diff:
        result['diff'] = diff
    module.exit_json(**result)


def main():
    single_value_arg = dict(group=dict(type='str'),
                            groups=dict(type='list', elements='str'),
                            key=dict(type='str', required=True, no_log=False),
                            value=dict(type='str'),
                            bool_value=dict(type='bool'))
    required_alternatives = [('group', 'groups'), ('value', 'bool_value')]
    module_args = dict(
        values=dict(type='list',
                    elements='dict',
                    options=single_value_arg,
                    mutually_exclusive=required_alternatives,
                    required_one_of=required_alternatives,
                    required=True),
        path=dict(type='path', required=True),
        kwriteconfig_path=dict(type='path'),
        backup=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        add_file_common_args=True,
        supports_check_mode=True,
    )

    kwriteconfig = None
    if module.params['kwriteconfig_path'] is not None:
        kwriteconfig = module.get_bin_path(module.params['kwriteconfig_path'], required=True)
    else:
        for progname in ('kwriteconfig5', 'kwriteconfig', 'kwriteconfig4'):
            kwriteconfig = module.get_bin_path(progname)
            if kwriteconfig is not None:
                break
        if kwriteconfig is None:
            module.fail_json(msg='kwriteconfig is not installed')
    for v in module.params['values']:
        if not v['key']:
            module.fail_json(msg="'key' cannot be empty")
    with TemporaryDirectory(dir=module.tmpdir) as tmpdir:
        run_module(module, tmpdir, kwriteconfig)


if __name__ == '__main__':
    main()
