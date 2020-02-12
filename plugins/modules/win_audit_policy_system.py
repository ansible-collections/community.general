#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Noah Sparks <nsparks@outlook.com>
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_audit_policy_system
short_description: Used to make changes to the system wide Audit Policy
description:
  - Used to make changes to the system wide Audit Policy.
options:
  category:
    description:
      - Single string value for the category you would like to adjust the policy on.
      - Cannot be used with I(subcategory). You must define one or the other.
      - Changing this setting causes all subcategories to be adjusted to the defined I(audit_type).
    type: str
  subcategory:
    description:
      - Single string value for the subcategory you would like to adjust the policy on.
      - Cannot be used with I(category). You must define one or the other.
    type: str
  audit_type:
    description:
      - The type of event you would like to audit for.
      - Accepts a list. See examples.
    type: list
    required: yes
    choices: [ failure, none, success ]
notes:
  - It is recommended to take a backup of the policies before adjusting them for the first time.
  - See this page for in depth information U(https://technet.microsoft.com/en-us/library/cc766468.aspx).
seealso:
- module: win_audit_rule
author:
  - Noah Sparks (@nwsparks)
'''

EXAMPLES = r'''
- name: Enable failure auditing for the subcategory "File System"
  win_audit_policy_system:
    subcategory: File System
    audit_type: failure

- name: Enable all auditing types for the category "Account logon events"
  win_audit_policy_system:
    category: Account logon events
    audit_type: success, failure

- name: Disable auditing for the subcategory "File System"
  win_audit_policy_system:
    subcategory: File System
    audit_type: none
'''

RETURN = r'''
current_audit_policy:
  description: details on the policy being targetted
  returned: always
  type: dict
  sample: |-
    {
      "File Share":"failure"
    }
'''
