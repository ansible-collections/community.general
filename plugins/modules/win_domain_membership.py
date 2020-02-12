#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
module: win_domain_membership
short_description: Manage domain/workgroup membership for a Windows host
description:
- Manages domain membership or workgroup membership for a Windows host. Also supports hostname changes.
- This module may require subsequent use of the M(win_reboot) action if changes are made.
options:
  dns_domain_name:
    description:
      - When C(state) is C(domain), the DNS name of the domain to which the targeted Windows host should be joined.
    type: str
  domain_admin_user:
    description:
      - Username of a domain admin for the target domain (required to join or leave the domain).
    type: str
    required: yes
  domain_admin_password:
    description:
      - Password for the specified C(domain_admin_user).
    type: str
  hostname:
    description:
      - The desired hostname for the Windows host.
    type: str
  domain_ou_path:
    description:
      - The desired OU path for adding the computer object.
      - This is only used when adding the target host to a domain, if it is already a member then it is ignored.
    type: str
  state:
    description:
      - Whether the target host should be a member of a domain or workgroup.
    type: str
    choices: [ domain, workgroup ]
  workgroup_name:
    description:
      - When C(state) is C(workgroup), the name of the workgroup that the Windows host should be in.
    type: str
seealso:
- module: win_domain
- module: win_domain_controller
- module: win_domain_computer
- module: win_domain_group
- module: win_domain_user
- module: win_group
- module: win_group_membership
- module: win_user
author:
    - Matt Davis (@nitzmahone)
'''

RETURN = r'''
reboot_required:
    description: True if changes were made that require a reboot.
    returned: always
    type: bool
    sample: true
'''

EXAMPLES = r'''

# host should be a member of domain ansible.vagrant; module will ensure the hostname is mydomainclient
# and will use the passed credentials to join domain if necessary.
# Ansible connection should use local credentials if possible.
# If a reboot is required, the second task will trigger one and wait until the host is available.
- hosts: winclient
  gather_facts: no
  tasks:
  - win_domain_membership:
      dns_domain_name: ansible.vagrant
      hostname: mydomainclient
      domain_admin_user: testguy@ansible.vagrant
      domain_admin_password: password123!
      domain_ou_path: "OU=Windows,OU=Servers,DC=ansible,DC=vagrant"
      state: domain
    register: domain_state

  - win_reboot:
    when: domain_state.reboot_required



# Host should be in workgroup mywg- module will use the passed credentials to clean-unjoin domain if possible.
# Ansible connection should use local credentials if possible.
# The domain admin credentials can be sourced from a vault-encrypted variable
- hosts: winclient
  gather_facts: no
  tasks:
  - win_domain_membership:
      workgroup_name: mywg
      domain_admin_user: '{{ win_domain_admin_user }}'
      domain_admin_password: '{{ win_domain_admin_password }}'
      state: workgroup
'''
