#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Ansible Project
# Copyright: (c) 2022, VMware, Inc. All Rights Reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iso_customize
short_description: Customize the ISO file by add/delete/modify files
description:
    - This module is used to customize the ISO file by add/delete/modify files.
author:
    - Yuhua Zou (@ZouYuhua) <zouy@vmware.com>
requirements:
- "pycdlib"
- "python >= 2.7"
version_added: '5.4.0'

options:
   src_iso:
     description:
     - This is the absolute paths of source ISO file.
     - Will fail if specified ISO file does not exist on local machine.
     - 'Note: With all ISO9660 levels from 1 to 3, all file names are restricted to uppercase letters, numbers and
       underscores (_). File names are limited to 31 characters, directory nesting is limited to 8 levels, and path
       names are limited to 255 characters.'
     type: path
     required: yes
   dest_iso:
     description:
     - The absolute path with file name of the customized ISO file on local machine.
     - Will create intermediate folders when they does not exist.
     type: path
     required: yes
   add_files:
     description:
     - The absolute path with file name on ISO file.
     - Will create intermediate folders when they does not exist.
     - The file will be replaced if already exists in ISO.
     type: list
     elements: dict
     required: no
     suboptions:
       src_file: 
         description:
         - The absolute path with file name in local machine.
         type: path
       dest_file: 
         description:
         - The absolute path with file name on ISO file.
         type: path
   delete_files:
     description:
     - The absolute path with file name on ISO file.
     type: list
     elements: path
     required: no
   modify_files:
     description:
     - replace the line/lines with specific string in file of ISO
     type: list
     elements: dict
     required: no
     suboptions:
       file:
         description:
         - The absolute path with file name on ISO file.
         type: path
       regexp:
         description:
         - the match string in line of file, it supports regular expression
         type: str
       replace: 
         description:
         - the target string
         type: str
'''

EXAMPLES = r'''
- name: "Customize ISO file"
  community.general.iso_customize:
    src_iso: "/Users/zouy/Documents/ubuntu-22.04-desktop-amd64.iso"
    dest_iso: "/Users/zouy/Documents/ubuntu-22.04-desktop-amd64-customized.iso"
    delete_files:
      - "/preseed/ubuntu.seed"
    add_files:
      - src_file: "/Users/zouy/Documents/ks.cfg"
        dest_file: "/ks.cfg"
      - src_file: "/Users/zouy/Documents/ubuntu.seed"
        dest_file: "/preseed/ubuntu.seed"
    modify_files:
      - file: "/boot/grub/grub.cfg"
        regexp: "timeout=30"
        replace: "default=0\nset timeout=5"
      - file: "/boot/grub/grub.cfg"
        regexp: "maybe-ubiquity quiet splash ---"
        replace: 'boot=casper debug-ubiquity automatic-ubiquity quiet splash noprompt ---'
  register: customize_iso_result
'''

RETURN = r'''
src_iso:
    description: path of source ISO file.
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
import re
import shutil
import time
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

module_iso_customize = None


# Create local temporary direction to store files getting from ISO
def get_local_tmp_dir():
    tmp_dir = "/tmp/{}".format(time.strftime('%Y-%m-%d-%H-%M-%S',
                               time.localtime(time.time())))
    try:
        os.makedirs(tmp_dir)
    except OSError as err:
        module_iso_customize.fail_json(msg='Exception caught when creating folder {} \
            with error {}'.foramt((tmp_dir, to_native(err))))

    return tmp_dir


def iso_get_file(opened_iso, iso_file, tmp_dir):
    file_name = os.path.basename(iso_file)
    file_local = os.path.join(tmp_dir, file_name)
    if os.path.exists(file_local):
        return 0, file_local

    try:
        record = opened_iso.get_record(rr_path=iso_file)
        if record.is_file():
            opened_iso.get_file_from_iso(file_local, rr_path=iso_file)
        else:
            return -1, "{} is not a file in ISO".format(iso_file)
    except Exception as err:
        module_iso_customize.fail_json(msg="Failed to get iso file {} \
            with error: {}".format(iso_file, to_native(err)))

    if not os.path.exists(file_local):
        return -1, "Failed to get file {} in ISO. \
            Please check the file exists in ISO or not".format(iso_file)

    return 0, file_local


def modify_local_file(local_file, regexp, replace):
    if not os.path.exists(local_file):
        return -1, "Not find file {}".format(local_file)

    shutil.copy(local_file, "{}.org".format(local_file))
    with open(local_file, "r+", encoding="utf-8") as fp:
        lines = fp.readlines()
        for i in range(len(lines)):
            lines[i] = re.sub(regexp, replace, lines[i], count=0)
        fp.seek(0, 0)
        fp.truncate()
        fp.writelines(lines)
        fp.flush()
        fp.close()

    return 0, ""


# The file will be replaced if it exists in ISO
def iso_add_file(opened_iso, src_file, dest_file):
    dest_file = dest_file.strip()
    file_local = src_file.strip()

    file_name = os.path.basename(dest_file)
    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    try:
        opened_iso.add_file(file_local, iso_path=file_in_iso_path,
                            rr_name=file_name.lower())
    except Exception as err:
        module_iso_customize.fail_json(msg="Failed to add local file {} to \
            iso {} with error: {}".format(
                file_local, file_in_iso_path, to_native(err)))

    return 0, ""


def iso_delete_file(opened_iso, dest_file):
    file_name = os.path.basename(dest_file)

    try:
        record = opened_iso.get_record(rr_path=dest_file)
        if record and not record.is_file():
            return -1, "the file {} does not exists in ISO or not a file. \
                ".format(dest_file)
    except Exception as err:
        module_iso_customize.fail_json(msg='Failed to get record for file {}, \
            with error: {}'.format(dest_file, to_native(err)))

    if '.' not in file_name:
        file_in_iso_path = dest_file.upper() + '.;1'
    else:
        file_in_iso_path = dest_file.upper() + ';1'

    try:
        opened_iso.rm_file(
            iso_path=file_in_iso_path, rr_name=file_name.lower())
    except Exception as err:
        module_iso_customize.fail_json(msg="Failed to delete iso file {} with error: \
            {}".format(dest_file, to_native(err)))

    return 0, ""


def iso_replace_file(opened_iso, src_file, dest_file):
    ret, msg = iso_delete_file(opened_iso, dest_file)
    if ret != 0:
        return ret, msg
    return iso_add_file(opened_iso, src_file, dest_file)


def iso_rebuild(src_iso, dest_iso, op_data_list):
    try:
        iso = pycdlib.PyCdlib()
        iso.open(src_iso)

        for op_data in op_data_list:
            op = op_data['op'].strip()
            data = op_data['data']
            if op == "delete_files":
                for item in data:
                    ret, msg = iso_delete_file(iso, item.strip())
                    if ret != 0:
                        module_iso_customize.fail_json(msg=msg)
            elif op == "add_files":
                for item in data:
                    ret, msg = iso_add_file(iso, item['src_file'],
                                            item['dest_file'])
                    if ret != 0:
                        module_iso_customize.fail_json(msg=msg)
            elif op == "modify_files":
                tmp_dir = get_local_tmp_dir()
                for item in data:
                    file_in_iso = item['file'].strip()
                    ret, msg = iso_get_file(iso, file_in_iso, tmp_dir)
                    if ret != 0:
                        module_iso_customize.fail_json(msg=msg)

                    local_file = msg
                    regexp = item['regexp']
                    replace_str = item['replace']
                    ret, msg = modify_local_file(
                        local_file, regexp, replace_str)
                    if ret != 0:
                        module_iso_customize.fail_json(msg=msg)

                    iso_replace_file(iso, local_file, file_in_iso)
                    if ret != 0:
                        module_iso_customize.fail_json(msg=msg)

        iso.write(dest_iso)
    except Exception as err:
        module_iso_customize.fail_json(msg="Failed to rebuild ISO {} \
            with error: {}".format(src_iso, to_native(err)))
    finally:
        if iso:
            iso.close()
    return


def main():
    op_data_list = []
    op_data_item = {}
    global module_iso_customize

    argument_spec = dict(
        src_iso=dict(type='path', required=True),
        dest_iso=dict(type='path', required=True),
        delete_files=dict(type='list', required=False, elements='path'),
        add_files=dict(type='list', required=False, elements='dict'),
        modify_files=dict(type='list', required=False, elements='dict'),
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
        module.fail_json(msg='The {} does not exist.'.format(src_iso))

    dest_iso = module.params.get('dest_iso')
    if dest_iso and len(dest_iso) == 0:
        module.fail_json(msg='Please specify the absolute path of the customized ISO file \
            using dest_iso parameter.')

    dest_iso_dir = os.path.dirname(dest_iso)
    if dest_iso_dir and not os.path.exists(dest_iso_dir):
        # will create intermediate dir for customized ISO file
        try:
            os.makedirs(dest_iso_dir)
        except OSError as err:
            module.fail_json(msg='Exception caught when creating folder {} with error: \
                {}'.format(dest_iso_dir, to_native(err)))

    module_iso_customize = module

    delete_files_list = module.params.get('delete_files')
    if delete_files_list and len(delete_files_list) > 0:
        op_data_item['op'] = "delete_files"
        op_data_item['data'] = delete_files_list
        op_data_list.append(copy.deepcopy(op_data_item))

    add_files_list = module.params.get('add_files')
    if add_files_list and len(add_files_list) > 0:
        for idx in range(len(add_files_list)):
            if not os.path.exists(add_files_list[idx]['src_file']):
                module.fail_json(msg='The {} does not exist.'.format(
                    add_files_list[idx]['src_file']))
        op_data_item['op'] = "add_files"
        op_data_item['data'] = add_files_list
        op_data_list.append(copy.deepcopy(op_data_item))

    modify_files_list = module.params.get('modify_files')
    if modify_files_list and len(modify_files_list) > 0:
        op_data_item['op'] = "modify_files"
        op_data_item['data'] = modify_files_list
        op_data_list.append(copy.deepcopy(op_data_item))

    iso_rebuild(src_iso, dest_iso, op_data_list)
    result = dict(
        changed=False,
        src_iso=src_iso,
        customized_iso=dest_iso,
        delete_files=delete_files_list,
        add_files=add_files_list,
        modify_files=modify_files_list,
    )

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
