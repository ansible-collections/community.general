# -*- coding: utf-8 -*-

# (c) 2022, Jonathan Lung (@lungj) <lungj@heresjono.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import sys

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, set_module_args

from ansible_collections.community.general.plugins.module_utils.identity.bitwarden import BitwardenException, Client
from ansible_collections.community.general.plugins.modules.identity import bitwarden

# Some objects that will be involved in unit testing. #

# The organizations in the mock vault at start.
ORGANIZATIONS = {
    '9ca': {
        'enabled': True,
        'id': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'name': 'Test',
        'object': 'organization',
        'status': 2,
        'type': 0
    }
}

# The folders in the mock vault at start.
FOLDERS = {
    None: {
        'id': None,
        'name': 'No Folder',
        'object': 'folder'
    },
    '2c8': {
        'id': '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a',
        'name': 'Hellog',
        'object': 'folder'
    },
    '2d0': {
        'id': '2d03899d-d56f-43ed-923d-aee100334387',
        'name': 'my_folder',
        'object': 'folder'
    },
    '3b1': {
        'id': '3b12a9da-7c49-40b8-ad33-aede017a7ead',
        'name': 'x',
        'object': 'folder'
    },
    '6b7': {
        'id': '6b773d8d-bafd-406f-a375-aee10149dd4c',
        'name': 'Folder nameX',
        'object': 'folder'
    }
}

# The items in the mock vault at start.
ITEMS = {
    '08c': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '08ce5bf6-7072-4a2c-bf9c-aee10167a9b6',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T21:49:29.553Z',
        'type': 1
    },
    '3e4': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '3e409a84-06a4-40c3-a35a-aee101750335',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T22:38:05.820Z',
        'type': 1
    },
    '58b': {
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '58bfc8b8-a800-419f-bbdd-aee200387c14',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-30T03:25:39.262Z',
        'type': 1
    },
    '5eb': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '5ebd4d31-104c-49fc-a09c-aedf003d28ad',
        'login': {
            'password': 'b',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a'
        },
        'name': 'dupe_name',
        'notes': None,
        'object': 'item',
        'organizationId': None,
        'reprompt': 0,
        'revisionDate': '2022-07-27T03:42:40.353Z',
        'type': 1
    },
    '634': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '63483ea8-0df3-4ef8-a37a-aee1016883de',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T21:52:54.163Z',
        'type': 1
    },
    '650': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': '2d03899d-d56f-43ed-923d-aee100334387',
        'id': '650e8fe4-0221-48da-ad99-aee100345d3b',
        'login': {
            'password': 'folder_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'folder_account'
        },
        'name': 'my_account',
        'notes': None,
        'object': 'item',
        'organizationId': None,
        'reprompt': 0,
        'revisionDate': '2022-07-29T03:10:39.123Z',
        'type': 1
    },
    '7b1': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '7b182421-cedd-4f1f-8759-aee1016e4f22',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T22:13:41.433Z',
        'type': 1
    },
    '7fa': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '7fa5c935-8f5c-4c50-ae54-aee101727af0',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T22:28:52.626Z',
        'type': 1
    },
    '8d1': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': '8d13ce86-408a-4a79-af7d-aee10170ebc0',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T22:23:11.986Z',
        'type': 1
    },
    '909': {
        'collectionIds': [],
        'deletedDate':
        None,
        'favorite':
        False,
        'fields': [{
            'linkedId': None,
            'name': 'a_new_secret',
            'type': 1,
            'value': 'this is a new secret'
        }, {
            'linkedId': None,
            'name': 'not so secret',
            'type': 0,
            'value': 'not secret'
        }],
        'folderId':
        '3b12a9da-7c49-40b8-ad33-aede017a7ead',
        'id':
        '90992f63-ddb6-4e76-8bfc-aede016ca5eb',
        'login': {
            'password': 'passwordA3',
            'passwordRevisionDate': '2022-07-26T23:03:23.399Z',
            'totp': None,
            'username': 'userA'
        },
        'name':
        'a_test',
        'notes':
        None,
        'object':
        'item',
        'organizationId':
        None,
        'passwordHistory': [{
            'lastUsedDate': '2022-07-26T23:03:23.405Z',
            'password': 'a_new_secret: this is secret'
        }, {
            'lastUsedDate': '2022-07-26T23:03:23.399Z',
            'password': 'passwordA2'
        }, {
            'lastUsedDate': '2022-07-26T22:59:52.885Z',
            'password': 'passwordA'
        }],
        'reprompt':
        0,
        'revisionDate':
        '2022-07-26T23:03:23.743Z',
        'type':
        1
    },
    'ac4': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'ac4ccf79-4608-4223-8eb0-aee101713eb6',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T22:24:22.780Z',
        'type': 1
    },
    'd2f': {
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'd2ffbf89-35db-4957-8803-aee20036fe16',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-30T03:20:13.295Z',
        'type': 1
    },
    'd3c': {
        'collectionIds': ['a9f66b9c-2844-4fad-af46-aee001714d6e'],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'd3c2a670-3779-4510-b45f-aee00171fc0c',
        'login': {
            'password': 'bar',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'foo'
        },
        'name': 'X',
        'notes': None,
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-28T22:27:04.353Z',
        'type': 1
    },
    'd69': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'd69f2677-68b4-4742-82f0-aee10167e92f',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item2',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-29T21:50:23.720Z',
        'type': 1
    },
    'dcb': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'dcb52254-1837-41a1-bd83-aee10033fc1e',
        'login': {
            'password': 'password1',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'account'
        },
        'name': 'my_account',
        'notes': None,
        'object': 'item',
        'organizationId': None,
        'reprompt': 0,
        'revisionDate': '2022-07-29T03:10:14.360Z',
        'type': 1
    },
    'e51': {
        'deletedDate': None,
        'favorite': False,
        'folderId': '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a',
        'id': 'e5148226-34b3-4bad-bc37-aee20038d49c',
        'login': {
            'password': 'some new_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'a_user'
        },
        'name': 'some item',
        'notes': 'Some information about a user is stored here. foo',
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-30T03:27:21.464Z',
        'type': 1
    },
    'ed4': {
        'collectionIds': [],
        'deletedDate': None,
        'favorite': False,
        'folderId': None,
        'id': 'ed401970-a191-4875-bb1a-aee20022cd85',
        'login': {
            'password': 'org_password',
            'passwordRevisionDate': None,
            'totp': None,
            'username': 'org_account'
        },
        'name': 'my_account',
        'notes': None,
        'object': 'item',
        'organizationId': '9caf72f5-55ad-4a15-b923-aee001714d67',
        'reprompt': 0,
        'revisionDate': '2022-07-30T03:02:12.517Z',
        'type': 1
    },
    'f12': {
        'collectionIds': ['a9f66b9c-2844-4fad-af46-aee001714d6e'],
        'deletedDate':
        None,
        'favorite':
        False,
        'folderId':
        '2d03899d-d56f-43ed-923d-aee100334387',
        'id':
        'f1214c58-5a3b-4134-95a1-aee100338c8f',
        'login': {
            'password': 'org_folder_password',
            'passwordRevisionDate': '2022-07-29T03:08:23.375Z',
            'totp': None,
            'username': 'org_folder_account'
        },
        'name':
        'my_account',
        'notes':
        None,
        'object':
        'item',
        'organizationId':
        '9caf72f5-55ad-4a15-b923-aee001714d67',
        'passwordHistory': [{
            'lastUsedDate': '2022-07-29T03:08:23.375Z',
            'password': 'folder_password'
        }, {
            'lastUsedDate': '2022-07-29T03:08:07.089Z',
            'password': 'org_folder_password'
        }],
        'reprompt':
        0,
        'revisionDate':
        '2022-07-29T03:08:25.523Z',
        'type':
        1
    }
}

# A newly created folder.
NEW_FOLDER = {
    'id': '5aff3ed1-80a6-40b5-91c0-aee2006844aa',
    'name': 'new folder name',
    'object': 'folder'
}

# A newly created item.
NEW_ITEM = {
    'deletedDate': None,
    'favorite': False,
    'folderId': None,
    'id': '71b9e080-3cb2-4d01-9652-aee2006c9f70',
    'login': {
        'password': 'new password',
        'passwordRevisionDate': None,
        'totp': None,
        'username': 'new username'
    },
    'name': 'a new item',
    'notes': 'test note',
    'object': 'item',
    'organizationId': None,
    'reprompt': 0,
    'revisionDate': '2022-07-30T06:35:29.008Z',
    'type': 1
}

# A mock response from bw after modifying a username.
MODIFIED_DCB_USERNAME = {
    'collectionIds': [],
    'deletedDate': None,
    'favorite': False,
    'folderId': None,
    'id': 'dcb52254-1837-41a1-bd83-aee10033fc1e',
    'login': {
        'password': 'password1',
        'passwordRevisionDate': None,
        'totp': None,
        'username': 'account_x'
    },
    'name': 'my_account',
    'notes': None,
    'object': 'item',
    'organizationId': None,
    'reprompt': 0,
    'revisionDate': '2022-07-30T16:43:13.720Z',
    'type': 1
}

# A mock response from bw after modifying notes.
MODIFIED_DCB_NOTES = {
    'collectionIds': [],
    'deletedDate': None,
    'favorite': False,
    'folderId': None,
    'id': 'dcb52254-1837-41a1-bd83-aee10033fc1e',
    'login': {
        'password': 'password1',
        'passwordRevisionDate': None,
        'totp': None,
        'username': 'account'
    },
    'name': 'my_account',
    'notes': 'can you hear me now?',
    'object': 'item',
    'organizationId': None,
    'reprompt': 0,
    'revisionDate': '2022-07-30T16:47:22.604Z',
    'type': 1
}

# bw's folder template.
FOLDER_TEMPLATE = {'name': 'Folder name'}

# bw's item template.
ITEM_TEMPLATE = {
    'card': None,
    'collectionIds': None,
    'favorite': False,
    'fields': [],
    'folderId': None,
    'identity': None,
    'login': None,
    'name': 'Item name',
    'notes': 'Some notes about this item.',
    'organizationId': None,
    'reprompt': 0,
    'secureNote': None,
    'type': 1
}

# Mapping of arguments (as a tuple) and stdin data to responses.
# Responses are a dict with the possible keys:
#   response: JSON stringify-able object or str returned by bw on stdout.
#             Lists are automatically sorted using the `_id_key` function.
#   rc: Integer exit code from bw subprocess. Default 0.
#   stderr: str of output from stderr. Default ''.
#   json: bool of whether response should be JSON stringified before returning.
MOCK_RESPONSES = {
    (('list', 'organizations'), None): {
        'response': list(ORGANIZATIONS.values()),
    },
    (('list', 'folders'), None): {
        'response': list(FOLDERS.values()),
    },
    (('list', 'items'), None): {
        'response': list(ITEMS.values()),
    },
    (('list', 'items', '--search', 'a_test'), None): {
        'response': [ITEMS['909']],
    },
    (('list', 'items', '--search', 'some item'), None): {
        'response': [
            item for item in ITEMS.values()
            if any(val for val in item.values()
                   if isinstance(val, str) and 'some item' in val)
        ],
    },
    (('list', 'items', '--search', 'e5148226-34b3-4bad-bc37-aee20038d49c'), None):
    {
        'response': [ITEMS['e51']]
    },
    (('list', 'items', '--search', 'some item2'), None): {
        'response': [
            item for item in ITEMS.values()
            if any(val for val in item.values()
                   if isinstance(val, str) and 'some item2' in val)
        ],
    },
    (('list', 'items', '--folderid', '3b12a9da-7c49-40b8-ad33-aede017a7ead'), None):
    {
        'response': [ITEMS['909']],
    },
    (('list', 'items', '--folderid', '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a'), None):
    {
        'response': [ITEMS['e51']]
    },
    (('list', 'items', '--folderid', 'null'), None): {
        'response':
        [item for item in ITEMS.values() if item['folderId'] is None],
    },
    (('list', 'items', '--search', 'my_account'), None): {
        'response': [
            item for item in ITEMS.values()
            if any(val for val in item.values()
                   if isinstance(val, str) and 'my_account' in val)
        ],
    },
    (('list', 'folders', '--organizationid', 'null'), None): {
        'response':
        [FOLDERS[None], FOLDERS['2c8'], FOLDERS['2d0'], FOLDERS['3b1']],
    },
    (('list', 'folders', '--organizationid', '9caf72f5-55ad-4a15-b923-aee001714d67'), None):
    {
        'response':
        [FOLDERS[None], FOLDERS['2c8'], FOLDERS['2d0'], FOLDERS['3b1']],
    },
    (('get', 'template', 'folder'), None): {
        'response': FOLDER_TEMPLATE,
    },
    (('encode', ), '{"name": "new folder name"}'): {
        'response': 'eyJuYW1lIjogIm5ldyBmb2xkZXIgbmFtZSJ9Cg==',
        'json': False,
    },
    (('create', 'folder'), 'eyJuYW1lIjogIm5ldyBmb2xkZXIgbmFtZSJ9Cg=='): {
        'response': NEW_FOLDER,
    },
    (('get', 'template', 'item'), None): {
        'response': ITEM_TEMPLATE,
    },
    (('encode', ), '{"card": null, "collectionIds": null, "favorite": false, "fields": [], '
     '"folderId": null, "identity": null, '
     '"login": {"password": "new password", "username": "new username"}, '
     '"name": "a new item", "notes": "test note", "organizationId": null, '
     '"reprompt": 0, "secureNote": null, "type": 1}'): {
        'response':
        'eyJjYXJkIjogbnVsbCwgImNvbGxlY3Rpb25JZHMiOiBudWxsLCAiZmF2b3Jp'
        'dGUiOiBmYWxzZSwgImZpZWxkcyI6IFtdLCAiZm9sZGVySWQiOiBudWxsLCAi'
        'aWRlbnRpdHkiOiBudWxsLCAibG9naW4iOiB7InVzZXJuYW1lIjogIm5ldyB1'
        'c2VybmFtZSIsICJwYXNzd29yZCI6ICJuZXcgcGFzc3dvcmQifSwgIm5hbWUi'
        'OiAiYSBuZXcgaXRlbSIsICJub3RlcyI6ICJ0ZXN0IG5vdGUiLCAib3JnYW5p'
        'emF0aW9uSWQiOiBudWxsLCAicmVwcm9tcHQiOiAwLCAic2VjdXJlTm90ZSI6'
        'IG51bGwsICJ0eXBlIjogMX0K',
        'json':
        False,
    },
    (('create', 'item'), 'eyJjYXJkIjogbnVsbCwgImNvbGxlY3Rpb25JZHMiOiBudWxsLCAiZmF2b3JpdGUiOiBmYWxzZSwgImZ'
     'pZWxkcyI6IFtdLCAiZm9sZGVySWQiOiBudWxsLCAiaWRlbnRpdHkiOiBudWxsLCAibG9naW4iOiB7In'
     'VzZXJuYW1lIjogIm5ldyB1c2VybmFtZSIsICJwYXNzd29yZCI6ICJuZXcgcGFzc3dvcmQifSwgIm5hb'
     'WUiOiAiYSBuZXcgaXRlbSIsICJub3RlcyI6ICJ0ZXN0IG5vdGUiLCAib3JnYW5pemF0aW9uSWQiOiBu'
     'dWxsLCAicmVwcm9tcHQiOiAwLCAic2VjdXJlTm90ZSI6IG51bGwsICJ0eXBlIjogMX0K'): {
        'response': NEW_ITEM,
    },
    (('encode', ), '{"card": null, "collectionIds": null, "favorite": false, "fields": [], '
     '"folderId": null, "identity": null, "login": {}, "name": "my_account", '
     '"notes": "Some notes about this item.", "organizationId": null, "reprompt": 0, '
     '"secureNote": null, "type": 1}'): {
        'response':
        'eyJjYXJkIjogbnVsbCwgImNvbGxlY3Rpb25JZHMiOiBudWxsLCAiZmF2b3Jp'
        'dGUiOiBmYWxzZSwgImZpZWxkcyI6IFtdLCAiZm9sZGVySWQiOiBudWxsLCAi'
        'aWRlbnRpdHkiOiBudWxsLCAibG9naW4iOiB7fSwgIm5hbWUiOiAibXlfYWNj'
        'b3VudCIsICJub3RlcyI6ICJTb21lIG5vdGVzIGFib3V0IHRoaXMgaXRlbS4i'
        'LCAib3JnYW5pemF0aW9uSWQiOiBudWxsLCAicmVwcm9tcHQiOiAwLCAic2Vj'
        'dXJlTm90ZSI6IG51bGwsICJ0eXBlIjogMX0K',
        'json':
        False,
    },
    (('list', 'items', '--search', 'a new item'), None): {
        'response': [],
    },
    (('list', 'items', '--search', 'my_account', '--organizationid', 'null'), None):
    {
        'response': [ITEMS['650'], ITEMS['dcb']],
    },
    (('encode', ), '{"collectionIds": [], "deletedDate": null, "favorite": false, '
     '"folderId": null, "id": "dcb52254-1837-41a1-bd83-aee10033fc1e", '
     '"login": {"password": "password1", "passwordRevisionDate": null, '
     '"totp": null, "username": "account"}, "name": "my_account", '
     '"notes": null, "object": "item", "organizationId": null, '
     '"reprompt": 0, "revisionDate": "2022-07-29T03:10:14.360Z", "type": 1}'):
    {
        'response':
        'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJm'
        'YXZvcml0ZSI6IGZhbHNlLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNi'
        'NTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMzNmYzFlIiwgImxvZ2luIjog'
        'eyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvbkRh'
        'dGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50'
        'In0sICJuYW1lIjogIm15X2FjY291bnQiLCAibm90ZXMiOiBudWxsLCAib2Jq'
        'ZWN0IjogIml0ZW0iLCAib3JnYW5pemF0aW9uSWQiOiBudWxsLCAicmVwcm9t'
        'cHQiOiAwLCAicmV2aXNpb25EYXRlIjogIjIwMjItMDctMjlUMDM6MTA6MTQu'
        'MzYwWiIsICJ0eXBlIjogMX0K',
        'json':
        False,
    },
    (('edit', 'item', 'dcb52254-1837-41a1-bd83-aee10033fc1e', '--organizationid', 'null'),
     'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJmYXZvcml0ZSI6IGZhbHN'
     'lLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNiNTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMz'
     'NmYzFlIiwgImxvZ2luIjogeyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvb'
     'kRhdGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50In0sICJuYW1lIjog'
     'Im15X2FjY291bnQiLCAibm90ZXMiOiBudWxsLCAib2JqZWN0IjogIml0ZW0iLCAib3JnYW5pemF0aW9'
     'uSWQiOiBudWxsLCAicmVwcm9tcHQiOiAwLCAicmV2aXNpb25EYXRlIjogIjIwMjItMDctMjlUMDM6MT'
     'A6MTQuMzYwWiIsICJ0eXBlIjogMX0K'): {
        'response': ITEMS['dcb'],
    },
    (('encode', ), '{"collectionIds": [], "deletedDate": null, "favorite": false, "folderId": null, '
     '"id": "dcb52254-1837-41a1-bd83-aee10033fc1e", "login": {"password": "password1", '
     '"passwordRevisionDate": null, "totp": null, "username": "account_x"}, '
     '"name": "my_account", "notes": null, "object": "item", "organizationId": null, '
     '"reprompt": 0, "revisionDate": "2022-07-29T03:10:14.360Z", "type": 1}'):
    {
        'response':
        'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJm'
        'YXZvcml0ZSI6IGZhbHNlLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNi'
        'NTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMzNmYzFlIiwgImxvZ2luIjog'
        'eyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvbkRh'
        'dGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50'
        'X3gifSwgIm5hbWUiOiAibXlfYWNjb3VudCIsICJub3RlcyI6IG51bGwsICJv'
        'YmplY3QiOiAiaXRlbSIsICJvcmdhbml6YXRpb25JZCI6IG51bGwsICJyZXBy'
        'b21wdCI6IDAsICJyZXZpc2lvbkRhdGUiOiAiMjAyMi0wNy0yOVQwMzoxMDox'
        'NC4zNjBaIiwgInR5cGUiOiAxfQo=',
        'json':
        False,
    },
    (('edit', 'item', 'dcb52254-1837-41a1-bd83-aee10033fc1e', '--organizationid', 'null'),
     'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJmYXZvcml0ZSI6IGZhbHN'
     'lLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNiNTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMz'
     'NmYzFlIiwgImxvZ2luIjogeyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvb'
     'kRhdGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50X3gifSwgIm5hbWUi'
     'OiAibXlfYWNjb3VudCIsICJub3RlcyI6IG51bGwsICJvYmplY3QiOiAiaXRlbSIsICJvcmdhbml6YXR'
     'pb25JZCI6IG51bGwsICJyZXByb21wdCI6IDAsICJyZXZpc2lvbkRhdGUiOiAiMjAyMi0wNy0yOVQwMz'
     'oxMDoxNC4zNjBaIiwgInR5cGUiOiAxfQo='): {
        'response': MODIFIED_DCB_USERNAME,
    },
    (('encode', ), '{"collectionIds": [], "deletedDate": null, "favorite": false, "folderId": null, '
     '"id": "dcb52254-1837-41a1-bd83-aee10033fc1e", "login": {"password": "password1", '
     '"passwordRevisionDate": null, "totp": null, "username": "account"}, '
     '"name": "my_account", "notes": "can you hear me now?", "object": "item", '
     '"organizationId": null, "reprompt": 0, "revisionDate": "2022-07-29T03:10:14.360Z", '
     '"type": 1}'): {
        'response':
        'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJm'
        'YXZvcml0ZSI6IGZhbHNlLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNi'
        'NTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMzNmYzFlIiwgImxvZ2luIjog'
        'eyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvbkRh'
        'dGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50'
        'In0sICJuYW1lIjogIm15X2FjY291bnQiLCAibm90ZXMiOiAiY2FuIHlvdSBo'
        'ZWFyIG1lIG5vdz8iLCAib2JqZWN0IjogIml0ZW0iLCAib3JnYW5pemF0aW9u'
        'SWQiOiBudWxsLCAicmVwcm9tcHQiOiAwLCAicmV2aXNpb25EYXRlIjogIjIw'
        'MjItMDctMjlUMDM6MTA6MTQuMzYwWiIsICJ0eXBlIjogMX0K',
        'json':
        False,
    },
    (('edit', 'item', 'dcb52254-1837-41a1-bd83-aee10033fc1e', '--organizationid', 'null'),
     'eyJjb2xsZWN0aW9uSWRzIjogW10sICJkZWxldGVkRGF0ZSI6IG51bGwsICJmYXZvcml0ZSI6IGZhbHN'
     'lLCAiZm9sZGVySWQiOiBudWxsLCAiaWQiOiAiZGNiNTIyNTQtMTgzNy00MWExLWJkODMtYWVlMTAwMzN'
     'mYzFlIiwgImxvZ2luIjogeyJwYXNzd29yZCI6ICJwYXNzd29yZDEiLCAicGFzc3dvcmRSZXZpc2lvbkR'
     'hdGUiOiBudWxsLCAidG90cCI6IG51bGwsICJ1c2VybmFtZSI6ICJhY2NvdW50In0sICJuYW1lIjogIm1'
     '5X2FjY291bnQiLCAibm90ZXMiOiAiY2FuIHlvdSBoZWFyIG1lIG5vdz8iLCAib2JqZWN0IjogIml0ZW0'
     'iLCAib3JnYW5pemF0aW9uSWQiOiBudWxsLCAicmVwcm9tcHQiOiAwLCAicmV2aXNpb25EYXRlIjogIjI'
     'wMjItMDctMjlUMDM6MTA6MTQuMzYwWiIsICJ0eXBlIjogMX0K'): {
        'response': MODIFIED_DCB_NOTES,
    },
    (('delete', 'folder', '6b773d8d-bafd-406f-a375-aee10149dd4c'), None): {
        'response': '',
        'json': False,
    },
    (('delete', 'folder', '2c8a747e-6f0b-4cc8-a98f-aee20038cc9a'), None): {
        'response': '',
        'json': False,
    },
    (('delete', 'item', 'e5148226-34b3-4bad-bc37-aee20038d49c'), None): {
        'response': '',
        'json': False,
    },
    (('list', 'items', '--search', 'my_account', '--organizationid', '9caf72f5-55ad-4a15-b923-aee001714d67'), None):
    {
        'response': [ITEMS['ed4'], ITEMS['f12']],
    },
    (('delete', 'item', 'ed401970-a191-4875-bb1a-aee20022cd85', '--organizationid', '9caf72f5-55ad-4a15-b923-aee001714d67'), None):
    {
        'response': '',
        'json': False,
    },
}


def py26_workaround(fn):
    '''Workaround for Python 2.6 test issues.

    Python 2.6's json encoder/decoder is non-deterministic and doesn't support the sort_keys
    option. We get as far as we can in the relevant tests and then assume everything else
    is okay.

    Decoding and re-encoding a dict doesn't necessarily create the same JSON object, even if
    the dict has identical contents.

    This non-deterministic behaviour makes it challenging to look up responses from the
    mocked bw client.
    '''
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        # Non-deterministic JSON encodings manifests itself as an inability to look up responses;
        # this results in a KeyError being raised.
        except KeyError:
            pass

    # The version_info tuple is unnamed in older Pythons;
    # index 0 is the major version and index 1 is the minor version.
    if sys.version_info[:2] < (2, 7):
        return wrapped
    return fn


class _MockJson(object):
    '''Mock json module that automatically sorts keys in Python 2.7 or higher.'''
    def __getattr__(self, attr):
        return getattr(json, attr)

    def dumps(self, data, *args, **kwargs):
        '''Wrapper for json.dumps with sort_keys enabled in Python >= 2.7.'''
        if sys.version_info[:2] < (2, 7):
            return json.dumps(data)

        # Assumes positional argument for sort_keys is not used.
        if 'sort_keys' not in kwargs:
            kwargs['sort_keys'] = True

        return json.dumps(data, *args, **kwargs)


def client(responses):
    '''Return a MockClient that uses the lookup table in responses.'''
    MockClient.responses = responses
    return MockClient.run_command


def mock():
    # Mock exit_json
    def exit_json(*_args, **kwargs):
        if 'changed' not in kwargs:
            kwargs['changed'] = False
        raise AnsibleExitJson(kwargs)

    def fail_json(*_args, **kwargs):
        if 'changed' not in kwargs:
            kwargs['changed'] = False
        raise AnsibleFailJson(kwargs)

    bitwarden.AnsibleModule.exit_json = exit_json
    bitwarden.AnsibleModule.fail_json = fail_json


class MockClient(Client):
    '''Mock of a bw client that gets responses using a lookup table.'''
    command_history = []
    responses = {}

    @staticmethod
    def run_command(module, args, data=None, binary_data=True, check_rc=False):
        MockClient.command_history.append(args)
        # Strip off argument 0, `bw`.
        result = MOCK_RESPONSES[tuple(args[1:]), data]

        def _id_key(val):
            return val['id'] or '0'

        # Put the output in a standard order if it is a list.
        stdout_obj = result.get('response', '')
        if isinstance(stdout_obj, list):
            stdout_obj = sorted(stdout_obj, key=_id_key)

        if result.get('json', True):
            stdout_obj = json.dumps(stdout_obj)

        if result.get('rc', 0):
            raise NotImplementedError('No simulation of non-zero rc')

        # Mocking using Python-generated json for clearer code.
        return result.get('rc', 0), stdout_obj, result.get('stderr', '')

    @staticmethod
    def number_of_edits():
        '''Return True iff a command in the command history edited the vault.'''
        mod_commands = ('create', 'edit', 'delete')

        # args[1] is the main command passed into `bw`.
        return [args[1] in mod_commands
                for args in MockClient.command_history].count(True)


@patch(
    'ansible_collections.community.general.plugins.modules.identity.bitwarden.json',
    new=_MockJson())
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenPresentFolder(unittest.TestCase):
    '''Test "present" idempotent behaviour for folders.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    def test_create_nonexistent(self):
        '''Test ensuring a folder exists that did not previously exist.'''
        set_module_args({
            'target': 'folder',
            'state': 'present',
            'folder_name': 'new folder name',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': NEW_FOLDER
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    def test_create_existent(self):
        '''Test ensuring a folder exists that previously existed.'''
        set_module_args({
            'target': 'folder',
            'state': 'present',
            'folder_name': 'Hellog',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': FOLDERS['2c8']
        })
        self.assertFalse(MockClient.number_of_edits())


@patch(
    'ansible_collections.community.general.plugins.modules.identity.bitwarden.json',
    new=_MockJson())
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenCreatedFolder(unittest.TestCase):
    '''Test "present" idempotent behaviour for folders.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    def test_create_nonexistent(self):
        '''Test ensuring a folder exists that did not previously exist.'''
        set_module_args({
            'target': 'folder',
            'state': 'created',
            'folder_name': 'new folder name',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': NEW_FOLDER
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    def test_create_existent(self):
        '''Test ensuring a folder exists that previously existed.'''
        set_module_args({
            'target': 'folder',
            'state': 'created',
            'folder_name': 'Hellog',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': FOLDERS['2c8']
        })
        self.assertFalse(MockClient.number_of_edits())


@patch(
    'ansible_collections.community.general.plugins.modules.identity.bitwarden.json',
    new=_MockJson())
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenPresentItem(unittest.TestCase):
    '''Test "present" idempotent behaviour for items.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    @py26_workaround
    def test_create_nonexistent(self):
        '''Test ensuring an item exists that did not previously exist.'''
        set_module_args({
            'target': 'item',
            'state': 'present',
            'item_name': 'a new item',
            'login': {
                'username': 'new username',
                'password': 'new password',
            },
            'notes': 'test note',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': NEW_ITEM
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    @py26_workaround
    def test_create_existent_no_data(self):
        '''Test ensuring an item exists that already existed -- but without specifying any
        extra data that might lead to a modification.'''
        set_module_args({
            'target': 'item',
            'state': 'present',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())

    def test_create_existent_no_changed_data(self):
        '''Test ensuring an item exists that already existed and trying to set its data
        to something its old value.'''
        set_module_args({
            'target': 'item',
            'state': 'present',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'login': {
                'username': 'account',
            }
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())

    @py26_workaround
    def test_create_existent_changed_data(self):
        '''Test ensuring an item exists that already existed and trying to set its data
        to a new value.'''
        set_module_args({
            'target': 'item',
            'state': 'present',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'login': {
                'username': 'account_x',
            }
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': MODIFIED_DCB_USERNAME
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    @py26_workaround
    def test_create_existent_changed_notes(self):
        '''Test ensuring an item exists that already existed and trying to set its notes
        to a new value.'''
        set_module_args({
            'target': 'item',
            'state': 'present',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'notes': 'can you hear me now?'
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': MODIFIED_DCB_NOTES
        })
        self.assertEqual(MockClient.number_of_edits(), 1)


@patch(
    'ansible_collections.community.general.plugins.modules.identity.bitwarden.json',
    new=_MockJson())
@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenCreatedItem(unittest.TestCase):
    '''Test "created" behaviour for items.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    @py26_workaround
    def test_create_nonexistent(self):
        '''Test ensuring an item exists that did not previously exist.'''
        set_module_args({
            'target': 'item',
            'state': 'created',
            'item_name': 'a new item',
            'login': {
                'username': 'new username',
                'password': 'new password',
            },
            'notes': 'test note',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': NEW_ITEM
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    @py26_workaround
    def test_create_existent_no_data(self):
        '''Test ensuring an item exists that already existed -- but without specifying any
        extra data that might lead to a modification.'''
        set_module_args({
            'target': 'item',
            'state': 'created',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())

    def test_create_existent_no_changed_data(self):
        '''Test ensuring an item exists that already existed and trying to set its data
        to something its old value.'''
        set_module_args({
            'target': 'item',
            'state': 'created',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'login': {
                'username': 'account',
            }
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())

    @py26_workaround
    def test_create_existent_changed_data(self):
        '''Test ensuring an item exists that already existed and trying to set its data
        to a new value.'''
        set_module_args({
            'target': 'item',
            'state': 'created',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'login': {
                'username': 'account_x',
            }
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())

    @py26_workaround
    def test_create_existent_changed_notes(self):
        '''Test ensuring an item exists that already existed and trying to set its notes
        to a new value.'''
        set_module_args({
            'target': 'item',
            'state': 'created',
            'folder_name': '',
            'organization_name': '',
            'item_name': 'my_account',
            'notes': 'can you hear me now?'
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ITEMS['dcb']
        })
        self.assertFalse(MockClient.number_of_edits())


@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenAbsentFolder(unittest.TestCase):
    '''Test "absent" idempotent behaviour for folders.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    def test_delete_nonexistent(self):
        '''Test ensuring a previously non-existent folder does not exist.'''
        set_module_args({
            'target': 'folder',
            'state': 'absent',
            'folder_name': 'this does not exist',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ''
        })
        self.assertFalse(MockClient.number_of_edits())

    def test_delete_existent_empty(self):
        '''Test ensuring a previously existent folder does not exist. The folder contains
        items.'''
        set_module_args({
            'target': 'folder',
            'state': 'absent',
            'folder_name': 'Folder nameX',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': ''
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    def test_delete_existent_nonempty(self):
        '''Test ensuring a previously existent folder does not exist. The folder contains
        no items.'''
        set_module_args({
            'target': 'folder',
            'state': 'absent',
            'folder_name': 'Hellog',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': ''
        })
        self.assertEqual(MockClient.number_of_edits(), 1)


@patch(
    'ansible.module_utils.basic.AnsibleModule.run_command',
    new=client(MOCK_RESPONSES))
class TestBitwardenAbsentItem(unittest.TestCase):
    '''Test "absent" idempotent behaviour for items.'''
    def setUp(self):
        mock()
        self.module = bitwarden
        MockClient.command_history = []

    def test_absent_nonexistent(self):
        '''Test ensuring a non-existent item continues to not exist.'''
        set_module_args({
            'target': 'item',
            'state': 'absent',
            'item_name': 'this does not exist',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': False,
            'ansible_module_results': ''
        })
        self.assertFalse(MockClient.number_of_edits())

    def test_absent_unique(self):
        '''Test ensuring a uniquely named item does not exist.'''
        set_module_args({
            'target': 'item',
            'state': 'absent',
            'item_name': 'some item',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': ''
        })
        self.assertEqual(MockClient.number_of_edits(), 1)

    def test_absent_name_in_multiple_folders(self):
        '''Test ensuring a non-uniquely specified item does not exist.'''
        set_module_args({
            'target': 'item',
            'state': 'absent',
            'item_name': 'some item2',
        })
        with self.assertRaises(BitwardenException):
            self.module.main()
        self.assertFalse(MockClient.number_of_edits())

    def test_absent_using_unique_folder_org(self):
        '''Test ensuring an item that requires matching folder and organization to
        properly remove it.'''
        set_module_args({
            'target': 'item',
            'state': 'absent',
            'folder_name': '',
            'organization_name': 'Test',
            'item_name': 'my_account',
        })
        with self.assertRaises(AnsibleExitJson) as ansible_exit_json:
            self.module.main()
        self.assertEqual(ansible_exit_json.exception.args[0], {
            'changed': True,
            'ansible_module_results': ''
        })
        self.assertEqual(MockClient.number_of_edits(), 1)


if __name__ == '__main__':
    unittest.main()
