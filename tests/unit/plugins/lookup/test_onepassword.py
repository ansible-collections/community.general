# (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest


from ansible.errors import AnsibleError
from ansible_collections.community.general.plugins.lookup.onepassword import OnePass as OnePassLookupModule
from ansible_collections.community.general.plugins.lookup.onepassword_raw import LookupModule as OnePasswordRawLookup


# Intentionally excludes metadata leaf nodes that would exist in real output if not relevant.
MOCK_ENTRIES = [
    {
        'vault_name': 'Acme "Quot\'d" Servers',
        'queries': [
            '0123456789',
            'Mock "Quot\'d" Server'
        ],
        'output': {
            'uuid': '0123456789',
            'vaultUuid': '2468',
            'overview': {
                'title': 'Mock "Quot\'d" Server'
            },
            'details': {
                'sections': [{
                    'title': '',
                    'fields': [
                        {'t': 'username', 'v': 'jamesbond'},
                        {'t': 'password', 'v': 't0pS3cret'},
                        {'t': 'notes', 'v': 'Test note with\nmultiple lines and trailing space.\n\n'},
                        {'t': 'tricksy "quot\'d" field\\', 'v': '"quot\'d" value'}
                    ]
                }]
            }
        }
    },
    {
        'vault_name': 'Acme Logins',
        'queries': [
            '9876543210',
            'Mock Website',
            'acme.com'
        ],
        'output': {
            'uuid': '9876543210',
            'vaultUuid': '1357',
            'overview': {
                'title': 'Mock Website',
                'URLs': [
                    {'l': 'website', 'u': 'https://acme.com/login'}
                ]
            },
            'details': {
                'sections': [{
                    'title': '',
                    'fields': [
                        {'t': 'password', 'v': 't0pS3cret'}
                    ]
                }]
            }
        }
    },
    {
        'vault_name': 'Acme Logins',
        'queries': [
            '864201357'
        ],
        'output': {
            'uuid': '864201357',
            'vaultUuid': '1357',
            'overview': {
                'title': 'Mock Something'
            },
            'details': {
                'fields': [
                    {
                        'value': 'jbond@mi6.gov.uk',
                        'name': 'emailAddress'
                    },
                    {
                        'name': 'password',
                        'value': 'vauxhall'
                    },
                    {},
                ]
            }
        }
    },
]


@pytest.fixture
def fake_opv1(mocker):
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase.get_current_version", return_value="1.12.42")
    op = OnePassLookupModule(None, None, None, None, None)
    mocker.patch.object(op._cli, "_run")

    return op


@pytest.fixture
def fake_opv2(mocker):
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase.get_current_version", return_value="2.14.7")
    op = OnePassLookupModule(None, None, None, None, None)
    mocker.patch.object(op._cli, "_run")

    return op


def test_op(fake_opv2):
    assert fake_opv2._cli.version == "2.14.7"
