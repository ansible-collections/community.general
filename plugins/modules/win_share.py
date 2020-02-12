#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2015, Hans-Joachim Kliemeck <git@kliemeck.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
---
module: win_share
short_description: Manage Windows shares
description:
  - Add, modify or remove Windows share and set share permissions.
requirements:
  - As this module used newer cmdlets like New-SmbShare this can only run on
    Windows 8 / Windows 2012 or newer.
  - This is due to the reliance on the WMI provider MSFT_SmbShare
    U(https://msdn.microsoft.com/en-us/library/hh830471) which was only added
    with these Windows releases.
options:
  name:
    description:
      - Share name.
    type: str
    required: yes
  path:
    description:
      - Share directory.
    type: path
    required: yes
  state:
    description:
      - Specify whether to add C(present) or remove C(absent) the specified share.
    type: str
    choices: [ absent, present ]
    default: present
  description:
    description:
      - Share description.
    type: str
  list:
    description:
      - Specify whether to allow or deny file listing, in case user has no permission on share. Also known as Access-Based Enumeration.
    type: bool
    default: no
  read:
    description:
      - Specify user list that should get read access on share, separated by comma.
    type: str
  change:
    description:
      - Specify user list that should get read and write access on share, separated by comma.
    type: str
  full:
    description:
      - Specify user list that should get full access on share, separated by comma.
    type: str
  deny:
    description:
      - Specify user list that should get no access, regardless of implied access on share, separated by comma.
    type: str
  caching_mode:
    description:
      - Set the CachingMode for this share.
    type: str
    choices: [ BranchCache, Documents, Manual, None, Programs, Unknown ]
    default: Manual
  encrypt:
    description: Sets whether to encrypt the traffic to the share or not.
    type: bool
    default: no
  rule_action:
    description: Whether to add or set (replace) access control entries.
    type: str
    choices: [ set, add ]
    default: set
author:
  - Hans-Joachim Kliemeck (@h0nIg)
  - David Baumann (@daBONDi)
  - Shachaf Goldstein (@Shachaf92)
'''

EXAMPLES = r'''
# Playbook example
# Add share and set permissions
---
- name: Add secret share
  win_share:
    name: internal
    description: top secret share
    path: C:\shares\internal
    list: no
    full: Administrators,CEO
    read: HR-Global
    deny: HR-External

- name: Add public company share
  win_share:
    name: company
    description: top secret share
    path: C:\shares\company
    list: yes
    full: Administrators,CEO
    read: Global

- name: Remove previously added share
  win_share:
    name: internal
    state: absent
'''

RETURN = r'''
actions:
    description: A list of action cmdlets that were run by the module.
    returned: success
    type: list
    sample: ['New-SmbShare -Name share -Path C:\temp']
'''
