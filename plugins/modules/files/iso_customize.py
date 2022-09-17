#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Ansible Project
# Copyright (c) 2022, VMware, Inc. All Rights Reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iso_customize
short_description: Add/remove/change files in ISO file
description:
  - This module is used to add/remove/change files in ISO file.
  - The file inside ISO will be overwritten if it exists by option I(add_files).
author:
  - Yuhua Zou (@ZouYuhua) <zouy@vmware.com>
requirements:
  - "pycdlib"
  - "python >= 2.7"
version_added: '5.7.0'

options:
  src_iso:
    description:
    - This is the path of source ISO file.
    - Will fail if specified ISO file does not exist on local machine.
    type: path
    required: true
  dest_iso:
    description:
    - The path with file name of the customized ISO file on local machine.
    type: path
    required: true
  delete_files:
    description:
    - Absolute paths for files inside the ISO file that should be removed.
    type: list
    required: false
    elements: str
  add_files:
    description:
    - Allows to add and replace files in the ISO file.
    - Will create intermediate folders inside the ISO file when they do not exist.
    type: list
    required: false
    elements: dict
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
- The C(pycdlib) library states it supports Python 2.7 and 3.4 only.
- >
  The function "add_file" in pycdlib will overwrite the existing file in ISO with type ISO9660 / Rock Ridge 1.12 / Joliet / UDF.
  But it won't overwrite the existing file in ISO with Rock Ridge 1.09 / 1.10.
  So we take workaround "delete the existing file and then add file for ISO with Rock Ridge".
'''

EXAMPLES = r'''
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
'''

RETURN = r'''
src_iso:
  description: Path of source ISO file.
  returned: on success
  type: str
  sample: "/path/to/file.iso"
dest_iso:
  description: path of the customized iso file.
  returned: on success
  type: str
  sample: "/path/to/customized.iso"
'''

import os
import traceback

PYCDLIB_IMP_ERR = None
try:
    import pycdlib
    HAS_PYCDLIB = True
except ImportError:
    PYCDLIB_IMP_ERR = traceback.format_exc()
    HAS_PYCDLIB = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


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


def iso_rr_check_file_exist(opened_iso, dest_file):
    try:
        record = opened_iso.get_record(rr_path=dest_file)
        # The record present file or directory
        if record and record.is_file():
            return True
    except Exception:
        # If we get exception, that means the file does not exists
        pass

    return False


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
            if iso_rr_check_file_exist(opened_iso, dest_file):
                opened_iso.rm_hard_link(iso_path=file_in_iso_path)
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, rr_name=file_name)
        elif iso_type == "joliet":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, joliet_path=dest_file)
        elif iso_type == "udf":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, udf_path=dest_file)
    except Exception as err:
        msg = "Failed to add local file %s to ISO with error: %s" % (file_local, to_native(err))
        module.fail_json(msg=msg)


def iso_delete_file(module, opened_iso, iso_type, dest_file):
    dest_file = dest_file.strip()
    if dest_file[0] != "/":
        dest_file = "/%s" % dest_file
    file_name = os.path.basename(dest_file)

    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    try:
        if iso_type == "iso9660":
            record = opened_iso.get_record(iso_path=file_in_iso_path)
        elif iso_type == "rr":
            record = opened_iso.get_record(rr_path=dest_file)
        elif iso_type == "joliet":
            record = opened_iso.get_record(joliet_path=dest_file)
        elif iso_type == "udf":
            record = opened_iso.get_record(udf_path=dest_file)

        if record and not record.is_file():
            module.fail_json(msg="The %s is not a file but directory." % dest_file)
    except Exception as err:
        msg = "Failed to get record of file %s in ISO with filesystem %s. error: %s" % (
            dest_file, iso_type, to_native(err))
        module.fail_json(msg=msg)

    try:
        if iso_type == "iso9660":
            opened_iso.rm_hard_link(iso_path=file_in_iso_path)
        elif iso_type == "rr":
            opened_iso.rm_hard_link(iso_path=file_in_iso_path)
        elif iso_type == "joliet":
            opened_iso.rm_hard_link(joliet_path=dest_file)
        elif iso_type == "udf":
            # function "rm_hard_link" won't work in some OS (such as Ubuntu with python 3.10.4)
            # take function "rm_file" instead
            opened_iso.rm_file(udf_path=dest_file)
    except Exception as err:
        msg = "Failed to delete iso file %s with error: %s" % (dest_file, to_native(err))
        module.fail_json(msg=msg)


def iso_rebuild(module, src_iso, dest_iso, delete_files_list, add_files_list):
    iso = None
    iso_type = "iso9660"

    try:
        iso = pycdlib.PyCdlib()
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
    if not HAS_PYCDLIB:
        module.fail_json(
            missing_required_lib('pycdlib'), exception=PYCDLIB_IMP_ERR)

    src_iso = module.params['src_iso']
    if not os.path.exists(src_iso):
        module.fail_json(msg="The %s does not exist." % src_iso)

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
        changed=False,
        src_iso=src_iso,
        customized_iso=dest_iso,
        delete_files=delete_files_list,
        add_files=add_files_list,
    )

    if not module.check_mode:
        iso_rebuild(module, src_iso, dest_iso, delete_files_list, add_files_list)

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
