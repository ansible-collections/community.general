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
        required: false
        default: 'bw'
    organization_name:
        type: str
        description:
            - Name of organization to target.
            - Leave as null for a wildcard vault or C('') for personal vaults.
            - Mutually exclusive from organization_id.
        required: false
        default: null
    organization_id:
        type: str
        description:
            - UID of organization to target.
            - Leave as null for a wildcard vault.
            - Mutually exclusive from organization_name.
        required: false
        default: null
    folder_name:
        type: str
        description:
            - Name of folder to target.
            - Leave as null for a wildcard folder.
            - Use C('') or C('No Folder') for no folder.
            - Mutually exclusive from folder_id.
        required: false
        default: null
    folder_id:
        type: str
        description:
            - UID of folder to target.
            - Leave as null for a wildcard folder.
            - Mutually exclusive from folder_name.
        required: false
        default: null
    item_name:
        type: str
        description:
            - Name of item to target.
            - Mutually exclusive from item_id.
        required: false
        default: null
    item_id:
        type: str
        description:
            - UID of item to target.
            - Mutually exclusive from item_name.
        required: false
        default: null
    login:
        type: dict
        description:
            - Mapping of keys to values for bw login details such as C(username) and C(password).
        required: false
        default: {}
    notes:
        type: str
        description:
            - A note about the item that is stored as metadata about the item.
        required: false
        default: null
    target:
        type: str
        description:
            - The type of item being added/modified/removed/queried.
            - For additions/modifications/removal, must be one of C(item) or C(folder).
            - For queries, the above targets are permitted along with
                - C(items),
                - C(folders),
                - C(organization), and
                - C(organizations).
        required: false
        default: 'item'
    state:
        type: str
        description:
            - To modify the target, C(absent) or C(present).
            - To query the state, C(query)
        required: False
        default: 'query'
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
'''

RETURN = '''
---
# A dictionary with the new/queried state.
'''


from collections import defaultdict
import json

from subprocess import Popen, PIPE

from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.basic import AnsibleModule


class BitwardenException(Exception):
    pass


class Client(object):
    '''A wrapper for for bw command.'''

    def __init__(self, cli_path):
        '''
        Args:
            cli_path(Path): Path to the bw executable.
        '''
        self._cli_path = cli_path

    def run(self, args, stdin=None, expected_rc=0):
        '''Run the bw client.

        Args:
            args(list): Arguments to pass to the bw CLI client.
            stdin(str): Data to write to the client's stdin.
            expected_rc(int): Expected return code of bw CLI client.

        Return:
            (str, str): The contents of standard out and standard error.
        '''
        proc = Popen([self._cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = proc.communicate(to_bytes(stdin))
        rc = proc.wait()
        if rc != expected_rc:
            raise BitwardenException(err)
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict')

    def run_json(self, args, stdin=None, expected_rc=0):
        '''Run the bw client.

        Args:
            args(list): Arguments to pass to the bw CLI client.
            stdin(str): Data to write to the client's stdin.
            expected_rc(int): Expected return code of bw CLI client.

        Return:
            dict: Decoded dictionary object returned by bw CLI client.
        '''
        stdout, stderr = self.run(args, stdin, expected_rc)
        return json.loads(stdout)


class _Element(object):
    '''Common elements for items in a Bitwarden vault.'''

    id = property(lambda self: self._id or self.dict['id'])
    name = property(lambda self: self._name or self.dict['name'])

    _dict = None

    @property
    def exists(self):
        # Determine existence by attempting to access the item.
        try:
            obj_dict = self.dict
        except KeyError:
            return False
        # Wildcard objects can return a dict, but their name is None.
        return obj_dict['name'] is not None

    @property
    def dict(self):
        '''Return a dictionary containing the JSON representation of this object.'''
        return self._populated._dict

    @dict.setter
    def dict(self, value):
        '''Populate this object with a dictionary.'''
        self._dict = value
        self._dict_resolve_callback(value)

    def _dict_resolve_callback(self, value):
        '''Callback after self._dict is populated by value.

        Used for filling in any other attributes necessary.
        '''
        pass

    @property
    def _populated(self):
        '''Return self with the side effect of resolving objects from bw.

        Populate self._dict; use cached values, if possible.
        '''
        # Not cached?
        if not self._dict:
            if self._id:
                # Search by id, if id specified.
                val = self._by_attribute('id', self._id).dict
            elif self._name:
                # Search by name, if name specified.
                val = self._by_attribute('name', self._name).dict
            else:
                # Preserve name == ''.
                val = {
                    'id': None,
                    'name': self._name,
                }
            self.dict = val

        return self


class Item(_Element):
    '''An item in the password database.'''

    folder = property(lambda self: self._folder)
    organization = property(lambda self: self._organization)

    def __init__(self, name=None, id_=None, folder=None, organization=None, dict_=None):
        if [name is None, id_ is None, dict_ is None].count(False) > 1:
            raise AssertionError('Cannot specify item in multiple ways')

        if not (name or id_ or dict):
            raise AssertionError('At least one way of specifying an Item is required')

        self._name = name
        self._id = id_
        self._folder = folder
        self._organization = organization

        if dict_:
            self.dict = dict_

    def _by_attribute(self, attribute, value):
        '''Return list of Item objects that match the search parameters.'''

        query = ['list', 'items', '--search', value] + self.organization.bw_filter_args

        # Filter by folder and attribute since `bw` ORs filters together.
        matches = [Item(dict_=d) for d in Bitwarden.client.run_json(query)
                   if self.folder.matches(d) and d[attribute] == value]

        if not matches:
            raise KeyError('Item not found')
        if len(matches) > 1:
            raise AssertionError('Item not unique')

        return matches[0]

    def _dict_resolve_callback(self, value):
        self._organization = Organization(id_=value['organizationId'])
        self._folder = Folder(id_=value['folderId'])


class Folder(_Element):

    organization = property(lambda self: self._organization)

    def __init__(self, name=None, id_=None, organization=None, dict_=None):
        if [name is None, id_ is None, dict_ is None].count(False) > 1:
            raise AssertionError('Cannot specify folder in multiple ways')

        self._name = name
        self._id = id_
        self._organization = organization

        if dict_:
            self.dict = dict_

    def _by_attribute(self, attribute, value):
        '''Return folder dict where the specified attribute
        has the specified value.
        '''
        matches = [folder for folder in self.organization.folders if folder.dict[attribute] == value]

        if not matches:
            raise KeyError("Folder not found")
        if len(matches) > 1:
            raise AssertionError("Folder not unique")

        return matches[0]

    @property
    def items(self):
        query = ['list', 'items']

        # Only restrict by folder if specified.
        if self.name is not None:
            # bw treats 'null' as items not belonging to any folder.
            query.extend(['--folderid', self.id or 'null'])

        # Filter by organization since `bw` ORs filters together.
        return [Item(dict_=d) for d in Bitwarden.client.run_json(query) if self.organization.matches(d)]

    def get_item(self, name=None, id_=None):
        return Item(name, id_, self, self.organization)

    def matches(self, folder):
        '''Return whether folder matches a pattern indicated by self.

        If self.name is None, any folder matches.
        If self.name is '' or 'No Folder', only the null folder is matched.
        All other folders are matched by id.
        '''

        if self.name is None:
            return True

        # No Folder is a special folder name in bw.
        if self.name in ('', 'No Folder'):
            return folder['folderId'] is None

        return self.id == folder['folderId']


class Organization(_Element):

    def __init__(self, name=None, id_=None, dict_=None):
        if [name is None, id_ is None, dict_ is None].count(False) > 1:
            raise AssertionError('Cannot specify organization in multiple ways')

        self._name = name
        self._id = id_

        if dict_:
            self.dict = dict_

    def _by_attribute(self, attribute, value):
        '''Return organization dict where the specified attribute
        has the specified value.
        '''

        matches = [org for org in Bitwarden.organizations() if org.dict[attribute] == value]

        if not matches:
            raise KeyError("Organization not found")
        if len(matches) > 1:
            raise AssertionError("Organization not unique")

        return matches[0]

    @property
    def folders(self):
        query = ['list', 'folders'] + self.bw_filter_args

        return [Folder(dict_=d) for d in
                Bitwarden.client.run_json(query)]

    def get_folder(self, name=None, id_=None):
        return Folder(name, id_, self)

    def matches(self, org):
        '''Return whether org matches a pattern indicated by self.

        If self.name is None, any organization matches.
        If self.name is '', only the null organization is matched.
        All other organizations are matched by id.
        '''

        if self.name is None:
            return True

        if self.name == '':
            return org['organizationId'] is None

        return self.id == org['organizationId']

    @property
    def bw_filter_args(self):
        '''Return bw filter args required to select this organization.

        An Organization with an empty name ('') is treated as requiring no organization.
        An Organization with a null name (None) is treated as allowing any organization.

        Return:
            list: List of strings to pass to bw.
        '''
        if self.name is None:
            return []

        # If name is not None, id will be a UID or None.
        # `bw` uses 'null' instead of None.
        return ['--organizationid', self.id or 'null']


class Bitwarden(object):

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

    @staticmethod
    def organizations():
        return [Organization(dict_=d) for d in Bitwarden.client.run_json(['list', 'organizations'])]

    @classmethod
    def set_client_path(cls, client_path):
        cls.client = Client(client_path)

    def _handle_query(self):
        '''Handle all state="query" requests.'''

        # Use a lookup table to determine how to handle the query.
        dispatch = defaultdict(
            _err('Unknown target'),
            organization=lambda: self.organization,
            organizations=Bitwarden.organizations,
            folder=lambda: self.folder,
            folders=lambda: self.organization.folders,
            item=lambda: self.item,
            items=lambda: self.folder.items,
        )

        return {
            'changed': False,
            'ansible_module_results': _to_dict(dispatch[self._target]()),
        }

    def _handle_present_item(self):
        ret_val = {'changed': False}

        # Get a base version of the item to modify.
        if self.item.exists:
            # Edit an existing item based on its current dict.
            base = self.item.dict
            bw_args = ['edit', 'item', self.item.id]

        else:
            # Create a new item based on the template dict.
            if not self.item.name:
                raise AssertionError('Name not specified')
            base = Bitwarden.client.run_json(['get', 'template', 'item'])
            base['name'] = self.item.name
            base['login'] = {}
            base['organizationId'] = self.organization.id
            base['folderId'] = self.folder.id

            ret_val['changed'] = True

            bw_args = ['create', 'item']

        bw_args += self.organization.bw_filter_args

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
            out, _stderr = Bitwarden.client.run(['encode'], stdin=json.dumps(base))
            ret_val['ansible_module_results'] = Bitwarden.client.run_json(bw_args, stdin=out)
        else:
            # Return cached value, which should be identical, if no change occured.
            ret_val['ansible_module_results'] = base

        return ret_val

    def _handle_present_holder(self):
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
            template = Bitwarden.client.run_json(['get', 'template', 'folder'])
            template['name'] = self.folder.name

            # Encode it using bw.
            out, _stderr = Bitwarden.client.run(['encode'], stdin=json.dumps(template))

            # Create the folder.
            bw_args = ['create', 'folder'] + self.organization.bw_filter_args
            ret_val['ansible_module_results'] = Bitwarden.client.run_json(bw_args, stdin=out)
            ret_val['changed'] = True

        return ret_val

    def _handle_present(self):
        if self._target == 'organization':
            raise BitwardenException('Creating organizations not supported')

        elif self._target == 'folder':
            return self._handle_present_holder()

        elif self._target == 'item':
            return self._handle_present_item()

        else:
            raise BitwardenException('Unknown target')

    def _handle_absent(self):
        ret_val = {'changed': False}

        org_args = self.organization.bw_filter_args

        if self._target == 'organization':
            raise BitwardenException('Removing organizations not supported.')

        elif self._target in ('folder', 'item'):
            # Dynamically select folder/item.
            element = getattr(self, self._target)
            if element.exists:
                ret_val['ansible_module_results'] = Bitwarden.client.run(['delete', self._target, element.id] + org_args)[0]
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
            query=self._handle_query,
            present=self._handle_present,
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


def _to_dict(obj):
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
            login=dict(type='dict', default={}, no_log=True),
            notes=dict(type='str'),
            target=dict(type='str', default='item'),
            state=dict(type='str', default='query'),
        ),
        mutually_exclusive=[
            ('organization_name', 'organization_id'),
            ('folder_name', 'folder_id'),
            ('item_name', 'item_id'),
        ],
        supports_check_mode=False
    )

    Bitwarden.set_client_path(module.params.get('cli_path'))

    module.exit_json(**Bitwarden(module).run())


if __name__ == '__main__':
    main()
