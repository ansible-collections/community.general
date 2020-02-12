#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Noah Sparks <nsparks@outlook.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_audit_rule
short_description: Adds an audit rule to files, folders, or registry keys
description:
  - Used to apply audit rules to files, folders or registry keys.
  - Once applied, it will begin recording the user who performed the operation defined into the Security
    Log in the Event viewer.
  - The behavior is designed to ignore inherited rules since those cannot be adjusted without first disabling
    the inheritance behavior. It will still print inherited rules in the output though for debugging purposes.
options:
  path:
    description:
      - Path to the file, folder, or registry key.
      - Registry paths should be in Powershell format, beginning with an abbreviation for the root
        such as, C(HKLM:\Software).
    type: path
    required: yes
    aliases: [ dest, destination ]
  user:
    description:
      - The user or group to adjust rules for.
    type: str
    required: yes
  rights:
    description:
      - Comma separated list of the rights desired. Only required for adding a rule.
      - If I(path) is a file or directory, rights can be any right under MSDN
        FileSystemRights U(https://msdn.microsoft.com/en-us/library/system.security.accesscontrol.filesystemrights.aspx).
      - If I(path) is a registry key, rights can be any right under MSDN
        RegistryRights U(https://msdn.microsoft.com/en-us/library/system.security.accesscontrol.registryrights.aspx).
    type: list
    required: yes
  inheritance_flags:
    description:
      - Defines what objects inside of a folder or registry key will inherit the settings.
      - If you are setting a rule on a file, this value has to be changed to C(none).
      - For more information on the choices see MSDN PropagationFlags enumeration
        at U(https://msdn.microsoft.com/en-us/library/system.security.accesscontrol.inheritanceflags.aspx).
    type: list
    choices: [ ContainerInherit, ObjectInherit ]
    default: ContainerInherit,ObjectInherit
  propagation_flags:
    description:
      - Propagation flag on the audit rules.
      - This value is ignored when the path type is a file.
      - For more information on the choices see MSDN PropagationFlags enumeration
        at U(https://msdn.microsoft.com/en-us/library/system.security.accesscontrol.propagationflags.aspx).
    choices: [ None, InherityOnly, NoPropagateInherit ]
    default: "None"
  audit_flags:
    description:
      - Defines whether to log on failure, success, or both.
      - To log both define as comma separated list "Success, Failure".
    type: list
    required: yes
    choices: [ Failure, Success ]
  state:
    description:
      - Whether the rule should be C(present) or C(absent).
      - For absent, only I(path), I(user), and I(state) are required.
      - Specifying C(absent) will remove all rules matching the defined I(user).
    type: str
    choices: [ absent, present ]
    default: present
seealso:
- module: win_audit_policy_system
author:
  - Noah Sparks (@nwsparks)
'''

EXAMPLES = r'''
- name: Add filesystem audit rule for a folder
  win_audit_rule:
    path: C:\inetpub\wwwroot\website
    user: BUILTIN\Users
    rights: write,delete,changepermissions
    audit_flags: success,failure
    inheritance_flags: ContainerInherit,ObjectInherit

- name: Add filesystem audit rule for a file
  win_audit_rule:
    path: C:\inetpub\wwwroot\website\web.config
    user: BUILTIN\Users
    rights: write,delete,changepermissions
    audit_flags: success,failure
    inheritance_flags: None

- name: Add registry audit rule
  win_audit_rule:
    path: HKLM:\software
    user: BUILTIN\Users
    rights: delete
    audit_flags: 'success'

- name: Remove filesystem audit rule
  win_audit_rule:
    path: C:\inetpub\wwwroot\website
    user: BUILTIN\Users
    state: absent

- name: Remove registry audit rule
  win_audit_rule:
    path: HKLM:\software
    user: BUILTIN\Users
    state: absent
'''

RETURN = r'''
current_audit_rules:
  description:
    - The current rules on the defined I(path)
    - Will return "No audit rules defined on I(path)"
  returned: always
  type: dict
  sample: |
    {
      "audit_flags": "Success",
      "user": "Everyone",
      "inheritance_flags": "False",
      "is_inherited": "False",
      "propagation_flags": "None",
      "rights": "Delete"
    }
path_type:
  description:
    - The type of I(path) being targetted.
    - Will be one of file, directory, registry.
  returned: always
  type: str
'''
