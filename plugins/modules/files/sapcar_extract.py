#!/usr/bin/python

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: sapcar_extract
short_description: Manages SAPCAR from SAP
version_added: "3.2.0"
description:
    - Provides support for unpacking sar/car files with the SAPCAR binary from SAP and pulling
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
      - The path to the SAPCAR binary e.g. /home/dummy/sapcar or https://myserver/SAPCAR.
        If this parameter is not provided the module will try excute from application binary e.g /usr/local/bin.
    type: path
  signature:
    description:
      - If true the Signature will be extracted
    default: false
    type: bool
  manifest:
    description:
      - The Name of the manifest defaults to SIGNATURE.SMF.
    default: "SIGNATURE.SMF"
    type: str
  remove:
    description:
      - If true the SAR/CAR file will be removed - !!!This should be used with caution!!!.
    default: false
    type: bool
author:
    - Rainer Leber (@RainerLeber)
'''

EXAMPLES = """
# Extract SAR file - simple
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
    register: sapcar

# Extract SAR file with destination
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
      dest: "~/test/"
    register: sapcar

# Extract SAR file with destination and download from webserver can be a fileshare as well
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
      dest: "~/dest/"
      binary_path: "https://myserver/SAPCAR"
    register: sapcar

# Extract SAR file and delete SAR after extract
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
      remove: true
    register: sapcar

# Extract SAR file with manifest
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
      signature: true
    register: sapcar

# Extract SAR file with manifest and rename it
  - name: Run sapcar extract
    community.general.sapcar_extract:
      path: "~/source/hana.sar"
      manifest: "MyNewSignature.SMF"
      signature: true
    register: sapcar

"""

import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url


def getListOfFiles(dirName):
    # create a list of file and directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if os.path.isdir(fullPath):
            allFiles = allFiles + [fullPath]
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def downloadSAPCAR(binary_path):
    bin_path = None
    # download sapcar binary if url is provided otherwise path is returned
    if binary_path is not None:
        try:
            with open_url(binary_path) as response:
                with open("/tmp/sapcar", 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)
            os.chmod("/tmp/sapcar", 0o755)
            bin_path = "/tmp/sapcar"
        except Exception:
            bin_path = binary_path
    return bin_path


def checkifPresent(command, path, dest, signature, manifest):
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
    files_extracted = getListOfFiles(dest)
    # compare extracted files with files in sar file
    present = all(elem in files_extracted for elem in sar_files)
    return present


def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            dest=dict(type='path'),
            binary_path=dict(type='path'),
            signature=dict(type='bool', default=False),
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
    manifest = params['manifest']
    remove = params['remove']

    bin_path = downloadSAPCAR(params['binary_path'])

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
            command = [module.get_bin_path('/tmp/sapcar' or '/tmp/SAPCAR', required=True)]
        except Exception:
            command = [module.get_bin_path('sapcar', required=True)]

    present = checkifPresent(command[0], path, dest, signature, manifest)

    if not present:
        if not signature:
            command.extend(['-xvf', path, '-R', dest])
        else:
            command.extend(['-xvf', path, '-R', dest, '-manifest', manifest])
        if not check_mode:
            (rc, out, err) = module.run_command(command, check_rc=True)
        changed = True
    else:
        changed = False
        out = "allready unpacked"

    if remove:
        os.remove(path)

    module.exit_json(changed=changed, message=rc, stdout=out,
                     stderr=err, command=' '.join(command))


if __name__ == '__main__':
    main()
