#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Chris Hoffman <choffman@chathamfinancial.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub.  actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
---
module: win_group
short_description: Add and remove local groups
description:
    - Add and remove local groups.
    - For non-Windows targets, please use the M(group) module instead.
options:
  name:
    description:
      - Name of the group.
    type: str
    required: yes
  description:
    description:
      - Description of the group.
    type: str
  state:
    description:
      - Create or remove the group.
    type: str
    choices: [ absent, present ]
    default: present
seealso:
- module: group
- module: win_domain_group
- module: win_group_membership
author:
- Chris Hoffman (@chrishoffman)
'''

EXAMPLES = r'''
- name: Create a new group
  win_group:
    name: deploy
    description: Deploy Group
    state: present

- name: Remove a group
  win_group:
    name: deploy
    state: absent
'''
