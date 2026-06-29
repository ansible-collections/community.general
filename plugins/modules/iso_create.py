#!/usr/bin/python

# Copyright (c) 2020, Ansible Project
# Copyright (c) 2020, VMware, Inc. All Rights Reserved.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: iso_create
short_description: Generate ISO file with specified files or folders
description:
  - This module is used to generate ISO file with specified path of files.
author:
  - Diane Wang (@Tomorrow9) <dianew@vmware.com>
requirements:
  - "pycdlib"
version_added: '0.2.0'

extends_documentation_fragment:
  - community.general._attributes

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  src_files:
    description:
      - This is a list of absolute paths of source files or folders to be contained in the new generated ISO file.
      - The module fails if specified file or folder in O(src_files) does not exist on local machine.
      - 'Note: With all ISO9660 levels from 1 to 3, all file names are restricted to uppercase letters, numbers and underscores
        (_). File names are limited to 31 characters, directory nesting is limited to 8 levels, and path names are limited
        to 255 characters.'
    type: list
    required: true
    elements: path
  dest_iso:
    description:
      - The absolute path with file name of the new generated ISO file on local machine.
      - It creates intermediate folders when they do not exist.
    type: path
    required: true
  interchange_level:
    description:
      - The ISO9660 interchange level to use, it dictates the rules on the names of files.
      - Levels and valid values V(1), V(2), V(3), V(4) are supported.
      - The default value is level V(1), which is the most conservative, level V(3) is recommended.
      - ISO9660 file names at interchange level V(1) cannot have more than 8 characters or 3 characters in the extension.
    type: int
    default: 1
    choices: [1, 2, 3, 4]
  vol_ident:
    description:
      - The volume identification string to use on the new generated ISO image.
    type: str
  rock_ridge:
    description:
      - Whether to make this ISO have the Rock Ridge extensions or not.
      - Valid values are V(1.09), V(1.10) or V(1.12), means adding the specified Rock Ridge version to the ISO.
      - If unsure, set V(1.09) to ensure maximum compatibility.
      - If not specified, then not add Rock Ridge extension to the ISO.
    type: str
    choices: ['1.09', '1.10', '1.12']
  joliet:
    description:
      - Support levels and valid values are V(1), V(2), or V(3).
      - Level V(3) is by far the most common.
      - If not specified, then no Joliet support is added.
    type: int
    choices: [1, 2, 3]
  udf:
    description:
      - Whether to add UDF support to this ISO.
      - If set to V(true), then version 2.60 of the UDF spec is used.
      - If not specified or set to V(false), then no UDF support is added.
    type: bool
    default: false
  boot_options:
    description:
      - Options for making the ISO bootable using El Torito boot support.
      - If not specified, the ISO will not be bootable.
    type: dict
    version_added: 13.0.0
    suboptions:
      boot_file:
        description:
          - Local path to the boot image file to embed in the ISO.
          - The file is added to the root of the ISO and referenced as the El Torito boot image.
          - The boot image must not share a filename with any file added via O(src_files), or pycdlib will raise a duplicate entry error.
        type: path
        required: true
      boot_catalog:
        description:
          - ISO9660 path for the El Torito boot catalog file inside the ISO.
        type: str
        default: '/BOOT.CAT;1'
      media_name:
        description:
          - Media emulation type for the El Torito boot entry.
        type: str
        default: 'noemul'
        choices: ['noemul', 'floppy', '1.2m', '1.44m', '2.88m']
      platform_id:
        description:
          - Target platform for the El Torito boot entry.
        type: str
        default: 'x86'
        choices: ['x86', 'efi', 'mac']
      boot_info_table:
        description:
          - Whether to add a boot info table to the boot image.
          - Required by some bootloaders such as ISOLINUX.
        type: bool
        default: false
"""

EXAMPLES = r"""
- name: Create an ISO file
  community.general.iso_create:
    src_files:
      - /root/testfile.yml
      - /root/testfolder
    dest_iso: /tmp/test.iso
    interchange_level: 3

- name: Create an ISO file with Rock Ridge extension
  community.general.iso_create:
    src_files:
      - /root/testfile.yml
      - /root/testfolder
    dest_iso: /tmp/test.iso
    rock_ridge: 1.09

- name: Create an ISO file with Joliet support
  community.general.iso_create:
    src_files:
      - ./windows_config/Autounattend.xml
    dest_iso: ./test.iso
    interchange_level: 3
    joliet: 3
    vol_ident: WIN_AUTOINSTALL

- name: Create a bootable ISO file using ISOLINUX
  community.general.iso_create:
    src_files:
      - /root/isocontents/isolinux.cfg
    dest_iso: /tmp/boot.iso
    interchange_level: 3
    boot_options:
      boot_file: /root/isocontents/isolinux.bin
      media_name: noemul
      boot_info_table: true
"""

RETURN = r"""
source_file:
  description: Configured source files or directories list.
  returned: on success
  type: list
  elements: path
  sample: ["/path/to/file.txt", "/path/to/folder"]
created_iso:
  description: Created iso file path.
  returned: on success
  type: str
  sample: "/path/to/test.iso"
interchange_level:
  description: Configured interchange level.
  returned: on success
  type: int
  sample: 3
vol_ident:
  description: Configured volume identification string.
  returned: on success
  type: str
  sample: "OEMDRV"
joliet:
  description: Configured Joliet support level.
  returned: on success
  type: int
  sample: 3
rock_ridge:
  description: Configured Rock Ridge version.
  returned: on success
  type: str
  sample: "1.09"
udf:
  description: Configured UDF support.
  returned: on success
  type: bool
  sample: false
boot_options:
  description: Configured El Torito boot options, or V(null) if the ISO is not bootable.
  returned: on success
  type: dict
  version_added: 13.0.0
  contains:
    boot_file:
      description: Local path to the boot image file.
      type: str
      sample: "/root/isolinux/isolinux.bin"
    boot_catalog:
      description: ISO9660 path of the boot catalog inside the ISO.
      type: str
      sample: "/BOOT.CAT;1"
    media_name:
      description: Media emulation type.
      type: str
      sample: "noemul"
    platform_id:
      description: Target platform identifier.
      type: str
      sample: "x86"
    boot_info_table:
      description: Whether a boot info table was added to the boot image.
      type: bool
      sample: false
"""

import os
import traceback

PLATFORM_ID_MAP = {
    "x86": b"\x00",
    "efi": b"\xef",
    "mac": b"\x02",
}

PYCDLIB_IMP_ERR = None
try:
    import pycdlib

    HAS_PYCDLIB = True
except ImportError:
    PYCDLIB_IMP_ERR = traceback.format_exc()
    HAS_PYCDLIB = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def add_file(module, iso_file=None, src_file=None, file_path=None, rock_ridge=None, use_joliet=None, use_udf=None):
    rr_name = None
    joliet_path = None
    udf_path = None
    # In standard ISO interchange level 1, file names have a maximum of 8 characters, followed by a required dot,
    # followed by a maximum 3 character extension, followed by a semicolon and a version
    file_name = os.path.basename(file_path)
    if "." not in file_name:
        file_in_iso_path = f"{file_path.upper()}.;1"
    else:
        file_in_iso_path = f"{file_path.upper()};1"
    if rock_ridge:
        rr_name = file_name
    if use_joliet:
        joliet_path = file_path
    if use_udf:
        udf_path = file_path
    try:
        iso_file.add_file(
            src_file, iso_path=file_in_iso_path, rr_name=rr_name, joliet_path=joliet_path, udf_path=udf_path
        )
    except Exception as err:
        module.fail_json(msg=f"Failed to add file {src_file} to ISO file due to {err}")


def add_directory(module, iso_file=None, dir_path=None, rock_ridge=None, use_joliet=None, use_udf=None):
    rr_name = None
    joliet_path = None
    udf_path = None
    iso_dir_path = dir_path.upper()
    if rock_ridge:
        rr_name = os.path.basename(dir_path)
    if use_joliet:
        joliet_path = dir_path
    if use_udf:
        udf_path = dir_path
    try:
        iso_file.add_directory(iso_path=iso_dir_path, rr_name=rr_name, joliet_path=joliet_path, udf_path=udf_path)
    except Exception as err:
        module.fail_json(msg=f"Failed to directory {dir_path} to ISO file due to {err}")


def main():
    argument_spec = dict(
        src_files=dict(type="list", required=True, elements="path"),
        dest_iso=dict(type="path", required=True),
        interchange_level=dict(type="int", choices=[1, 2, 3, 4], default=1),
        vol_ident=dict(type="str"),
        rock_ridge=dict(type="str", choices=["1.09", "1.10", "1.12"]),
        joliet=dict(type="int", choices=[1, 2, 3]),
        udf=dict(type="bool", default=False),
        boot_options=dict(
            type="dict",
            options=dict(
                boot_file=dict(type="path", required=True),
                boot_catalog=dict(type="str", default="/BOOT.CAT;1"),
                media_name=dict(type="str", default="noemul", choices=["noemul", "floppy", "1.2m", "1.44m", "2.88m"]),
                platform_id=dict(type="str", default="x86", choices=["x86", "efi", "mac"]),
                boot_info_table=dict(type="bool", default=False),
            ),
        ),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    if not HAS_PYCDLIB:
        module.fail_json(missing_required_lib("pycdlib"), exception=PYCDLIB_IMP_ERR)

    src_file_list = module.params.get("src_files")
    if src_file_list and len(src_file_list) == 0:
        module.fail_json(msg="Please specify source file and/or directory list using src_files parameter.")
    for src_file in src_file_list:
        if not os.path.exists(src_file):
            module.fail_json(msg=f"Specified source file/directory path does not exist on local machine, {src_file}")

    boot_options = module.params.get("boot_options")
    if boot_options:
        boot_file = boot_options["boot_file"]
        if not os.path.exists(boot_file):
            module.fail_json(msg=f"Specified boot file path does not exist on local machine, {boot_file}")

    dest_iso = module.params.get("dest_iso")
    if dest_iso and len(dest_iso) == 0:
        module.fail_json(msg="Please specify the absolute path of the new created ISO file using dest_iso parameter.")

    dest_iso_dir = os.path.dirname(dest_iso)
    if dest_iso_dir and not os.path.exists(dest_iso_dir):
        # will create intermediate dir for new ISO file
        try:
            os.makedirs(dest_iso_dir)
        except OSError as err:
            module.fail_json(msg=f"Exception caught when creating folder {dest_iso_dir}, with error {err}")

    volume_id = module.params.get("vol_ident")
    if volume_id is None:
        volume_id = ""
    inter_level = module.params.get("interchange_level")
    rock_ridge = module.params.get("rock_ridge")
    use_joliet = module.params.get("joliet")
    use_udf = None
    if module.params["udf"]:
        use_udf = "2.60"

    result = dict(
        changed=False,
        source_file=src_file_list,
        created_iso=dest_iso,
        interchange_level=inter_level,
        vol_ident=volume_id,
        rock_ridge=rock_ridge,
        joliet=use_joliet,
        udf=use_udf,
        boot_options=boot_options,
    )
    if not module.check_mode:
        iso_file = pycdlib.PyCdlib(always_consistent=True)
        iso_file.new(
            interchange_level=inter_level, vol_ident=volume_id, rock_ridge=rock_ridge, joliet=use_joliet, udf=use_udf
        )

        for src_file in src_file_list:
            # if specify a dir then go through the dir to add files and dirs
            if os.path.isdir(src_file):
                dir_list = []
                file_list = []
                src_file = src_file.rstrip("/")
                dir_name = os.path.basename(src_file)
                add_directory(
                    module,
                    iso_file=iso_file,
                    dir_path=f"/{dir_name}",
                    rock_ridge=rock_ridge,
                    use_joliet=use_joliet,
                    use_udf=use_udf,
                )

                # get dir list and file list
                for path, dirs, files in os.walk(src_file):
                    for filename in files:
                        file_list.append(os.path.join(path, filename))
                    for dir in dirs:
                        dir_list.append(os.path.join(path, dir))
                for new_dir in dir_list:
                    add_directory(
                        module,
                        iso_file=iso_file,
                        dir_path=new_dir.split(os.path.dirname(src_file))[1],
                        rock_ridge=rock_ridge,
                        use_joliet=use_joliet,
                        use_udf=use_udf,
                    )
                for new_file in file_list:
                    add_file(
                        module,
                        iso_file=iso_file,
                        src_file=new_file,
                        file_path=new_file.split(os.path.dirname(src_file))[1],
                        rock_ridge=rock_ridge,
                        use_joliet=use_joliet,
                        use_udf=use_udf,
                    )
            # if specify a file then add this file directly to the '/' path in ISO
            else:
                add_file(
                    module,
                    iso_file=iso_file,
                    src_file=src_file,
                    file_path=f"/{os.path.basename(src_file)}",
                    rock_ridge=rock_ridge,
                    use_joliet=use_joliet,
                    use_udf=use_udf,
                )

        if boot_options:
            boot_file = boot_options["boot_file"]
            boot_file_basename = os.path.basename(boot_file)
            if "." not in boot_file_basename:
                boot_iso_path = f"/{boot_file_basename.upper()}.;1"
            else:
                boot_iso_path = f"/{boot_file_basename.upper()};1"
            add_file(
                module,
                iso_file=iso_file,
                src_file=boot_file,
                file_path=f"/{boot_file_basename}",
                rock_ridge=rock_ridge,
                use_joliet=use_joliet,
                use_udf=use_udf,
            )
            boot_catalog_basename = os.path.basename(boot_options["boot_catalog"]).split(";")[0].lower()
            eltorito_kwargs = dict(
                bootcatfile=boot_options["boot_catalog"],
                media_name=boot_options["media_name"],
                platform_id=PLATFORM_ID_MAP[boot_options["platform_id"]],
                boot_info_table=boot_options["boot_info_table"],
            )
            if rock_ridge:
                eltorito_kwargs["rr_bootcatfile"] = boot_catalog_basename
            if use_joliet:
                eltorito_kwargs["joliet_bootcatfile"] = f"/{boot_catalog_basename}"
            try:
                iso_file.add_eltorito(boot_iso_path, **eltorito_kwargs)
            except Exception as err:
                module.fail_json(msg=f"Failed to add El Torito boot record to ISO file: {err}")

        iso_file.write(dest_iso)
        iso_file.close()

    result["changed"] = True
    module.exit_json(**result)


if __name__ == "__main__":
    main()
