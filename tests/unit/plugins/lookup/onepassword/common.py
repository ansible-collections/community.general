# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json

from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePassCLIv1,
    OnePassCLIv2,
)


def load_file(file):
    with open((os.path.join(os.path.dirname(__file__), "fixtures", file)), "r") as f:
        return json.loads(f.read())


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
            'output': load_file("v1_out_01.json"),
        },
        {
            'vault_name': 'Acme Logins',
            'queries': [
                '9876543210',
                'Mock Website',
                'acme.com'
            ],
            'expected': ['t0pS3cret', 't0pS3cret', 't0pS3cret'],
            'output': load_file("v1_out_02.json"),
        },
        {
            'vault_name': 'Acme Logins',
            'queries': [
                '864201357'
            ],
            'expected': ['vauxhall'],
            'output': load_file("v1_out_03.json"),
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
            "output": load_file("v2_out_01.json"),
        },
        {
            # Request a custom field where ID and label are different
            "vault_name": "Test Vault",
            "queries": ["Dummy Login"],
            "kwargs": {
                "field": "password1",
            },
            "expected": ["data in custom field"],
            "output": load_file("v2_out_02.json")
        },
        {
            # Request data from a custom section
            "vault_name": "Test Vault",
            "queries": ["Duplicate Sections"],
            "kwargs": {
                "field": "s2 text",
                "section": "Section 2",
            },
            "expected": ["first value"],
            "output": load_file("v2_out_03.json")
        },
    ],
}
