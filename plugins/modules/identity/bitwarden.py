#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2022, Jonathan Lung (@lungj) <lungj@heresjono.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: bitwarden
author:
    - Jonathan Lung (@lungj)
requirements:
    - C(bw) Bitwarden command line utility. See U(https://bitwarden.com/help/cli/)
    - Organization names in Bitwarden are unique.
    - Folders in Bitwarden have no duplicate names per organization.
    - The name of items in folders uniquely identifies the items per organization.
notes:
    - Tested with C(bw) version 2022.6.2
short_description: Manipulate items in Bitwarden
description:
    - M(community.general.bitwarden) wraps the C(bw) command line utility to modify Bitwarden-compatible vaults.
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
            - Leave both I(organization_name) and I(organization_id) empty for a wildcard vault.
            - Use I(organization_name='') for personal vaults.
            - Mutually exclusive from I(organization_id).
    organization_id:
        type: str
        description:
            - UID of organization to target.
            - Leave as C(null) for a wildcard vault.
            - Mutually exclusive from I(organization_name).
    folder_name:
        type: str
        description:
            - Name of folder to target.
            - Leave as C(null) for a wildcard folder.
            - Use C('') or C('No Folder') for no folder.
            - Mutually exclusive from I(folder_id).
    folder_id:
        type: str
        description:
            - UID of folder to target.
            - Leave as C(null) for a wildcard folder.
            - Mutually exclusive from I(folder_name).
    item_name:
        type: str
        description:
            - Name of item to target.
            - Mutually exclusive from I(item_id).
    item_id:
        type: str
        description:
            - UID of item to target.
            - Mutually exclusive from I(item_name).
    login:
        type: dict
        description:
            - Mapping of keys to values for C(bw) login details such as C(username) and C(password).
        default: {}
    notes:
        type: str
        description:
            - A note about the item that is stored as metadata about the item.
    target:
        type: str
        description:
            - The type of item being added/modified/removed/queried.
        choices:
            - item
            - folder
        default: 'item'
    state:
        type: str
        description:
            - Action to perform on target.
            - The C(absent) option will remove the target if it exists. This includes non-empty folders.
            - The C(created) option will create the target, if needed, with the fields in I(login) and I(notes).
            - C(created) will not update an existing entry.
            - The C(present) option will create the target, if needed, and update fields in I(login) and I(notes).
        choices:
            - absent
            - created
            - present
        default: 'present'
'''

EXAMPLES = '''
- name: "Ensure a folder exists"
  community.general.bitwarden:
    folder_name: "my_folder"
    target: "folder"
    state: "present"

- name: "Ensure an entry exists in the database"
  community.general.bitwarden:
    folder_name: "my_folder"
    item_name: "some item"
    login:
      username: "a_user"
      password: "some password"
    notes: >-
      Some information about a user is stored here. foo
    target: "item"
    state: "present"
  delegate_to: "localhost"

- name: "Ensure an entry does not exist in the database"
  community.general.bitwarden:
    folder_name: "my_folder"
    item_name: "some item"
    target: "item"
    state: "absent"
  delegate_to: "localhost"

- name: "Create an entry in the database if it does not already exist"
  community.general.bitwarden:
    folder_name: "my_folder"
    item_name: "some item"
    login:
      username: "a_user"
      password: "some password"
    notes: >-
      Some information about a user is stored here. foo
    target: "item"
    state: "created"
  delegate_to: "localhost"
'''

RETURN = '''
---
# A dictionary with the new/queried state.
'''


from collections import defaultdict
import json

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.identity.bitwarden import (
    BitwardenException, Client, Organization
)


class Bitwarden(object):
    '''Accessor for mutating Bitwarden vaults.'''

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

        self._login = module.params.get('login')
        self._notes = module.params.get('notes')

        self._target = module.params.get('target')
        self._state = module.params.get('state')

    def _handle_present_item(self, update=True):
        ret_val = {'changed': False}

        # Determine whether any updates should be made if the item exists.
        do_updates = not self.item.exists or update

        # Get a base version of the item to modify.
        if self.item.exists:
            # Edit an existing item based on its current dict.
            base = self.item.dict
            bw_args = ['edit', 'item', self.item.id]

        else:
            # Create a new item based on the template dict.
            if not self.item.name:
                raise AssertionError('Name not specified')
            base = Client.run_json(['get', 'template', 'item'])
            base['name'] = self.item.name
            base['login'] = {}
            base['organizationId'] = self.organization.id
            base['folderId'] = self.folder.id

            ret_val['changed'] = True

            bw_args = ['create', 'item']

        bw_args += self.organization.bw_filter_args

        if do_updates:
            # Update base `login` key's contents.
            for key, value in self._login.items():
                if key not in base['login'] or base['login'][key] != value:
                    base['login'][key] = value
                    ret_val['changed'] = True

            # Update the base notes section.
            if self._notes is not None:
                if base['notes'] != self._notes:
                    base['notes'] = self._notes
                    ret_val['changed'] = True

        if ret_val['changed']:
            # Encode it using bw.
            out, _stderr = Client.run(['encode'], stdin=json.dumps(base))
            ret_val['ansible_module_results'] = Client.run_json(bw_args, stdin=out)
        else:
            # Return cached value, which should be identical, if no change occured.
            ret_val['ansible_module_results'] = base

        return ret_val

    def _handle_present_folder(self):
        ret_val = {'changed': False}

        if self.folder.exists:
            # A folder with this name already exists; return it.
            ret_val['ansible_module_results'] = self.folder.dict

        else:
            # 'No Folder' is a reserved name in Bitwarden -- we shouldn't create a folder
            # with that name.
            if self.folder.name in (None, '', 'No Folder'):
                raise AssertionError('Illegal folder name used')

            # Fill in a template for a folder object to fill in.
            template = Client.run_json(['get', 'template', 'folder'])
            template['name'] = self.folder.name

            # Encode it using bw.
            out = Client.run(['encode'], stdin=json.dumps(template))[0]

            # Create the folder.
            bw_args = ['create', 'folder'] + self.organization.bw_filter_args
            ret_val['ansible_module_results'] = Client.run_json(bw_args, stdin=out)
            ret_val['changed'] = True

        return ret_val

    def _handle_present(self, update=True):
        # Use a lookup table to determine handler for desired target.
        dispatch = defaultdict(
            _err('Unknown target'),
            organization=_err('Creating organizations not supported'),
            folder=self._handle_present_folder,
            item=lambda: self._handle_present_item(update),
        )

        return dispatch[self._target]()

    def _handle_created(self):
        # Use a lookup table to determine handler for desired target.
        dispatch = defaultdict(
            _err('Unknown target'),
            organization=_err('Creating organizations not supported'),
            folder=self._handle_present_folder,
            item=self._handle_created_item,
        )

        return dispatch[self._target]()

    def _handle_absent(self):
        ret_val = {'changed': False}

        org_args = self.organization.bw_filter_args

        if self._target == 'organization':
            raise BitwardenException('Removing organizations not supported.')

        if self._target in ('folder', 'item'):
            # Dynamically select folder/item.
            element = getattr(self, self._target)
            if element.exists:
                ret_val['ansible_module_results'] = Client.run(['delete', self._target, element.id] + org_args)[0]
                ret_val['changed'] = True
            else:
                ret_val['ansible_module_results'] = ''

        else:
            raise BitwardenException('Unknown target.')

        return ret_val

    def run(self):
        # Use a lookup table to determine handler for desired state.
        dispatch = defaultdict(
            _err('Unknown state'),
            present=self._handle_present,
            created=lambda: self._handle_present(False),
            absent=self._handle_absent,
        )

        return dispatch[self._state]()


def _err(msg):
    '''Return a function that raises a BitwardenException.

    Args:
        msg (str): The message to include in the exception.
    '''
    def exception_raiser():
        raise BitwardenException(msg)

    return exception_raiser


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
            login=dict(type='dict', default={}, no_log=True),
            notes=dict(type='str'),
            target=dict(type='str', default='item', choices=['item', 'folder']),
            state=dict(type='str', default='present', choices=['present', 'absent', 'created']),
        ),
        mutually_exclusive=[
            ('organization_name', 'organization_id'),
            ('folder_name', 'folder_id'),
            ('item_name', 'item_id'),
        ],
        supports_check_mode=False
    )
    Client.cli_path = module.params.get('cli_path')
    Client.module = module

    module.exit_json(**Bitwarden(module).run())


if __name__ == '__main__':
    main()
