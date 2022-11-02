#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: sapcar_extract
short_description: Manages SAP SAPCAR archives
version_added: "3.2.0"
description:
    - Provides support for unpacking C(sar)/C(car) files with the SAPCAR binary from SAP and pulling
      information back into Ansible.
options:
  path:
    description: The path to the SAR/CAR file.
    type: path
    required: true
  dest:
    description:
      - The destination where SAPCAR extracts the SAR file. Missing folders will be created.
        If this parameter is not provided it will unpack in the same folder as the SAR file.
    type: path
  binary_path:
    description:
      - The path to the SAPCAR binary, for example, C(/home/dummy/sapcar) or C(https://myserver/SAPCAR).
        If this parameter is not provided the module will look in C(PATH).
    type: path
  signature:
    description:
      - If C(true) the signature will be extracted.
    default: false
    type: bool
  security_library:
    description:
      - The path to the security library, for example, C(/usr/sap/hostctrl/exe/libsapcrytp.so), for signature operations.
    type: path
  manifest:
    description:
      - The name of the manifest.
    default: "SIGNATURE.SMF"
    type: str
  remove:
    description:
      - If C(true) the SAR/CAR file will be removed. B(This should be used with caution!)
    default: false
    type: bool
author:
    - Rainer Leber (@RainerLeber)
notes:
    - Always returns C(changed=true) in C(check_mode).
'''

EXAMPLES = """
- name: Extract SAR file
  community.general.sapcar_extract:
    path: "~/source/hana.sar"

- name: Extract SAR file with destination
  community.general.sapcar_extract:
    path: "~/source/hana.sar"
    dest: "~/test/"

- name: Extract SAR file with destination and download from webserver can be a fileshare as well
  community.general.sapcar_extract:
    path: "~/source/hana.sar"
    dest: "~/dest/"
    binary_path: "https://myserver/SAPCAR"

- name: Extract SAR file and delete SAR after extract
  community.general.sapcar_extract:
    path: "~/source/hana.sar"
    remove: true

- name: Extract SAR file with manifest
  community.general.sapcar_extract:
    path: "~/source/hana.sar"
    signature: true

- name: Extract SAR file with manifest and rename it
  community.general.sapcar_extract:
    path: "~/source/hana.sar"
    manifest: "MyNewSignature.SMF"
    signature: true
"""

import os
from tempfile import NamedTemporaryFile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
from ansible.module_utils.common.text.converters import to_native


def get_list_of_files(dir_name):
    # create a list of file and directories
    # names in the given directory
    list_of_file = os.listdir(dir_name)
    allFiles = list()
    # Iterate over all the entries
    for entry in list_of_file:
        # Create full path
        fullPath = os.path.join(dir_name, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + [fullPath]
            allFiles = allFiles + get_list_of_files(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def download_SAPCAR(binary_path, module):
    bin_path = None
    # download sapcar binary if url is provided otherwise path is returned
    if binary_path is not None:
        if binary_path.startswith('https://') or binary_path.startswith('http://'):
            random_file = NamedTemporaryFile(delete=False)
            with open_url(binary_path) as response:
                with random_file as out_file:
                    data = response.read()
                    out_file.write(data)
            os.chmod(out_file.name, 0o700)
            bin_path = out_file.name
            module.add_cleanup_file(bin_path)
        else:
            bin_path = binary_path
    return bin_path


def check_if_present(command, path, dest, signature, manifest, module):
    # manipuliating output from SAR file for compare with already extracted files
    iter_command = [command, '-tvf', path]
    sar_out = module.run_command(iter_command)[1]
    sar_raw = sar_out.split("\n")[1:]
    if dest[-1] != "/":
        dest = dest + "/"
    sar_files = [dest + x.split(" ")[-1] for x in sar_raw if x]
    # remove any SIGNATURE.SMF from list because it will not unpacked if signature is false
    if not signature:
        sar_files = [item for item in sar_files if '.SMF' not in item]
    # if signature is renamed manipulate files in list of sar file for compare.
    if manifest != "SIGNATURE.SMF":
        sar_files = [item for item in sar_files if '.SMF' not in item]
        sar_files = sar_files + [manifest]
    # get extracted files if present
    files_extracted = get_list_of_files(dest)
    # compare extracted files with files in sar file
    present = all(elem in files_extracted for elem in sar_files)
    return present


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            dest=dict(type='path'),
            binary_path=dict(type='path'),
            signature=dict(type='bool', default=False),
            security_library=dict(type='path'),
            manifest=dict(type='str', default="SIGNATURE.SMF"),
            remove=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    rc, out, err = [0, "", ""]
    params = module.params
    check_mode = module.check_mode

    path = params['path']
    dest = params['dest']
    signature = params['signature']
    security_library = params['security_library']
    manifest = params['manifest']
    remove = params['remove']

    bin_path = download_SAPCAR(params['binary_path'], module)

    if dest is None:
        dest_head_tail = os.path.split(path)
        dest = dest_head_tail[0] + '/'
    else:
        if not os.path.exists(dest):
            os.makedirs(dest, 0o755)

    if bin_path is not None:
        command = [module.get_bin_path(bin_path, required=True)]
    else:
        try:
            command = [module.get_bin_path('sapcar', required=True)]
        except Exception as e:
            module.fail_json(msg='Failed to find SAPCAR at the expected path or URL "{0}". Please check whether it is available: {1}'
                             .format(bin_path, to_native(e)))

    present = check_if_present(command[0], path, dest, signature, manifest, module)

    if not present:
        command.extend(['-xvf', path, '-R', dest])
        if security_library:
            command.extend(['-L', security_library])
        if signature:
            command.extend(['-manifest', manifest])
        if not check_mode:
            (rc, out, err) = module.run_command(command, check_rc=True)
        changed = True
    else:
        changed = False
        out = "already unpacked"

    if remove:
        os.remove(path)

    module.exit_json(changed=changed, message=rc, stdout=out,
                     stderr=err, command=' '.join(command))


if __name__ == '__main__':
    main()
