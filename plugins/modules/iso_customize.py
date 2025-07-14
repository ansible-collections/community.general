#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Ansible Project
# Copyright (c) 2022, VMware, Inc. All Rights Reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: iso_customize
short_description: Add/remove/change files in ISO file
description:
  - This module is used to add/remove/change files in ISO file.
  - The file inside ISO is overwritten if it exists by option O(add_files).
author:
  - Yuhua Zou (@ZouYuhua) <zouy@vmware.com>
requirements:
  - "pycdlib"
version_added: '5.8.0'

extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  src_iso:
    description:
      - This is the path of source ISO file.
    type: path
    required: true
  dest_iso:
    description:
      - The path of the customized ISO file.
    type: path
    required: true
  delete_files:
    description:
      - Absolute paths for files inside the ISO file that should be removed.
    type: list
    required: false
    elements: str
    default: []
  add_files:
    description:
      - Allows to add and replace files in the ISO file.
      - It creates intermediate folders inside the ISO file when they do not exist.
    type: list
    required: false
    elements: dict
    default: []
    suboptions:
      src_file:
        description:
          - The path with file name on the machine the module is executed on.
        type: path
        required: true
      dest_file:
        description:
          - The absolute path of the file inside the ISO file.
        type: str
        required: true
notes:
  - The C(pycdlib) library states it supports Python 2.7 and 3.4+.
  - The function C(add_file) in pycdlib is designed to overwrite the existing file in ISO with type ISO9660 / Rock Ridge 1.12
    / Joliet / UDF. But it does not overwrite the existing file in ISO with Rock Ridge 1.09 / 1.10. So we take workaround
    "delete the existing file and then add file for ISO with Rock Ridge".
"""

EXAMPLES = r"""
- name: "Customize ISO file"
  community.general.iso_customize:
    src_iso: "/path/to/ubuntu-22.04-desktop-amd64.iso"
    dest_iso: "/path/to/ubuntu-22.04-desktop-amd64-customized.iso"
    delete_files:
      - "/boot.catalog"
    add_files:
      - src_file: "/path/to/grub.cfg"
        dest_file: "/boot/grub/grub.cfg"
      - src_file: "/path/to/ubuntu.seed"
        dest_file: "/preseed/ubuntu.seed"
  register: customize_iso_result
"""

RETURN = r"""
src_iso:
  description: Path of source ISO file.
  returned: on success
  type: str
  sample: "/path/to/file.iso"
dest_iso:
  description: Path of the customized ISO file.
  returned: on success
  type: str
  sample: "/path/to/customized.iso"
"""

import os

from ansible_collections.community.general.plugins.module_utils import deps
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

with deps.declare("pycdlib"):
    import pycdlib


# The upper dir exist, we only add subdirectoy
def iso_add_dir(module, opened_iso, iso_type, dir_path):
    parent_dir, check_dirname = dir_path.rsplit("/", 1)
    if not parent_dir.strip():
        parent_dir = "/"
    check_dirname = check_dirname.strip()

    for dirname, dirlist, dummy_filelist in opened_iso.walk(iso_path=parent_dir.upper()):
        if dirname == parent_dir.upper():
            if check_dirname.upper() in dirlist:
                return

            if parent_dir == "/":
                current_dirpath = "/%s" % check_dirname
            else:
                current_dirpath = "%s/%s" % (parent_dir, check_dirname)

            current_dirpath_upper = current_dirpath.upper()
            try:
                if iso_type == "iso9660":
                    opened_iso.add_directory(current_dirpath_upper)
                elif iso_type == "rr":
                    opened_iso.add_directory(current_dirpath_upper, rr_name=check_dirname)
                elif iso_type == "joliet":
                    opened_iso.add_directory(current_dirpath_upper, joliet_path=current_dirpath)
                elif iso_type == "udf":
                    opened_iso.add_directory(current_dirpath_upper, udf_path=current_dirpath)
            except Exception as err:
                msg = "Failed to create dir %s with error: %s" % (current_dirpath, to_native(err))
                module.fail_json(msg=msg)


def iso_add_dirs(module, opened_iso, iso_type, dir_path):
    dirnames = dir_path.strip().split("/")

    current_dirpath = "/"
    for item in dirnames:
        if not item.strip():
            continue
        if current_dirpath == "/":
            current_dirpath = "/%s" % item
        else:
            current_dirpath = "%s/%s" % (current_dirpath, item)

        iso_add_dir(module, opened_iso, iso_type, current_dirpath)


def iso_check_file_exists(opened_iso, dest_file):
    file_dir = os.path.dirname(dest_file).strip()
    file_name = os.path.basename(dest_file)
    dirnames = file_dir.strip().split("/")

    parent_dir = "/"
    for item in dirnames:
        if not item.strip():
            continue

        for dirname, dirlist, dummy_filelist in opened_iso.walk(iso_path=parent_dir.upper()):
            if dirname != parent_dir.upper():
                break

            if item.upper() not in dirlist:
                return False

        if parent_dir == "/":
            parent_dir = "/%s" % item
        else:
            parent_dir = "%s/%s" % (parent_dir, item)

    if '.' not in file_name:
        file_in_iso_path = file_name.upper() + '.;1'
    else:
        file_in_iso_path = file_name.upper() + ';1'

    for dirname, dummy_dirlist, filelist in opened_iso.walk(iso_path=parent_dir.upper()):
        if dirname != parent_dir.upper():
            return False

        return file_name.upper() in filelist or file_in_iso_path in filelist


def iso_add_file(module, opened_iso, iso_type, src_file, dest_file):
    dest_file = dest_file.strip()
    if dest_file[0] != "/":
        dest_file = "/%s" % dest_file

    file_local = src_file.strip()

    file_dir = os.path.dirname(dest_file).strip()
    file_name = os.path.basename(dest_file)
    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    if file_dir and file_dir != "/":
        iso_add_dirs(module, opened_iso, iso_type, file_dir)

    try:
        if iso_type == "iso9660":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path)
        elif iso_type == "rr":
            # For ISO with Rock Ridge 1.09 / 1.10, it won't overwrite the existing file
            # So we take workaround here: delete the existing file and then add file
            if iso_check_file_exists(opened_iso, dest_file):
                opened_iso.rm_file(iso_path=file_in_iso_path)
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, rr_name=file_name)
        elif iso_type == "joliet":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, joliet_path=dest_file)
        elif iso_type == "udf":
            # For ISO with UDF, it won't always succeed to overwrite the existing file
            # So we take workaround here: delete the existing file and then add file
            if iso_check_file_exists(opened_iso, dest_file):
                opened_iso.rm_file(udf_path=dest_file)
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, udf_path=dest_file)
    except Exception as err:
        msg = "Failed to add local file %s to ISO with error: %s" % (file_local, to_native(err))
        module.fail_json(msg=msg)


def iso_delete_file(module, opened_iso, iso_type, dest_file):
    dest_file = dest_file.strip()
    if dest_file[0] != "/":
        dest_file = "/%s" % dest_file
    file_name = os.path.basename(dest_file)

    if not iso_check_file_exists(opened_iso, dest_file):
        module.fail_json(msg="The file %s does not exist." % dest_file)

    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    try:
        if iso_type == "iso9660":
            opened_iso.rm_file(iso_path=file_in_iso_path)
        elif iso_type == "rr":
            opened_iso.rm_file(iso_path=file_in_iso_path)
        elif iso_type == "joliet":
            opened_iso.rm_file(joliet_path=dest_file)
        elif iso_type == "udf":
            opened_iso.rm_file(udf_path=dest_file)
    except Exception as err:
        msg = "Failed to delete iso file %s with error: %s" % (dest_file, to_native(err))
        module.fail_json(msg=msg)


def iso_rebuild(module, src_iso, dest_iso, delete_files_list, add_files_list):
    iso = None
    iso_type = "iso9660"

    try:
        iso = pycdlib.PyCdlib(always_consistent=True)
        iso.open(src_iso)
        if iso.has_rock_ridge():
            iso_type = "rr"
        elif iso.has_joliet():
            iso_type = "joliet"
        elif iso.has_udf():
            iso_type = "udf"

        for item in delete_files_list:
            iso_delete_file(module, iso, iso_type, item)

        for item in add_files_list:
            iso_add_file(module, iso, iso_type, item['src_file'], item['dest_file'])

        iso.write(dest_iso)
    except Exception as err:
        msg = "Failed to rebuild ISO %s with error: %s" % (src_iso, to_native(err))
        module.fail_json(msg=msg)
    finally:
        if iso:
            iso.close()


def main():
    argument_spec = dict(
        src_iso=dict(type='path', required=True),
        dest_iso=dict(type='path', required=True),
        delete_files=dict(type='list', elements='str', default=[]),
        add_files=dict(
            type='list', elements='dict', default=[],
            options=dict(
                src_file=dict(type='path', required=True),
                dest_file=dict(type='str', required=True),
            ),
        ),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=[('delete_files', 'add_files'), ],
        supports_check_mode=True,
    )
    deps.validate(module)

    src_iso = module.params['src_iso']
    if not os.path.exists(src_iso):
        module.fail_json(msg="ISO file %s does not exist." % src_iso)

    dest_iso = module.params['dest_iso']
    dest_iso_dir = os.path.dirname(dest_iso)
    if dest_iso_dir and not os.path.exists(dest_iso_dir):
        module.fail_json(msg="The dest directory %s does not exist" % dest_iso_dir)

    delete_files_list = [s.strip() for s in module.params['delete_files']]
    add_files_list = module.params['add_files']
    if add_files_list:
        for item in add_files_list:
            if not os.path.exists(item['src_file']):
                module.fail_json(msg="The file %s does not exist." % item['src_file'])

    result = dict(
        src_iso=src_iso,
        customized_iso=dest_iso,
        delete_files=delete_files_list,
        add_files=add_files_list,
        changed=True,
    )

    if not module.check_mode:
        iso_rebuild(module, src_iso, dest_iso, delete_files_list, add_files_list)

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
