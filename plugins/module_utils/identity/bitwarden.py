# -*- coding: utf-8 -*-

# (c) 2022, Jonathan Lung (@lungj) <lungj@heresjono.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.common.text.converters import to_text


class BitwardenException(Exception):
    pass


class Client(object):
    '''A wrapper for for bw command.'''

    # Path to the `bw` executable.
    cli_path = 'bw'
    # AnsibleModule using the client.
    module = None

    @staticmethod
    def run(args, stdin=None, expected_rc=0):
        '''Run the bw client.

        Args:
            args(list): Arguments to pass to the bw CLI client.
            stdin(str): Data to write to the client's stdin.
            expected_rc(int): Expected return code of bw CLI client.

        Return:
            (str, str): The contents of standard out and standard error.
        '''
        rc, out, err = Client.module.run_command([Client.cli_path] + args, data=stdin, binary_data=True)

        if rc != expected_rc:
            raise BitwardenException(err)
        return to_text(out, errors='surrogate_or_strict'), to_text(err, errors='surrogate_or_strict')

    @staticmethod
    def run_json(args, stdin=None, expected_rc=0):
        '''Run the bw client.

        Args:
            args(list): Arguments to pass to the bw CLI client.
            stdin(str): Data to write to the client's stdin.
            expected_rc(int): Expected return code of bw CLI client.

        Return:
            dict: Decoded dictionary object returned by bw CLI client.
        '''
        stdout, _stderr = Client.run(args, stdin, expected_rc)
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
        matches = [Item(dict_=d) for d in Client.run_json(query)
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
    '''A folder in the password database.'''

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
        return [Item(dict_=d) for d in Client.run_json(query) if self.organization.matches(d)]

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
    '''An organization in the password database.'''

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

        matches = [org for org in organizations() if org.dict[attribute] == value]

        if not matches:
            raise KeyError("Organization not found")
        if len(matches) > 1:
            raise AssertionError("Organization not unique")

        return matches[0]

    @property
    def folders(self):
        query = ['list', 'folders'] + self.bw_filter_args

        return [Folder(dict_=d) for d in
                Client.run_json(query)]

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


def organizations():
    return [Organization(dict_=d) for d in Client.run_json(['list', 'organizations'])]


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
