#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2022, Jonathan Lung (@lungj) <lungj@heresjono.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: bitwarden_info
author:
    - Jonathan Lung (@lungj)
requirements:
    - C(bw) Bitwarden command line utility. See U(https://bitwarden.com/help/cli/)
    - Organization names in Bitwarden are unique.
    - Folders in Bitwarden have no duplicate names per organization.
    - The name of items in folders uniquely identifies the items per organization.
notes:
    - Tested with C(bw) version 2022.6.2
short_description: Get items from Bitwarden
description:
    - M(community.general.bitwarden_info) wraps the C(bw) command line utility to read Bitwarden-compatible vaults.
    - A fatal error occurs if any of the items being searched for can not be found.
    - Recommend using with the C(no_log) option to avoid logging the values of the secrets being retrieved.
options:
    cli_path:
        type: path
        description: Used to specify the exact path to the C(bw) command line interface
        default: 'bw'
    organization_name:
        type: str
        description:
            - Name of organization to target.
            - Leave as C(null) for a wildcard vault or C('') for personal vaults.
            - Mutually exclusive with I(organization_id).
    organization_id:
        type: str
        description:
            - UID of organization to target.
            - Leave as C(null) for a wildcard vault.
            - Mutually exclusive with I(organization_name).
    folder_name:
        type: str
        description:
            - Name of folder to target.
            - Leave as C(null) for a wildcard folder.
            - Use C('') or C('No Folder') for no folder.
            - Mutually exclusive with I(folder_id).
    folder_id:
        type: str
        description:
            - UID of folder to target.
            - Leave as C(null) for a wildcard folder.
            - Mutually exclusive with I(folder_name).
    item_name:
        type: str
        description:
            - Name of item to target.
            - Mutually exclusive with I(item_id).
    item_id:
        type: str
        description:
            - UID of item to target.
            - Mutually exclusive with I(item_name).
    target:
        type: str
        description:
            - The type of item being queried.
        choices:
            - item
            - items
            - folder
            - folders
            - organization
            - organizations
        default: 'item'
'''

EXAMPLES = '''
- name: "Get all organizations"
  community.general.bitwarden:
    organization_name: null
    target: "organizations"
  delegate_to: "localhost"

- name: "Get all folders"
  community.general.bitwarden:
    target: "folders"
  delegate_to: "localhost"

- name: "Get all items in a folder within an organization"
  community.general.bitwarden:
    organization_name: "Test"
    folder_name: "my_folder"
    target: "items"
  delegate_to: "localhost"

- name: "Get an item without an organization in a specific folder"
  community.general.bitwarden:
    organization_name: ""
    folder_name: "my_folder"
    item_name: "a secret item"
    target: "items"
  register: "ret_val"
  delegate_to: "localhost"

# Note this will not display anything due to no_log being set.
- name: "Access the password"
  ansible.builtin.debug:
    msg: >-
      {{ ret_val['ansible_module_results']['login']['password'] }}
'''

RETURN = '''
---
# A dictionary with the queried state.
'''


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.bitwarden import (
    BitwardenException, Client, Organization, organizations
)


class BitwardenInfo(object):
    '''Accessor for Bitwarden vault information.'''
    organization = property(lambda self: self._organization)
    folder = property(lambda self: self._folder)
    item = property(lambda self: self._item)

    def __init__(self, module):
        self._organization = Organization(
            name=module.params.get('organization_name'),
            id_=module.params.get('organization_id')
        )

        self._folder = self.organization.get_folder(
            name=module.params.get('folder_name'),
            id_=module.params.get('folder_id')
        )

        self._item = self.folder.get_item(
            name=module.params.get('item_name'),
            id_=module.params.get('item_id')
        )

        self._target = module.params.get('target')

    def run(self):
        '''Handle requests.'''
        # Use a lookup table to determine how to handle the query.
        dispatch = {
            'organization': lambda: self.organization,
            'organizations': organizations,
            'folder': lambda: self.folder,
            'folders': lambda: self.organization.folders,
            'item': lambda: self.item,
            'items': lambda: self.folder.items,
        }

        return {
            'changed': False,
            'ansible_module_results': _dictize_elements(dispatch[self._target]()),
        }


def _err(msg):
    '''Return a function that raises a BitwardenException.

    Args:
        msg (str): The message to include in the exception.
    '''
    def exception_raiser():
        raise BitwardenException(msg)

    return exception_raiser


def _dictize_elements(obj):
    '''Return a 'dict'-ized version of the inputs.

    Turn an iterable of _Elements into a list of dicts.
    Turn a single _Element into a dict version of the element.
    '''
    if hasattr(obj, '__iter__'):
        return [el.dict for el in obj]

    return obj.dict


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cli_path=dict(type='path', default='bw'),
            organization_name=dict(type='str'),
            organization_id=dict(type='str'),
            folder_name=dict(type='str'),
            folder_id=dict(type='str'),
            item_name=dict(type='str'),
            item_id=dict(type='str'),
            target=dict(type='str', default='item', choices=[
                        'item', 'items', 'folder', 'folders', 'organization', 'organizations']),
        ),
        mutually_exclusive=[
            ('organization_name', 'organization_id'),
            ('folder_name', 'folder_id'),
            ('item_name', 'item_id'),
        ],
        supports_check_mode=True,
    )

    Client.cli_path = module.params.get('cli_path')
    Client.module = module

    module.exit_json(**BitwardenInfo(module).run())


if __name__ == '__main__':
    main()
