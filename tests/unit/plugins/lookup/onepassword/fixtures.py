# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePassCLIv1,
    OnePassCLIv2,
)
# Intentionally excludes metadata leaf nodes that would exist in real output if not relevant.
MOCK_ENTRIES = {
    OnePassCLIv1: [
        {
            'vault_name': 'Acme "Quot\'d" Servers',
            'queries': [
                '0123456789',
                'Mock "Quot\'d" Server'
            ],
            'expected': ['t0pS3cret', 't0pS3cret'],
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
            'expected': ['t0pS3cret', 't0pS3cret', 't0pS3cret'],
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
            'expected': ['vauxhall'],
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
    ],
    OnePassCLIv2: [
        {
            "vault_name": "Test Vault",
            "queries": [
                "ywvdbojsguzgrgnokmcxtydgdv",
                "Authy Backup",
            ],
            "expected": ["OctoberPoppyNuttyDraperySabbath", "OctoberPoppyNuttyDraperySabbath"],
            "output": {
                "id": "ywvdbojsguzgrgnokmcxtydgdv",
                "title": "Authy Backup",
                "version": 1,
                "vault": {
                    "id": "bcqxysvcnejjrwzoqrwzcqjqxc",
                    "name": "test vault"
                },
                "category": "PASSWORD",
                "last_edited_by": "7FUPZ8ZNE02KSHMAIMKHIVUE17",
                "created_at": "2015-01-18T13:13:38Z",
                "updated_at": "2016-02-20T16:23:54Z",
                "additional_information": "Jan 18, 2015, 08:13:38",
                "fields": [
                    {
                        "id": "password",
                        "type": "CONCEALED",
                        "purpose": "PASSWORD",
                        "label": "password",
                        "value": "OctoberPoppyNuttyDraperySabbath",
                        "reference": "op://Test Vault/Authy Backup/password",
                        "password_details": {
                            "strength": "FANTASTIC"
                        }
                    },
                    {
                        "id": "notesPlain",
                        "type": "STRING",
                        "purpose": "NOTES",
                        "label": "notesPlain",
                        "value": "Backup password to restore Authy",
                        "reference": "op://Test Vault/Authy Backup/notesPlain"
                    }
                ]
            },
        },
        {
            # Request a custom field where ID and label are different
            "vault_name": "Test Vault",
            "queries": ["Dummy Login"],
            "kwargs": {
                "field": "password1",
            },
            "expected": ["data in custom field"],
            "output": {
                "id": "awk4s2u44fhnrgppszcsvc663i",
                "title": "Dummy Login",
                "version": 4,
                "vault": {
                    "id": "stpebbaccrq72xulgouxsk4p7y",
                    "name": "Personal"
                },
                "category": "LOGIN",
                "last_edited_by": "LSGPJERUYBH7BFPHMZ2KKGL6AU",
                "created_at": "2018-04-25T21:55:19Z",
                "updated_at": "2022-09-02T17:51:21Z",
                "additional_information": "agent.smith",
                "urls": [
                    {
                        "primary": True,
                        "href": "https://acme.com"
                    }
                ],
                "sections": [
                    {
                        "id": "add more"
                    },
                    {
                        "id": "gafaeg7vnqmgrklw5r6yrufyxy",
                        "label": "COMMANDS"
                    },
                    {
                        "id": "linked items",
                        "label": "Related Items"
                    }
                ],
                "fields": [
                    {
                        "id": "username",
                        "type": "STRING",
                        "purpose": "USERNAME",
                        "label": "username",
                        "value": "agent.smith",
                        "reference": "op://Personal/Dummy Login/username"
                    },
                    {
                        "id": "password",
                        "type": "CONCEALED",
                        "purpose": "PASSWORD",
                        "label": "password",
                        "value": "FootworkDegreeReverence",
                        "entropy": 159.60836791992188,
                        "reference": "op://Personal/Dummy Login/password",
                        "password_details": {
                            "entropy": 159,
                            "generated": True,
                            "strength": "FANTASTIC"
                        }
                    },
                    {
                        "id": "notesPlain",
                        "type": "STRING",
                        "purpose": "NOTES",
                        "label": "notesPlain",
                        "reference": "op://Personal/Dummy Login/notesPlain"
                    },
                    {
                        "id": "7gyjekelk24ghgd4rvafspjbli",
                        "section": {
                            "id": "add more"
                        },
                        "type": "STRING",
                        "label": "title",
                        "value": "value of the field",
                        "reference": "op://Personal/Dummy Login/add more/title"
                    },
                    {
                        "id": "fx4wpzokrxn7tlb3uwpdjfptgm",
                        "section": {
                            "id": "gafaeg7vnqmgrklw5r6yrufyxy",
                            "label": "COMMANDS"
                        },
                        "type": "CONCEALED",
                        "label": "password1",
                        "value": "data in custom field",
                        "reference": "op://Personal/Dummy Login/COMMANDS/password1"
                    }
                ]
            }
        },
    ],
}
