#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub.  actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
---
module: win_stat
short_description: Get information about Windows files
description:
     - Returns information about a Windows file.
     - For non-Windows targets, use the M(stat) module instead.
options:
    path:
        description:
            - The full path of the file/object to get the facts of; both forward and
              back slashes are accepted.
        type: path
        required: yes
        aliases: [ dest, name ]
    get_checksum:
        description:
            - Whether to return a checksum of the file (default sha1)
        type: bool
        default: yes
    checksum_algorithm:
        description:
            - Algorithm to determine checksum of file.
            - Will throw an error if the host is unable to use specified algorithm.
        type: str
        default: sha1
        choices: [ md5, sha1, sha256, sha384, sha512 ]
    follow:
        description:
            - Whether to follow symlinks or junction points.
            - In the case of C(path) pointing to another link, then that will
              be followed until no more links are found.
        type: bool
        default: no
seealso:
- module: stat
- module: win_acl
- module: win_file
- module: win_owner
author:
- Chris Church (@cchurch)
'''

EXAMPLES = r'''
- name: Obtain information about a file
  win_stat:
    path: C:\foo.ini
  register: file_info

- name: Obtain information about a folder
  win_stat:
    path: C:\bar
  register: folder_info

- name: Get MD5 checksum of a file
  win_stat:
    path: C:\foo.ini
    get_checksum: yes
    checksum_algorithm: md5
  register: md5_checksum

- debug:
    var: md5_checksum.stat.checksum

- name: Get SHA1 checksum of file
  win_stat:
    path: C:\foo.ini
    get_checksum: yes
  register: sha1_checksum

- debug:
    var: sha1_checksum.stat.checksum

- name: Get SHA256 checksum of file
  win_stat:
    path: C:\foo.ini
    get_checksum: yes
    checksum_algorithm: sha256
  register: sha256_checksum

- debug:
    var: sha256_checksum.stat.checksum
'''

RETURN = r'''
changed:
    description: Whether anything was changed
    returned: always
    type: bool
    sample: true
stat:
    description: dictionary containing all the stat data
    returned: success
    type: complex
    contains:
        attributes:
            description: Attributes of the file at path in raw form.
            returned: success, path exists
            type: str
            sample: "Archive, Hidden"
        checksum:
            description: The checksum of a file based on checksum_algorithm specified.
            returned: success, path exist, path is a file, get_checksum == True
              checksum_algorithm specified is supported
            type: str
            sample: 09cb79e8fc7453c84a07f644e441fd81623b7f98
        creationtime:
            description: The create time of the file represented in seconds since epoch.
            returned: success, path exists
            type: float
            sample: 1477984205.15
        exists:
            description: If the path exists or not.
            returned: success
            type: bool
            sample: true
        extension:
            description: The extension of the file at path.
            returned: success, path exists, path is a file
            type: str
            sample: ".ps1"
        filename:
            description: The name of the file (without path).
            returned: success, path exists, path is a file
            type: str
            sample: foo.ini
        hlnk_targets:
            description: List of other files pointing to the same file (hard links), excludes the current file.
            returned: success, path exists
            type: list
            sample:
            - C:\temp\file.txt
            - C:\Windows\update.log
        isarchive:
            description: If the path is ready for archiving or not.
            returned: success, path exists
            type: bool
            sample: true
        isdir:
            description: If the path is a directory or not.
            returned: success, path exists
            type: bool
            sample: true
        ishidden:
            description: If the path is hidden or not.
            returned: success, path exists
            type: bool
            sample: true
        isjunction:
            description: If the path is a junction point or not.
            returned: success, path exists
            type: bool
            sample: true
        islnk:
            description: If the path is a symbolic link or not.
            returned: success, path exists
            type: bool
            sample: true
        isreadonly:
            description: If the path is read only or not.
            returned: success, path exists
            type: bool
            sample: true
        isreg:
            description: If the path is a regular file.
            returned: success, path exists
            type: bool
            sample: true
        isshared:
            description: If the path is shared or not.
            returned: success, path exists
            type: bool
            sample: true
        lastaccesstime:
            description: The last access time of the file represented in seconds since epoch.
            returned: success, path exists
            type: float
            sample: 1477984205.15
        lastwritetime:
            description: The last modification time of the file represented in seconds since epoch.
            returned: success, path exists
            type: float
            sample: 1477984205.15
        lnk_source:
            description: Target of the symlink normalized for the remote filesystem.
            returned: success, path exists and the path is a symbolic link or junction point
            type: str
            sample: C:\temp\link
        lnk_target:
            description: Target of the symlink. Note that relative paths remain relative.
            returned: success, path exists and the path is a symbolic link or junction point
            type: str
            sample: ..\link
        nlink:
            description: Number of links to the file (hard links).
            returned: success, path exists
            type: int
            sample: 1
        owner:
            description: The owner of the file.
            returned: success, path exists
            type: str
            sample: BUILTIN\Administrators
        path:
            description: The full absolute path to the file.
            returned: success, path exists, file exists
            type: str
            sample: C:\foo.ini
        sharename:
            description: The name of share if folder is shared.
            returned: success, path exists, file is a directory and isshared == True
            type: str
            sample: file-share
        size:
            description: The size in bytes of a file or folder.
            returned: success, path exists, file is not a link
            type: int
            sample: 1024
'''
