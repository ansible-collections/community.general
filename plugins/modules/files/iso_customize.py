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
short_description: Customize the ISO file by add/delete/modify files
description:
  - This module is used to customize the ISO file by add/delete files.
author:
  - Yuhua Zou (@ZouYuhua) <zouy@vmware.com>
requirements:
  - "pycdlib"
  - "python >= 2.7"
version_added: '5.6.0'

options:
  src_iso:
    description:
    - This is the path of source ISO file.
    - Will fail if specified ISO file does not exist on local machine.
    - 'Note: With all ISO9660 levels from 1 to 3, all file names are restricted to uppercase letters, numbers and
      underscores (_). File names are limited to 31 characters, directory nesting is limited to 8 levels, and path
      names are limited to 255 characters.'
    type: str
    required: true
  dest_iso:
    description:
    - The path with file name of the customized ISO file on local machine.
    type: str
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
      dest_file:
        description:
        - The absolute path of the file inside the ISO file.
        type: str
'''

EXAMPLES = r'''
- name: "Customize ISO file"
  community.general.iso_customize:
    src_iso: "/path/to/ubuntu-22.04-desktop-amd64.iso"
    dest_iso: "/path/to/ubuntu-22.04-desktop-amd64-customized.iso"
    delete_files:
      - "/preseed/ubuntu.seed"
    add_files:
      - src_file: "/path/to/grub.cfg"
        dest_file: "/boot/grub/grub.cfg"
      - src_file: "/path/to/ubuntu.seed"
        dest_file: "/preseed/ubuntu.seed"
  register: customize_iso_result
'''

RETURN = r'''
description:
- In the example, the file /preseed/ubuntu.seed is deleted at first. Then we add local file
- /path/to/ubuntu.seed to /path/to/ubuntu.seed inside ISO. So the file /path/to/ubuntu.seed
- inside ISO is replaced.
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
import copy

PYCDLIB_IMP_ERR = None
try:
    import pycdlib
    HAS_PYCDLIB = True
except ImportError:
    PYCDLIB_IMP_ERR = traceback.format_exc()
    HAS_PYCDLIB = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

MODULE_ISO_CUSTOMIZE = None
ISO_MODE = "iso9660"


# The upper dir exist, we only add subdirectoy
def iso_add_dir(opened_iso, dir_path):
    parent_dir, check_dirname = dir_path.rsplit("/", 1)
    if not parent_dir.strip():
        parent_dir = "/"
    check_dirname = check_dirname.strip()

    for dirname, dirlist, dummy_filelist in opened_iso.walk(iso_path=parent_dir.upper()):
        if dirname == parent_dir.upper():
            if check_dirname.upper() in dirlist:
                return 0, ""

            if parent_dir == "/":
                current_dirpath = "/%s" % check_dirname
            else:
                current_dirpath = "%s/%s" % (parent_dir, check_dirname)

            try:
                if ISO_MODE == "iso9660":
                    opened_iso.add_directory(current_dirpath.upper())
                elif ISO_MODE == "rr":
                    opened_iso.add_directory(current_dirpath.upper(), rr_name=check_dirname)
                elif ISO_MODE == "joliet":
                    opened_iso.add_directory(current_dirpath.upper(), joliet_path=current_dirpath)
                elif ISO_MODE == "udf":
                    opened_iso.add_directory(current_dirpath.upper(), udf_path=current_dirpath)
            except Exception as err:
                msg = "Failed to create dir %s with error: %s" % (current_dirpath, to_native(err))
                return -1, msg

    return 0, ""


def iso_add_dirs(opened_iso, dir_path):
    dirnames = dir_path.strip().split("/")

    current_dirpath = "/"
    for item in dirnames:
        if not item.strip():
            continue
        if current_dirpath == "/":
            current_dirpath = "/%s" % item
        else:
            current_dirpath = "%s/%s" % (current_dirpath, item)

        ret, ret_msg = iso_add_dir(opened_iso, current_dirpath)
        if ret != 0:
            return ret, ret_msg

    return 0, ""


def iso_add_file(opened_iso, src_file, dest_file):
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
        ret, ret_msg = iso_add_dirs(opened_iso, file_dir)
        if ret != 0:
            MODULE_ISO_CUSTOMIZE.fail_json(msg=ret_msg)

    try:
        # The file will be replaced if it exists in ISO
        if ISO_MODE == "iso9660":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path)
        elif ISO_MODE == "rr":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, rr_name=file_name)
        elif ISO_MODE == "joliet":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, joliet_path=dest_file)
        elif ISO_MODE == "udf":
            opened_iso.add_file(file_local, iso_path=file_in_iso_path, udf_path=dest_file)
    except Exception as err:
        msg = "Failed to add local file %s to ISO with error: %s" % (file_local, to_native(err))
        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)

    return 0, ""


def iso_delete_file(opened_iso, dest_file):
    dest_file = dest_file.strip()
    if dest_file[0] != "/":
        dest_file = "/%s" % dest_file
    file_name = os.path.basename(dest_file)

    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    try:
        if ISO_MODE == "iso9660":
            record = opened_iso.get_record(iso_path=file_in_iso_path)
        elif ISO_MODE == "rr":
            record = opened_iso.get_record(rr_path=dest_file)
        elif ISO_MODE == "joliet":
            record = opened_iso.get_record(joliet_path=dest_file)
        elif ISO_MODE == "udf":
            record = opened_iso.get_record(udf_path=dest_file)

        if record and not record.is_file():
            return -1, "the file %s does not exists in ISO or not a file." % dest_file
    except Exception as err:
        msg = "Failed to get record of file %s with error: %s" % (dest_file, to_native(err))
        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)

    try:
        if ISO_MODE == "iso9660":
            opened_iso.rm_file(iso_path=file_in_iso_path)
        elif ISO_MODE == "rr":
            opened_iso.rm_file(iso_path=file_in_iso_path, rr_name=os.path.basename(dest_file))
        elif ISO_MODE == "joliet":
            opened_iso.rm_file(joliet_path=dest_file)
        elif ISO_MODE == "udf":
            opened_iso.rm_file(udf_path=dest_file)
    except Exception as err:
        msg = "Failed to delete iso file %s with error: %s" % (dest_file, to_native(err))
        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)

    return 0, ""


def iso_rebuild(src_iso, dest_iso, op_data_list):
    global ISO_MODE

    try:
        iso = pycdlib.PyCdlib()
        iso.open(src_iso)
        if iso.has_rock_ridge():
            ISO_MODE = "rr"
        elif iso.has_joliet():
            ISO_MODE = "joliet"
        elif iso.has_udf():
            ISO_MODE = "udf"

        for op_data in op_data_list:
            op = op_data['op'].strip()
            data = op_data['data']
            if op == "delete_files":
                for item in data:
                    ret, msg = iso_delete_file(iso, item.strip())
                    if ret != 0:
                        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)
            elif op == "add_files":
                for item in data:
                    ret, msg = iso_add_file(iso, item['src_file'],
                                            item['dest_file'])
                    if ret != 0:
                        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)

        iso.write(dest_iso)
    except Exception as err:
        msg = "Failed to rebuild ISO %s with error: %s" % (src_iso, to_native(err))
        MODULE_ISO_CUSTOMIZE.fail_json(msg=msg)
    finally:
        if iso:
            iso.close()
    return


def main():
    op_data_list = []
    op_data_item = {}
    global MODULE_ISO_CUSTOMIZE

    argument_spec = dict(
        src_iso=dict(type='str', required=True),
        dest_iso=dict(type='str', required=True),
        delete_files=dict(type='list', required=False, elements='str'),
        add_files=dict(type='list', required=False, elements='dict'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )
    if not HAS_PYCDLIB:
        module.fail_json(
            missing_required_lib('pycdlib'), exception=PYCDLIB_IMP_ERR)

    src_iso = module.params.get('src_iso')
    if not os.path.exists(src_iso):
        module.fail_json(msg="The %s does not exist." % src_iso)

    dest_iso = module.params.get('dest_iso')
    if not dest_iso:
        module.fail_json(str(msg='Please specify the path of the customized ISO file \
            using dest_iso parameter.'))

    dest_iso_dir = os.path.dirname(dest_iso)
    if dest_iso_dir and not os.path.exists(dest_iso_dir):
        module.fail_json(msg="The dest directory %s does not exist" % dest_iso_dir)

    MODULE_ISO_CUSTOMIZE = module

    delete_files_list = module.params.get('delete_files')
    if delete_files_list:
        op_data_item['op'] = "delete_files"
        op_data_item['data'] = delete_files_list
        op_data_list.append(copy.deepcopy(op_data_item))

    add_files_list = module.params.get('add_files')
    if add_files_list:
        for item in add_files_list:
            if not os.path.exists(item['src_file']):
                module.fail_json(msg="The %s does not exist." % item['src_file'])
        op_data_item['op'] = "add_files"
        op_data_item['data'] = add_files_list
        op_data_list.append(copy.deepcopy(op_data_item))

    iso_rebuild(src_iso, dest_iso, op_data_list)
    result = dict(
        changed=False,
        src_iso=src_iso,
        customized_iso=dest_iso,
        delete_files=delete_files_list,
        add_files=add_files_list,
    )

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
