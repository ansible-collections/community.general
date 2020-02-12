#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Michael Eaton <meaton@iforium.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub.  actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_firewall
short_description: Enable or disable the Windows Firewall
description:
- Enable or Disable Windows Firewall profiles.
requirements:
  - This module requires Windows Management Framework 5 or later.
options:
  profiles:
    description:
    - Specify one or more profiles to change.
    type: list
    choices: [ Domain, Private, Public ]
    default: [ Domain, Private, Public ]
  state:
    description:
    - Set state of firewall for given profile.
    type: str
    choices: [ disabled, enabled ]
seealso:
- module: win_firewall_rule
author:
- Michael Eaton (@michaeldeaton)
'''

EXAMPLES = r'''
- name: Enable firewall for Domain, Public and Private profiles
  win_firewall:
    state: enabled
    profiles:
    - Domain
    - Private
    - Public
  tags: enable_firewall

- name: Disable Domain firewall
  win_firewall:
    state: disabled
    profiles:
    - Domain
  tags: disable_firewall
'''

RETURN = r'''
enabled:
    description: Current firewall status for chosen profile (after any potential change).
    returned: always
    type: bool
    sample: true
profiles:
    description: Chosen profile.
    returned: always
    type: str
    sample: Domain
state:
    description: Desired state of the given firewall profile(s).
    returned: always
    type: list
    sample: enabled
'''
