#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Ansible Project
# Copyright: (c) 2022, VMware, Inc. All Rights Reserved.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: iso_get_files
short_description: Fetch files from ISO
description:
    - This module is used to get specific files from ISO.
author:
    - Yuhua Zou (@ZouYuhua) <zouy@vmware.com>
requirements:
- "pycdlib"
- "python >= 2.7"
version_added: '5.5.0'

options:
   iso:
     description:
     - This is the absolute paths of source ISO file.
     - Will fail if specified ISO file does not exist on local machine.
     - 'Note: With all ISO9660 levels from 1 to 3, all file names are restricted to uppercase letters, numbers and
       underscores (_). File names are limited to 31 characters, directory nesting is limited to 8 levels, and path
       names are limited to 255 characters.'
     type: path
     required: yes
   get_files:
     description:
     - The absolute path with file name on ISO file.
     type: list
     elements: dict
     required: yes
     suboptions:
       file_in_iso:
         description:
         - the path of file in ISO
         type: path
       file_local:
         description:
         - the local path
         type: path
'''

EXAMPLES = r'''
- name: "Get file from ISO"
  community.general.iso_get_files:
    iso: "/Users/zouy/Documents/ubuntu-22.04-desktop-amd64.iso"
    get_files:
      - file_in_iso: "/preseed/ubuntu.seed"
        file_local: "/tmp/ubuntu.seed.org"
      - file_in_iso: "/boot/grub/grub.cfg"
        file_local: "/tmp/grub.cfg.org"
'''

RETURN = r'''
iso:
    description: paths of source ISO file..
    returned: on success
    type: str
    sample: "/path/to/file.iso"
file_in_iso:
    description: path of the file in ISO.
    returned: on success
    type: str
    sample: "/preseed/ubuntu.seed"
file_local:
    description: path of the local file
    returned: on success
    type: str
    sample: "/tmp/ubuntu.seed"

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


def iso_get_file(module, iso_path, get_files_list):
    try:
        iso = pycdlib.PyCdlib()
        iso.open(iso_path)

        for item in get_files_list:
            file_in_iso = item['file_in_iso'].strip()
            file_local = item['file_local'].strip()

            file_local_dir = os.path.dirname(file_local)
            if not os.path.exists(file_local_dir):
                try:
                    os.makedirs(file_local_dir)
                except OSError as err:
                    iso.close()
                    msg = "Failed to create folder %s with error: %s" % (
                        file_local_dir, to_native(err))
                    return -1, msg

            record = iso.get_record(rr_path=file_in_iso)
            if record.is_file():
                iso.get_file_from_iso(file_local, rr_path=file_in_iso)
            else:
                iso.close()
                return -1, "%s is not a file in ISO" % file_in_iso
    except Exception as err:
        msg = "Exception caught when fetch files from ISO %s with error %s" % (
            iso_path, to_native(err))
        module.fail_json(msg=msg)

    return 0, ""


def main():
    argument_spec = dict(
        iso=dict(type='path', required=True),
        get_files=dict(type='list', required=True, elements='dict'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )
    if not HAS_PYCDLIB:
        module.fail_json(
            missing_required_lib('pycdlib'), exception=PYCDLIB_IMP_ERR)

    iso = module.params.get('iso')
    if not os.path.exists(iso):
        module.fail_json(msg="The %s does not exist." % iso)

    get_files_list = module.params.get('get_files')
    if get_files_list and len(get_files_list) > 0:
        ret, msg = iso_get_file(module, iso, get_files_list)
        if ret != 0:
            module.fail_json(msg=msg)

    result = dict(
        changed=False,
        iso=iso,
        get_files=get_files_list,
    )

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
